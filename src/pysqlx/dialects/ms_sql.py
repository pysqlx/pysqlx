"""Microsoft SQL Server dialect."""

from datetime import datetime
from typing import Any, cast

from .._compat import override
from ..exceptions import InvalidArgumentError
from ..queries import Drop, IsExists, Reflect
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
from .i_dialect import IDialect

_int_name_dict = {
    1: "tinyint",
    2: "smallint",
    4: "int",
    8: "bigint",
}


class MsSql(IDialect):
    """Dialect of Microsoft SQL Server."""

    def __init__(self) -> None:
        super().__init__(dialect_name="mssql")

    @override
    def quote_identifier(self, name: str) -> str:
        return "[" + name.replace("]", "]]") + "]"

    @override
    def get_table_qualifier(self, table: Table) -> str:
        q_ar = []

        if table.database and table.schema:
            q_ar.append(table.database.database_name)

        if table.schema:
            q_ar.append(table.schema.schema_name)

        q_ar.append(table.table_name)

        return ".".join(self.quote_identifier(x) for x in q_ar)

    @override
    def _get_datetime_string(self, val: datetime) -> str:
        return val.isoformat(timespec="milliseconds")

    @override
    def _get_binary_string(self, val: bytes) -> str:
        return "0x" + val.hex()

    @override
    def _get_identity_string(self) -> str:
        return "IDENTITY(1, 1)"

    @override
    def get_BinaryColumn_declaration(self, column: BinaryColumn) -> str:
        return self._get_declaration_string(column, type_string="varbinary(max)")

    @override
    def get_BooleanColumn_declaration(self, column: BooleanColumn) -> str:
        return self._get_declaration_string(column, type_string="bit")

    @override
    def get_CharStringColumn_declaration(self, column: CharStringColumn) -> str:
        type_string = ""

        if column.is_unicode:
            type_string += "n"

        if not column.is_fixed:
            type_string += "var"

        type_string += f"char({column.size})"

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
            column, type_string=f"float({53 if column.is_double else 24})"
        )

    @override
    def get_IntegerColumn_declaration(self, column: IntegerColumn) -> str:
        return self._get_declaration_string(column, type_string=_int_name_dict[column.n_bytes])

    @override
    def get_TextColumn_declaration(self, column: TextColumn) -> str:
        type_string = ""

        if column.is_unicode:
            type_string += "n"

        type_string += "varchar(max)"

        return self._get_declaration_string(column, type_string)

    @override
    def get_Drop_index_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        index = cast(Index, query.structure)

        name = self.quote_identifier(index.index_name)
        scope = self.get_table_qualifier(index.table)
        return f"DROP INDEX {name} ON {scope}"

    @override
    def get_IsExists_database_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        database = cast(Database, query.structure)

        return f"""if exists (
    SELECT name FROM master.sys.databases
    WHERE name={self.get_literal_string(database.database_name)})
    SELECT 1 AS result;
else
    SELECT 0 AS result;"""

    @override
    def get_IsExists_schema_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        schema = cast(Schema, query.structure)

        return f"""if exists (
    SELECT schema_name FROM information_schema.schemata
    WHERE schema_name={self.get_literal_string(schema.schema_name)})
    SELECT 1 AS result;
else
    SELECT 0 AS result;"""

    @override
    def get_IsExists_table_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        table = cast(Table, query.structure)

        return f"""if exists (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'
    AND TABLE_NAME={self.get_literal_string(table.table_name)})
    SELECT 1 AS result;
else
    SELECT 0 AS result;"""

    @override
    def get_IsExists_index_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        index = cast(Index, query.structure)

        return f"""if exists (
    SELECT 1 FROM sys.indexes WHERE name={self.get_literal_string(index.index_name)}
    AND object_id=OBJECT_ID({self.get_literal_string(self.get_table_qualifier(index.table))}))
    SELECT 1 AS result;
else
    SELECT 0 AS result;"""

    @override
    def _get_limit_strings(
        self,
        top: int | None,
        offset: int | None,
        is_ordered: bool,
    ) -> tuple[str, str]:
        if offset is None:
            return ("" if top is None else f"TOP ({top})"), ""

        if not is_ordered:
            raise InvalidArgumentError("SQL Server needs ascend_by or descend_by to use offset")

        suffix = f"OFFSET {offset} ROWS"

        if top is not None:
            suffix += f" FETCH NEXT {top} ROWS ONLY"

        return "", suffix

    @override
    def get_Reflect_table_string(self, query: Reflect, parameters: list[Any] | None = None) -> str:
        table = query.structure

        return self._get_information_schema_string(
            table,
            schema_string=(
                self.get_literal_string(table.schema.schema_name)
                if table.schema
                else "SCHEMA_NAME()"
            ),
            identity_string=(
                "COLUMNPROPERTY(OBJECT_ID(QUOTENAME(c.table_schema) + '.' +"
                " QUOTENAME(c.table_name)), c.column_name, 'IsIdentity')"
            ),
        )

    @override
    def _get_reflected_type(
        self,
        data_type: str,
        size: int | None,
        precision: int | None,
        column_type: str | None,
    ) -> dict[str, Any]:
        if data_type in ("varchar", "nvarchar", "char", "nchar"):
            is_unicode = data_type.startswith("n")

            # A size of -1 stands for "max".
            if size is None or size < 0:
                return {"kind": "text", "is_unicode": is_unicode}

            return {
                "kind": "char",
                "is_unicode": is_unicode,
                "is_fixed": not data_type.endswith("varchar"),
                "size": size,
            }

        if data_type in ("text", "ntext"):
            return {"kind": "text", "is_unicode": data_type == "ntext"}

        if data_type in ("tinyint", "smallint", "int", "bigint"):
            return {
                "kind": "integer",
                "n_bytes": {"tinyint": 1, "smallint": 2, "int": 4, "bigint": 8}[data_type],
            }

        if data_type in ("float", "real"):
            return {"kind": "float", "is_double": data_type == "float" and (precision or 53) > 24}

        if data_type in ("datetime", "datetime2", "smalldatetime"):
            return {"kind": "datetime"}

        if data_type == "date":
            return {"kind": "date"}

        if data_type == "bit":
            return {"kind": "boolean"}

        if data_type in ("decimal", "numeric"):
            return {"kind": "decimal", "precision": precision}

        if data_type in ("varbinary", "binary", "image"):
            return {"kind": "binary"}

        return super()._get_reflected_type(data_type, size, precision, column_type)
