"""SQLite dialect."""

from collections.abc import Sequence
from typing import Any, cast

from .._compat import override
from ..exceptions import UnsupportedOperationError
from ..queries import Create, Drop, IsExists, Reflect, Truncate
from ..structures import (
    BinaryColumn,
    BooleanColumn,
    CharStringColumn,
    Column,
    DateColumn,
    DatetimeColumn,
    DecimalColumn,
    FloatColumn,
    Index,
    IntegerColumn,
    Table,
    TextColumn,
)
from .i_dialect import IDialect


class Sqlite(IDialect):
    """Dialect of SQLite.

    SQLite has neither databases nor schemas to create, so the queries which
    act on them raise ``UnsupportedOperationError``.
    """

    def __init__(self) -> None:
        super().__init__(dialect_name="sqlite")

    @override
    def quote_identifier(self, name: str) -> str:
        return "[" + name.replace("]", "]]") + "]"

    @override
    def get_table_qualifier(self, table: Table) -> str:
        return self.quote_identifier(table.table_name)

    @override
    def _get_declaration_string(self, column: Column, type_string: str) -> str:
        # An identity column must be declared as the primary key of its own.
        is_inline_key = (
            column.is_primary_key and len(super()._get_primary_key_columns(column.table)) == 1
        )

        return " ".join(
            x
            for x in (
                self.quote_identifier(column.column_name),
                type_string,
                "NOT NULL" if column.is_prevent_null else "",
                "PRIMARY KEY" if is_inline_key else "",
                "AUTOINCREMENT" if column.is_identity else "",
                f"DEFAULT {column.default_value}" if column.default_value is not None else "",
            )
            if x != ""
        )

    @override
    def _get_primary_key_columns(self, table: Table) -> list[Column]:
        table_keys = super()._get_primary_key_columns(table)

        # A single key column is declared with the column.
        return table_keys if len(table_keys) > 1 else []

    @override
    def get_BinaryColumn_declaration(self, column: BinaryColumn) -> str:
        return self._get_declaration_string(column, type_string="blob")

    @override
    def get_BooleanColumn_declaration(self, column: BooleanColumn) -> str:
        return self._get_declaration_string(column, type_string="boolean")

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
        return self._get_declaration_string(column, type_string="real")

    @override
    def get_IntegerColumn_declaration(self, column: IntegerColumn) -> str:
        return self._get_declaration_string(column, type_string="integer")

    @override
    def get_TextColumn_declaration(self, column: TextColumn) -> str:
        return self._get_declaration_string(column, type_string="text")

    @override
    def get_Create_database_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        raise UnsupportedOperationError("database creation is not supported in SQLite")

    @override
    def get_Create_schema_string(self, query: Create, parameters: list[Any] | None = None) -> str:
        raise UnsupportedOperationError("schema creation is not supported in SQLite")

    @override
    def get_Drop_database_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        raise UnsupportedOperationError("database dropping is not supported in SQLite")

    @override
    def get_Drop_schema_string(self, query: Drop, parameters: list[Any] | None = None) -> str:
        raise UnsupportedOperationError("schema dropping is not supported in SQLite")

    @override
    def get_IsExists_database_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        raise UnsupportedOperationError("database checks are not supported in SQLite")

    @override
    def get_IsExists_schema_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        raise UnsupportedOperationError("schema checks are not supported in SQLite")

    @override
    def get_IsExists_table_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        table = cast(Table, query.structure)

        name = self.get_literal_string(table.table_name)
        return f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name={name}"

    @override
    def get_IsExists_index_string(
        self, query: IsExists, parameters: list[Any] | None = None
    ) -> str:
        index = cast(Index, query.structure)

        name = self.get_literal_string(index.index_name)
        return f"SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name={name}"

    @override
    def _get_no_limit_string(self) -> str:
        return "LIMIT -1"

    @override
    def get_Truncate_table_string(
        self, query: Truncate, parameters: list[Any] | None = None
    ) -> str:
        return f"DELETE FROM {self.get_table_qualifier(query.structure)}"

    @override
    def get_Reflect_table_string(self, query: Reflect, parameters: list[Any] | None = None) -> str:
        name = self.get_literal_string(query.structure.table_name)

        return f"""SELECT p.name, p.type, p."notnull", p.dflt_value, p.pk,
(SELECT sql FROM sqlite_master WHERE type='table' AND name={name})
FROM pragma_table_info({name}) p ORDER BY p.cid"""

    @override
    def get_reflected_table(self, query: Reflect, rows: Sequence[Sequence[Any]]) -> Table:
        table = self._get_empty_table(query, rows)

        for column_name, type_string, is_prevent_null, default_value, key_index, sql in rows:
            type_name, numbers = self._parse_type(type_string)
            is_primary_key = bool(key_index)

            arguments: dict[str, Any]

            if type_name in ("nvarchar", "varchar", "nchar", "char"):
                arguments = {
                    "kind": "char",
                    "is_unicode": type_name.startswith("n"),
                    "is_fixed": not type_name.endswith("varchar"),
                    "size": numbers[0] if numbers else None,
                }
            elif type_name in ("text", "ntext", "clob"):
                arguments = {"kind": "text"}
            elif type_name in ("integer", "int", "tinyint", "smallint", "mediumint", "bigint"):
                arguments = {"kind": "integer", "n_bytes": 8}
            elif type_name in ("real", "double", "double precision", "float"):
                arguments = {"kind": "float"}
            elif type_name in ("datetime", "timestamp"):
                arguments = {"kind": "datetime"}
            elif type_name == "date":
                arguments = {"kind": "date"}
            elif type_name in ("boolean", "bool"):
                arguments = {"kind": "boolean"}
            elif type_name in ("decimal", "numeric"):
                arguments = {
                    "kind": "decimal",
                    "precision": numbers[0] if numbers else None,
                    "scale": numbers[1] if len(numbers) > 1 else None,
                }
            elif type_name == "blob":
                arguments = {"kind": "binary"}
            else:
                raise UnsupportedOperationError(f'unknown column type "{type_string}"')

            self._append_reflected_column(
                table,
                column_name=column_name,
                default_value=default_value,
                is_identity=(
                    is_primary_key
                    and arguments["kind"] == "integer"
                    and "AUTOINCREMENT" in str(sql).upper()
                ),
                is_primary_key=is_primary_key,
                is_prevent_null=bool(is_prevent_null),
                **arguments,
            )

        return table
