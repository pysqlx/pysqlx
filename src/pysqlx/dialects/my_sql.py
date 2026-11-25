"""MySQL dialect."""

from typing import Any, cast

from .._compat import override
from ..exceptions import UnsupportedOperationError
from ..queries import Create, Drop, Exists, Reflect
from ..structures import (
    BinaryColumn,
    BooleanColumn,
    CharStringColumn,
    Database,
    DateColumn,
    DatetimeColumn,
    DecimalColumn,
    FloatColumn,
    Index,
    IntegerColumn,
    Schema,
    Table,
    TextColumn,
)
from .dialect import Dialect

_int_name_dict = {
    1: "tinyint",
    2: "smallint",
    4: "int",
    8: "bigint",
}


class MySql(Dialect):
    """Dialect of MySQL and MariaDB.

    MySQL has no schemas inside a database: a schema is another name for a
    database. A table is qualified with its database, or with its schema when
    it has no database.
    """

    def __init__(self) -> None:
        super().__init__(dialect_name="mysql")

    @property
    @override
    def placeholder(self) -> str:
        return "%s"

    @override
    def quote_identifier(self, name: str) -> str:
        return "`" + name.replace("`", "``") + "`"

    def _get_database_name(self, table: Table) -> str | None:
        if table.database:
            return table.database.database_name

        if table.schema:
            return table.schema.schema_name

        return None

    @override
    def get_table_qualifier(self, table: Table) -> str:
        q_ar = []

        database_name = self._get_database_name(table)

        if database_name:
            q_ar.append(database_name)

        q_ar.append(table.table_name)

        return ".".join(self.quote_identifier(x) for x in q_ar)

    @override
    def get_literal_string(self, val: object) -> str:
        if isinstance(val, str):
            # MySQL also treats the backslash as an escape character.
            return "'" + val.replace("\\", "\\\\").replace("'", "''") + "'"

        return super().get_literal_string(val)

    @override
    def _get_identity_string(self) -> str:
        return "AUTO_INCREMENT"

    @override
    def get_BinaryColumn_declaration(self, column: BinaryColumn) -> str:
        return self._get_declaration_string(column, type_string="longblob")

    @override
    def get_BooleanColumn_declaration(self, column: BooleanColumn) -> str:
        return self._get_declaration_string(column, type_string="boolean")

    @override
    def get_CharStringColumn_declaration(self, column: CharStringColumn) -> str:
        type_string = f"char({column.size})" if column.is_fixed else f"varchar({column.size})"

        return self._get_declaration_string(column, type_string)

    @override
    def get_DateColumn_declaration(self, column: DateColumn) -> str:
        return self._get_declaration_string(column, type_string="date")

    @override
    def get_DatetimeColumn_declaration(self, column: DatetimeColumn) -> str:
        return self._get_declaration_string(column, type_string="datetime")

    @override
    def get_DecimalColumn_declaration(self, column: DecimalColumn) -> str:
        return self._get_declaration_string(
            column, type_string=f"decimal({column.precision}, {column.scale})"
        )

    @override
    def get_FloatColumn_declaration(self, column: FloatColumn) -> str:
        return self._get_declaration_string(
            column, type_string="double" if column.is_double else "float"
        )

    @override
    def get_IntegerColumn_declaration(self, column: IntegerColumn) -> str:
        return self._get_declaration_string(column, type_string=_int_name_dict[column.n_bytes])

    @override
    def get_TextColumn_declaration(self, column: TextColumn) -> str:
        return self._get_declaration_string(column, type_string="longtext")

    @override
    def get_Create_schema_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        schema = cast(Schema, query.structure)

        if schema.owner_name:
            raise UnsupportedOperationError("schema owners are not supported in MySQL")

        return f"CREATE SCHEMA {self.quote_identifier(schema.schema_name)}"

    @override
    def get_Drop_index_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        index = cast(Index, query.structure)

        name = self.quote_identifier(index.index_name)
        scope = self.get_table_qualifier(index.table)
        return f"DROP INDEX {name} ON {scope}"

    @override
    def get_Exists_database_string(self, query: Exists, parameters: list[Any] | None = None) -> str:
        database = cast(Database, query.structure)

        name = self.get_literal_string(database.database_name)
        return f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name={name}"

    @override
    def get_Exists_schema_string(self, query: Exists, parameters: list[Any] | None = None) -> str:
        schema = cast(Schema, query.structure)

        name = self.get_literal_string(schema.schema_name)
        return f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name={name}"

    @override
    def get_Exists_table_string(self, query: Exists, parameters: list[Any] | None = None) -> str:
        table = cast(Table, query.structure)

        name = self.get_literal_string(table.table_name)
        scope = self._get_database_filter(table)
        return f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name={name}{scope}"

    @override
    def get_Exists_index_string(self, query: Exists, parameters: list[Any] | None = None) -> str:
        index = cast(Index, query.structure)

        name = self.get_literal_string(index.index_name)
        scope = self.get_literal_string(index.table.table_name)
        scope_filter = self._get_database_filter(index.table)
        return (
            "SELECT COUNT(DISTINCT index_name) FROM information_schema.statistics"
            f" WHERE index_name={name} AND table_name={scope}{scope_filter}"
        )

    def _get_database_filter(self, table: Table) -> str:
        database_name = self._get_database_name(table)

        if database_name:
            return f" AND table_schema={self.get_literal_string(database_name)}"

        return " AND table_schema=DATABASE()"

    @override
    def _get_no_limit_string(self) -> str:
        return "LIMIT 18446744073709551615"

    @override
    def get_Reflect_table_string(self, query: Reflect, parameters: list[Any] | None = None) -> str:
        table = query.table
        database_name = self._get_database_name(table)

        return self._get_information_schema_string(
            table,
            schema_string=(
                self.get_literal_string(database_name) if database_name else "DATABASE()"
            ),
            identity_string="CASE WHEN c.extra LIKE '%auto_increment%' THEN 1 ELSE 0 END",
            type_string="c.column_type",
        )

    @override
    def _get_reflected_type(
        self,
        data_type: str,
        size: int | None,
        precision: int | None,
        column_type: str | None,
    ) -> dict[str, Any]:
        if data_type in ("varchar", "char"):
            return {"kind": "char", "is_fixed": data_type == "char", "size": size}

        if data_type in ("tinytext", "text", "mediumtext", "longtext"):
            return {"kind": "text"}

        # MySQL stores a boolean as a tinyint which shows one digit.
        if data_type == "tinyint" and column_type == "tinyint(1)":
            return {"kind": "boolean"}

        if data_type in ("tinyint", "smallint", "mediumint", "int", "bigint"):
            sizes = {"tinyint": 1, "smallint": 2, "mediumint": 4, "int": 4, "bigint": 8}
            return {"kind": "integer", "n_bytes": sizes[data_type]}

        if data_type in ("double", "float"):
            return {"kind": "float", "is_double": data_type == "double"}

        if data_type in ("datetime", "timestamp"):
            return {"kind": "datetime"}

        if data_type == "date":
            return {"kind": "date"}

        if data_type == "decimal":
            return {"kind": "decimal", "precision": precision}

        if data_type in ("tinyblob", "blob", "mediumblob", "longblob", "binary", "varbinary"):
            return {"kind": "binary"}

        return super()._get_reflected_type(data_type, size, precision, column_type)

    @override
    def get_foreign_keys_string(self, table: Table) -> str:
        name = self.get_literal_string(table.table_name)
        database_name = self._get_database_name(table)
        scope = self.get_literal_string(database_name) if database_name else "DATABASE()"

        return f"""SELECT constraint_name, column_name,
CASE WHEN referenced_table_schema = table_schema THEN NULL ELSE referenced_table_schema END,
referenced_table_name, referenced_column_name
FROM information_schema.key_column_usage
WHERE table_name = {name} AND table_schema = {scope}
AND referenced_table_name IS NOT NULL
ORDER BY constraint_name, ordinal_position"""

    @override
    def get_reference_table(
        self,
        table: Table,
        schema_name: str | None,
        table_name: str,
    ) -> Table:
        # A schema of MySQL is a database.
        return Table(
            table_name=table_name,
            database=Database(database_name=schema_name) if schema_name else table.database,
            schema=table.schema,
        )
