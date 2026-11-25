"""SQLite dialect."""

from datetime import datetime
from typing import cast, override

from ..queries import (
    Create,
    Delete,
    Drop,
    GetLength,
    Insert,
    IsEmpty,
    IsExists,
    Select,
    SelectDistinct,
    Truncate,
    Union,
    Update,
)
from ..structures import (
    CharStringColumn,
    Clause,
    Column,
    DatetimeColumn,
    FloatColumn,
    IntegerColumn,
    Table,
    TextColumn,
)
from ..structures.columntypes.logicalclause import (
    And,
    Between,
    Equal,
    GreaterThan,
    GreaterThanEqual,
    InList,
    IsNotNull,
    IsNull,
    LessThan,
    LessThanEqual,
    Like,
    NotBetween,
    NotEqual,
    NotInList,
    NotLike,
    Or,
)
from .i_dialect import IDialect


class Sqlite(IDialect):
    """Dialect of SQLite.

    SQLite has neither databases nor schemas to create, so the queries which
    act on them raise ``RuntimeError``.
    """

    def __init__(self) -> None:
        super().__init__(dialect_name="sqlite")

    @override
    def get_table_qualifier(self, table: Table) -> str:
        return table.table_name

    @override
    def get_column_qualifier(self, column: Column) -> str:
        return "[" + column.column_name + "]"

    def _get_common_declaration_string(self, column: Column, type_string: str) -> str:
        return " ".join(
            tuple(
                x
                for x in (
                    self.get_column_qualifier(column),
                    type_string,
                    "NOT NULL" if column.is_prevent_null else "",
                    "PRIMARY KEY" if column.is_primary_key else "",
                    "AUTOINCREMENT" if column.is_identity else "",
                    f"DEFAULT {column.default_value}" if column.default_value else "",
                )
                if x != ""
            )
        )

    @override
    def get_CharStringColumn_declaration(self, column: CharStringColumn) -> str:
        type_string = ""

        if column.is_unicode:
            type_string += "n"

        if not column.is_fixed:
            type_string += "var"

        type_string += f"char({column.size})"

        return self._get_common_declaration_string(column, type_string)

    @override
    def get_DatetimeColumn_declaration(self, column: DatetimeColumn) -> str:
        return self._get_common_declaration_string(column, type_string="datetime")

    @override
    def get_FloatColumn_declaration(self, column: FloatColumn) -> str:
        return self._get_common_declaration_string(column, type_string="real")

    @override
    def get_IntegerColumn_declaration(self, column: IntegerColumn) -> str:
        return self._get_common_declaration_string(column, type_string="integer")

    @override
    def get_TextColumn_declaration(self, column: TextColumn) -> str:
        return self._get_common_declaration_string(column, type_string="text")

    def _convert_value(self, val: object) -> str:
        if isinstance(val, str):
            return "'" + val + "'"

        if isinstance(val, datetime):
            return self._convert_value(val.isoformat(sep=" ", timespec="seconds"))

        if isinstance(val, (int, float)):
            return str(val)

        if isinstance(val, Clause):
            return "".join(
                [
                    "(",
                    self.get_clause_string(val),
                    ")",
                ]
            )

        if isinstance(val, Column):
            return self.get_column_qualifier(val)

        raise RuntimeError(f'unknown value "{val}" of type "{type(val).__name__}"')

    @override
    def get_And_string(self, clause: And) -> str:
        return " ".join(
            (
                self._convert_value(clause.clause0),
                "AND",
                self._convert_value(clause.clause1),
            )
        )

    @override
    def get_Between_string(self, clause: Between) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "BETWEEN",
                self._convert_value(clause.value0),
                "AND",
                self._convert_value(clause.value1),
            )
        )

    @override
    def get_Equal_string(self, clause: Equal) -> str:
        return " = ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_GreaterThan_string(self, clause: GreaterThan) -> str:
        return " > ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_GreaterThanEqual_string(self, clause: GreaterThanEqual) -> str:
        return " >= ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_InList_string(self, clause: InList) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "IN (",
                ", ".join(tuple(self._convert_value(val) for val in clause.val_list)),
                ")",
            )
        )

    @override
    def get_IsNotNull_string(self, clause: IsNotNull) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "IS NOT NULL",
            )
        )

    @override
    def get_IsNull_string(self, clause: IsNull) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "IS NULL",
            )
        )

    @override
    def get_LessThan_string(self, clause: LessThan) -> str:
        return " < ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_LessThanEqual_string(self, clause: LessThanEqual) -> str:
        return " <= ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_Like_string(self, clause: Like) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "LIKE",
                self._convert_value(clause.value),
            )
        )

    @override
    def get_NotBetween_string(self, clause: NotBetween) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "NOT BETWEEN",
                self._convert_value(clause.value0),
                "AND",
                self._convert_value(clause.value1),
            )
        )

    @override
    def get_NotEqual_string(self, clause: NotEqual) -> str:
        return " != ".join(
            (
                self._convert_value(clause.lhs),
                self._convert_value(clause.rhs),
            )
        )

    @override
    def get_NotInList_string(self, clause: NotInList) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "NOT IN (",
                ", ".join(tuple(self._convert_value(val) for val in clause.val_list)),
                ")",
            )
        )

    @override
    def get_NotLike_string(self, clause: NotLike) -> str:
        return " ".join(
            (
                self._convert_value(clause.column),
                "NOT LIKE",
                self._convert_value(clause.value),
            )
        )

    @override
    def get_Or_string(self, clause: Or) -> str:
        return " ".join(
            (
                self._convert_value(clause.clause0),
                "OR",
                self._convert_value(clause.clause1),
            )
        )

    @override
    def get_Create_database_string(self, query: Create) -> str:
        raise RuntimeError("database creation is not supported in SQLite")

    @override
    def get_Create_schema_string(self, query: Create) -> str:
        raise RuntimeError("schema creation is not supported in SQLite")

    @override
    def get_Create_table_string(self, query: Create) -> str:
        table = cast(Table, query.structure)

        if not table.columns:
            raise RuntimeError("table has no columns")

        table_cols = [self.get_column_declaration(col) for col in table.columns]

        return "CREATE TABLE {} (\n{}\n)".format(
            self.get_table_qualifier(table),
            ",\n".join(table_cols),
        )

    @override
    def get_Delete_table_string(self, query: Delete) -> str:
        table = query.structure
        condition = query.condition

        return " ".join(
            (
                "DELETE FROM",
                self.get_table_qualifier(table),
                "WHERE",
                self.get_clause_string(condition),
            )
        )

    @override
    def get_Drop_database_string(self, query: Drop) -> str:
        raise RuntimeError("database dropping is not supported in SQLite")

    @override
    def get_Drop_schema_string(self, query: Drop) -> str:
        raise RuntimeError("schema dropping is not supported in SQLite")

    @override
    def get_Drop_table_string(self, query: Drop) -> str:
        table = cast(Table, query.structure)

        return f"DROP TABLE {self.get_table_qualifier(table)}"

    @override
    def get_GetLength_table_string(self, query: GetLength) -> str:
        table = query.structure

        return f"SELECT COUNT(*) FROM {self.get_table_qualifier(table)}"

    @override
    def get_Insert_table_string(self, query: Insert) -> str:
        table = query.structure
        columns = query.columns

        col_names = tuple(self.get_column_qualifier(col) for col in columns)

        return "INSERT INTO {} ({}) VALUES ({})".format(
            self.get_table_qualifier(table),
            ",\n".join(col_names),
            ", ".join(["?"] * len(col_names)),
        )

    @override
    def get_IsEmpty_table_string(self, query: IsEmpty) -> str:
        table = query.structure

        return f"SELECT COUNT(*) FROM {self.get_table_qualifier(table)}"

    @override
    def get_IsExists_database_string(self, query: IsExists) -> str:
        raise RuntimeError("database checks is not supported in SQLite")

    @override
    def get_IsExists_schema_string(self, query: IsExists) -> str:
        raise RuntimeError("schema checks is not supported in SQLite")

    @override
    def get_IsExists_table_string(self, query: IsExists) -> str:
        table = cast(Table, query.structure)

        return f"""
SELECT name FROM sqlite_master WHERE type='table' AND name='{table.table_name}'
"""

    @override
    def get_Select_table_string(self, query: Select) -> str:
        table = query.structure
        top = query.top
        columns = query.columns
        ascend_by = query.ascend_by
        descend_by = query.descend_by
        condition = query.condition

        sql_ar = [
            "SELECT",
            ",\n".join(tuple(self.get_column_qualifier(col) for col in columns)),
            "FROM",
            self.get_table_qualifier(table),
        ]

        if condition:
            sql_ar += [
                "WHERE",
                self.get_clause_string(condition),
            ]

        if any((ascend_by, descend_by)):
            order_ar = []

            if ascend_by:
                order_ar += [self.get_column_qualifier(col) + " ASC" for col in ascend_by]

            if descend_by:
                order_ar += [self.get_column_qualifier(col) + " DESC" for col in descend_by]

            sql_ar += [
                "ORDER BY",
                ",\n".join(order_ar),
            ]

        if top:
            sql_ar.append(f"LIMIT ({top})")

        return " ".join(tuple(x for x in sql_ar if x != ""))

    @override
    def get_SelectDistinct_table_string(self, query: SelectDistinct) -> str:
        table = query.structure
        columns = query.columns
        ascend_by = query.ascend_by
        descend_by = query.descend_by
        condition = query.condition

        sql_ar = [
            "SELECT DISTINCT",
            ", ".join(tuple(self.get_column_qualifier(col) for col in columns)),
            "FROM",
            self.get_table_qualifier(table),
        ]

        if condition:
            sql_ar += [
                "WHERE",
                self.get_clause_string(condition),
            ]

        if any((ascend_by, descend_by)):
            order_ar = []

            if ascend_by:
                order_ar += [self.get_column_qualifier(col) + " ASC" for col in ascend_by]

            if descend_by:
                order_ar += [self.get_column_qualifier(col) + " DESC" for col in descend_by]

            sql_ar += [
                "ORDER BY",
                ", ".join(order_ar),
            ]

        return " ".join(sql_ar)

    @override
    def get_Truncate_table_string(self, query: Truncate) -> str:
        table = query.structure

        return f"DELETE FROM {self.get_table_qualifier(table)}"

    @override
    def get_Union_table_string(self, query: Union) -> str:
        table_list = query.structure_list
        query_list = query.query_list
        columns_list = query.columns_list
        is_all = query.is_all
        ascend_by = query.ascend_by
        descend_by = query.descend_by
        condition = query.condition

        union_str = ("\nUNION{}\n".format(" ALL" if is_all else "")).join(
            tuple(
                " ".join(
                    [
                        "SELECT",
                        ",\n".join(
                            tuple(self.get_column_qualifier(col) for col in columns_list[i])
                        ),
                        "FROM",
                        "(\n" + self.get_query_string(query_list[i]) + "\n)",
                        table_list[i].table_name,
                    ]
                )
                for i in range(len(table_list))
            )
        ) + "\n"

        if condition:
            union_str += "WHERE\n" + self.get_clause_string(condition)

        if any((ascend_by, descend_by)):
            order_ar = []

            if ascend_by:
                order_ar += [self.get_column_qualifier(col) + " ASC" for col in ascend_by]

            if descend_by:
                order_ar += [self.get_column_qualifier(col) + " DESC" for col in descend_by]

            union_str += "ORDER BY\n" + ",\n".join(order_ar)

        return union_str

    @override
    def get_Update_table_string(self, query: Update) -> str:
        table = query.structure
        columns = query.columns
        condition = query.condition

        col_names = tuple(self.get_column_qualifier(col) for col in columns)

        return "UPDATE {}\nSET {}\nWHERE {}".format(
            self.get_table_qualifier(table),
            ", ".join(tuple(col + "=?" for col in col_names)),
            self.get_clause_string(condition),
        )
