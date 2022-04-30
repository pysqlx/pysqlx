
from datetime import datetime


def test_columns(local_table):
    table = local_table

    assert len(table.columns) == 5

    for col in table.columns:
        assert col.structure_name == 'column'
        assert col.table.table_name == table.table_name

    char_string_column, datetime_column, float_column, integer_column, \
        text_column = table.columns

    assert char_string_column.column_name == 'char_string_column'
    assert datetime_column.column_name == 'datetime_column'
    assert float_column.column_name == 'float_column'
    assert integer_column.column_name == 'integer_column'
    assert text_column.column_name == 'text_column'

    assert not char_string_column.is_unicode
    assert not char_string_column.is_fixed
    assert char_string_column.size == 255
    assert not char_string_column.is_primary_key
    assert not char_string_column.is_prevent_null

    assert not datetime_column.is_primary_key
    assert not datetime_column.is_prevent_null

    assert float_column.is_double
    assert not float_column.is_primary_key
    assert not float_column.is_prevent_null

    assert integer_column.n_bytes == 4
    assert not integer_column.is_identity
    assert not integer_column.is_primary_key
    assert not integer_column.is_prevent_null

    assert not text_column.is_unicode
    assert not text_column.is_primary_key
    assert not text_column.is_prevent_null


def _check_clause(sqlite_dialect, clause, output_str):
    return sqlite_dialect.get_clause_string(clause) == output_str


def test_columns_simple_expressions(local_table, sqlite_dialect):
    table = local_table

    assert len(table.columns) == 5

    char_string_column, datetime_column, float_column, integer_column, \
        text_column = table.columns

    assert _check_clause(
        sqlite_dialect,
        (char_string_column == 'hi'),
        "[char_string_column] = 'hi'"
    )

    assert _check_clause(
        sqlite_dialect,
        (char_string_column != 'hi'),
        "[char_string_column] != 'hi'"
    )

    assert _check_clause(
        sqlite_dialect, (datetime_column > datetime(1998, 1, 1)),
        "[datetime_column] > '1998-01-01 00:00:00'"
    )

    assert _check_clause(
        sqlite_dialect,
        (datetime_column >= datetime(1998, 1, 1)),
        "[datetime_column] >= '1998-01-01 00:00:00'"
    )

    assert _check_clause(
        sqlite_dialect,
        (float_column < 10),
        "[float_column] < 10")

    assert _check_clause(
        sqlite_dialect,
        (float_column <= 10),
        "[float_column] <= 10")

    assert _check_clause(
        sqlite_dialect, (integer_column.is_between(
            9, 14)), "[integer_column] BETWEEN 9 AND 14")

    assert _check_clause(
        sqlite_dialect, (integer_column.is_in_list(
            (9, 14))), "[integer_column] IN ( 9, 14 )")

    assert _check_clause(
        sqlite_dialect,
        (text_column.is_null()),
        "[text_column] IS NULL")

    assert _check_clause(
        sqlite_dialect,
        (text_column.is_not_null()),
        "[text_column] IS NOT NULL")

    assert _check_clause(
        sqlite_dialect,
        (text_column.is_like('test%')),
        "[text_column] LIKE 'test%'")


def test_columns_simple_not_expressions(local_table, sqlite_dialect):
    table = local_table

    assert len(table.columns) == 5

    char_string_column, datetime_column, float_column, integer_column, \
        text_column = table.columns

    assert _check_clause(sqlite_dialect,
                         (~(char_string_column == 'hi')),
                         "[char_string_column] != 'hi'")

    assert _check_clause(sqlite_dialect,
                         (~(char_string_column != 'hi')),
                         "[char_string_column] = 'hi'")

    assert _check_clause(
        sqlite_dialect, (~(
            datetime_column > datetime(
                1998, 1, 1))), "[datetime_column] <= '1998-01-01 00:00:00'")

    assert _check_clause(
        sqlite_dialect, (~(
            datetime_column >= datetime(
                1998, 1, 1))), "[datetime_column] < '1998-01-01 00:00:00'")

    assert _check_clause(sqlite_dialect,
                         (~(float_column < 10)),
                         "[float_column] >= 10")

    assert _check_clause(sqlite_dialect,
                         (~(float_column <= 10)),
                         "[float_column] > 10")

    assert _check_clause(
        sqlite_dialect, (~(
            integer_column.is_between(
                9, 14))), "[integer_column] NOT BETWEEN 9 AND 14")

    assert _check_clause(
        sqlite_dialect, (~(
            integer_column.is_in_list(
                (9, 14)))), "[integer_column] NOT IN ( 9, 14 )")

    assert _check_clause(sqlite_dialect,
                         (~(text_column.is_null())),
                         "[text_column] IS NOT NULL")

    assert _check_clause(sqlite_dialect,
                         (~(text_column.is_not_null())),
                         "[text_column] IS NULL")

    assert _check_clause(sqlite_dialect,
                         (~(text_column.is_like('test%'))),
                         "[text_column] NOT LIKE 'test%'")


def test_columns_compound_expressions(local_table, sqlite_dialect):
    table = local_table

    assert len(table.columns) == 5

    char_string_column, datetime_column, float_column, _, _ = \
        table.columns

    assert _check_clause(sqlite_dialect, (
        (char_string_column == 'hi') &
        (datetime_column > datetime(1998, 1, 1))
    ),
        "([char_string_column] = 'hi') AND ([datetime_column] > '1998-01-01 00:00:00')")

    assert _check_clause(
        sqlite_dialect,
        ((datetime_column >= datetime(
            1998,
            1,
            1)) | (
            float_column <= 10)),
        "([datetime_column] >= '1998-01-01 00:00:00') OR ([float_column] <= 10)")

    assert _check_clause(
        sqlite_dialect,
        (((char_string_column == 'hi') & (
            datetime_column > datetime(
                1998,
                1,
                1))) | (
            (datetime_column >= datetime(
                1998,
                1,
                1)) | (
                float_column <= 10))),
        "(([char_string_column] = 'hi') AND ([datetime_column] > '1998-01-01 00:00:00')) OR (([datetime_column] >= '1998-01-01 00:00:00') OR ([float_column] <= 10))")


def test_columns_compound_not_expressions(local_table, sqlite_dialect):
    table = local_table

    assert len(table.columns) == 5

    char_string_column, datetime_column, float_column, _, _ = \
        table.columns

    assert _check_clause(sqlite_dialect, (
        ~(
            (char_string_column == 'hi') &
            (datetime_column > datetime(1998, 1, 1))
        )
    ),
        "([char_string_column] != 'hi') OR ([datetime_column] <= '1998-01-01 00:00:00')")

    assert _check_clause(sqlite_dialect, (~((datetime_column >= datetime(1998, 1, 1)) | (
        float_column <= 10))), "([datetime_column] < '1998-01-01 00:00:00') AND ([float_column] > 10)")

    assert _check_clause(sqlite_dialect, (~(((char_string_column == 'hi') & (datetime_column > datetime(1998, 1, 1))) | ((datetime_column >= datetime(1998, 1, 1)) | (
        float_column <= 10)))), "(([char_string_column] != 'hi') OR ([datetime_column] <= '1998-01-01 00:00:00')) AND (([datetime_column] < '1998-01-01 00:00:00') AND ([float_column] > 10))")
