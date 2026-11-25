"""Generate the figures shown in the documentation.

Every figure is written twice to ``docs/_static``, for the light and for the
dark theme of the documentation. Run it with ``make docs-images``.
"""

from dataclasses import dataclass
from html import escape
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / "_static"

SANS = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


@dataclass(frozen=True)
class Theme:
    """Colors of a figure for one theme of the documentation."""

    name: str
    text: str
    muted: str
    line: str
    box: str
    box_border: str
    accent: str
    accent_box: str
    code_box: str
    good: str
    good_box: str
    bad: str
    bad_box: str


THEMES = (
    Theme(
        name="light",
        text="#1f2937",
        muted="#6b7280",
        line="#9ca3af",
        box="#f8fafc",
        box_border="#cbd5e1",
        accent="#4f46e5",
        accent_box="#eef2ff",
        code_box="#f1f5f9",
        good="#047857",
        good_box="#ecfdf5",
        bad="#b91c1c",
        bad_box="#fef2f2",
    ),
    Theme(
        name="dark",
        text="#e5e7eb",
        muted="#9ca3af",
        line="#6b7280",
        box="#1f2430",
        box_border="#3b4252",
        accent="#a5b4fc",
        accent_box="#25264a",
        code_box="#161a22",
        good="#34d399",
        good_box="#10291f",
        bad="#f87171",
        bad_box="#2d1616",
    ),
)


class Figure:
    """Drawing which is written as an SVG file.

    :param width: the width of the drawing
    :param height: the height of the drawing
    :param theme: the colors to draw with
    :param title: the description of the figure for screen readers
    """

    def __init__(self, width: int, height: int, theme: Theme, title: str) -> None:
        self.width = width
        self.height = height
        self.theme = theme
        self.title = title
        self.parts: list[str] = []

    def box(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str | None = None,
        border: str | None = None,
        radius: float = 8,
        dashed: bool = False,
    ) -> None:
        """Draw a rounded rectangle."""
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
            f'fill="{fill or self.theme.box}" stroke="{border or self.theme.box_border}" '
            f'stroke-width="1.5"{dash}/>'
        )

    def text(
        self,
        x: float,
        y: float,
        content: str,
        size: int = 14,
        color: str | None = None,
        anchor: str = "middle",
        bold: bool = False,
        mono: bool = False,
    ) -> None:
        """Draw one line of text, whose baseline is at ``y``."""
        weight = ' font-weight="600"' if bold else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{MONO if mono else SANS}" font-size="{size}" '
            f'fill="{color or self.theme.text}" text-anchor="{anchor}"{weight} '
            f'xml:space="preserve">{escape(content)}</text>'
        )

    def arrow(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str | None = None,
        dashed: bool = False,
    ) -> None:
        """Draw a straight arrow."""
        color = color or self.theme.line
        marker = f"arrow-{color.lstrip('#')}"
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(
            f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{color}"/></marker></defs>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.8" '
            f'marker-end="url(#{marker})"{dash}/>'
        )

    def raw(self, svg: str) -> None:
        """Add SVG elements as they are."""
        self.parts.append(svg)

    def save(self, name: str) -> Path:
        """Write the figure to the static files of the documentation."""
        path = STATIC_DIR / f"{name}-{self.theme.name}.svg"
        path.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img">\n'
            f"<title>{escape(self.title)}</title>\n" + "\n".join(self.parts) + "\n</svg>\n",
            encoding="utf-8",
        )
        return path


def make_overview(theme: Theme) -> Figure:
    """Draw how a query in Python becomes SQL for a database."""
    figure = Figure(760, 250, theme, "From Python objects to the SQL of a database")

    steps = (
        ("Tables and", "conditions", theme.box, theme.box_border),
        ("Query", "", theme.box, theme.box_border),
        ("Client", "and dialect", theme.accent_box, theme.accent),
        ("SQL and", "parameters", theme.box, theme.box_border),
        ("Database", "", theme.box, theme.box_border),
    )

    width, gap, top = 123, 35, 22

    for index, (first, second, fill, border) in enumerate(steps):
        x = index * (width + gap)
        figure.box(x + 1, top, width, 64, fill=fill, border=border)

        if second:
            figure.text(x + 1 + width / 2, top + 29, first, bold=True)
            figure.text(x + 1 + width / 2, top + 48, second, bold=True)
        else:
            figure.text(x + 1 + width / 2, top + 38, first, bold=True)

        if index:
            figure.arrow(x - gap + 5, top + 32, x - 3, top + 32)

    figure.text(1, 124, "What you write", size=12, color=theme.muted, anchor="start")
    figure.box(1, 134, 758, 38, fill=theme.code_box, border=theme.box_border, radius=6)
    figure.text(
        16,
        158,
        'client.select(orders, condition=(customer == "Ada") & (total > 50))',
        size=13,
        anchor="start",
        mono=True,
    )

    figure.text(1, 198, "What the database receives", size=12, color=theme.muted, anchor="start")
    figure.box(1, 208, 758, 38, fill=theme.code_box, border=theme.box_border, radius=6)
    figure.text(
        16,
        232,
        "SELECT ... FROM [orders] WHERE ([customer] = ?) AND ([total] > ?)",
        size=13,
        anchor="start",
        mono=True,
    )
    figure.text(744, 232, "['Ada', 50]", size=13, color=theme.accent, anchor="end", mono=True)

    return figure


def make_databases(theme: Theme) -> Figure:
    """Draw the clients, their libraries and their databases."""
    figure = Figure(760, 268, theme, "One interface for four databases")

    figure.box(1, 92, 136, 84, fill=theme.accent_box, border=theme.accent)
    figure.text(69, 128, "Your code", bold=True)
    figure.text(69, 150, "tables and queries", size=12, color=theme.muted)

    rows = (
        ("SqliteClient", "sqlite3", "SQLite"),
        ("PostgreSqlClient", "psycopg", "PostgreSQL"),
        ("MySqlClient", "pymysql", "MySQL, MariaDB"),
        ("SqlServerClient", "pyodbc", "SQL Server"),
    )

    figure.text(286, 16, "Client", size=12, color=theme.muted)
    figure.text(465, 16, "Library", size=12, color=theme.muted)
    figure.text(668, 16, "Database", size=12, color=theme.muted)

    for index, (client, library, database) in enumerate(rows):
        y = 28 + index * 60

        figure.arrow(137, 134, 194, y + 22)
        figure.box(198, y, 176, 44)
        figure.text(286, y + 27, client, bold=True)
        figure.arrow(374, y + 22, 406, y + 22)
        figure.box(410, y, 110, 44, fill=theme.code_box)
        figure.text(465, y + 27, library, size=13, mono=True)
        figure.arrow(520, y + 22, 574, y + 22)
        figure.box(578, y, 180, 44, radius=22)
        figure.text(668, y + 27, database)

    return figure


def make_parameters(theme: Theme) -> Figure:
    """Draw how the values of a condition travel apart from the statement."""
    figure = Figure(760, 232, theme, "The values of a condition are sent as parameters")

    figure.box(1, 78, 222, 76, fill=theme.accent_box, border=theme.accent)
    figure.text(112, 106, "Condition", size=12, color=theme.muted)
    figure.text(112, 132, 'name == "O\'Brien"', size=13, mono=True)

    figure.arrow(223, 104, 284, 52)
    figure.arrow(223, 128, 284, 180)

    figure.box(288, 14, 252, 76)
    figure.text(414, 42, "Statement", size=12, color=theme.muted)
    figure.text(414, 68, "... WHERE [name] = ?", size=13, mono=True)

    figure.box(288, 142, 252, 76, fill=theme.good_box, border=theme.good)
    figure.text(414, 170, "Parameters", size=12, color=theme.muted)
    figure.text(414, 196, '["O\'Brien"]', size=13, color=theme.good, mono=True)

    figure.arrow(540, 52, 602, 104)
    figure.arrow(540, 180, 602, 128)

    figure.box(606, 78, 153, 76, radius=38)
    figure.text(682, 121, "Database", bold=True)

    return figure


def make_joins(theme: Theme) -> Figure:
    """Draw which rows each kind of join keeps."""
    figure = Figure(760, 196, theme, "The rows which each kind of join keeps")

    kinds = (
        ("inner", "rows with a match", False, True, False),
        ("left", "all rows of the query's table", True, True, False),
        ("right", "all rows of the joined table", False, True, True),
        ("full", "all rows of both tables", True, True, True),
    )

    for index, (kind, caption, left, middle, right) in enumerate(kinds):
        center = 95 + index * 190
        left_x, right_x, y, radius = center - 26, center + 26, 76, 46
        clip = f"clip-{kind}-{theme.name}"

        figure.raw(
            f'<defs><clipPath id="{clip}"><circle cx="{right_x}" cy="{y}" r="{radius}"/>'
            f"</clipPath></defs>"
        )

        if left:
            figure.raw(f'<circle cx="{left_x}" cy="{y}" r="{radius}" fill="{theme.accent}"/>')

        if right:
            figure.raw(f'<circle cx="{right_x}" cy="{y}" r="{radius}" fill="{theme.accent}"/>')

        if not left or not right:
            # Empty the part of the other circle, then fill the middle again.
            for x, keep in ((left_x, left), (right_x, right)):
                if not keep:
                    figure.raw(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{theme.box}"/>')

            for x, keep in ((left_x, left), (right_x, right)):
                if keep:
                    figure.raw(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{theme.accent}"/>')

        if middle:
            figure.raw(
                f'<circle cx="{left_x}" cy="{y}" r="{radius}" fill="{theme.accent}" '
                f'clip-path="url(#{clip})"/>'
            )

        for x in (left_x, right_x):
            figure.raw(
                f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" '
                f'stroke="{theme.box_border}" stroke-width="1.5"/>'
            )

        figure.text(center, 152, f'kind="{kind}"', size=13, mono=True)
        figure.text(center, 174, caption, size=12, color=theme.muted)

    figure.text(4, 20, "table of the query", size=11, color=theme.muted, anchor="start")
    figure.text(186, 20, "joined table", size=11, color=theme.muted, anchor="end")

    return figure


def make_transaction(theme: Theme) -> Figure:
    """Draw how a transaction ends with a commit or with a rollback."""
    figure = Figure(760, 222, theme, "A transaction is committed or rolled back")

    figure.box(1, 82, 104, 58, fill=theme.accent_box, border=theme.accent)
    figure.text(53, 116, "begin()", size=13, mono=True)

    figure.arrow(105, 111, 141, 111)

    figure.box(145, 58, 250, 106, dashed=True)
    figure.text(270, 82, "Changes, not yet permanent", size=12, color=theme.muted)

    for index, label in enumerate(("insert", "update", "delete")):
        x = 159 + index * 76
        figure.box(x, 98, 68, 44, fill=theme.code_box)
        figure.text(x + 34, 125, label, size=13, mono=True)

    figure.arrow(395, 92, 451, 50, color=theme.good)
    figure.arrow(395, 130, 451, 172, color=theme.bad)

    figure.box(455, 20, 304, 62, fill=theme.good_box, border=theme.good)
    figure.text(471, 46, "commit()", size=13, color=theme.good, anchor="start", mono=True)
    figure.text(471, 68, "all changes take effect together", size=12, anchor="start")

    figure.box(455, 140, 304, 62, fill=theme.bad_box, border=theme.bad)
    figure.text(471, 166, "rollback()", size=13, color=theme.bad, anchor="start", mono=True)
    figure.text(471, 188, "all changes are undone", size=12, anchor="start")

    return figure


FIGURES = {
    "overview": make_overview,
    "databases": make_databases,
    "parameters": make_parameters,
    "joins": make_joins,
    "transaction": make_transaction,
}


def main() -> None:
    """Write every figure for every theme."""
    for name, make in FIGURES.items():
        for theme in THEMES:
            path = make(theme).save(name)
            print(f"wrote {path.relative_to(STATIC_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
