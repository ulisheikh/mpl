from rich.console import Console
from rich.table import Table
from random import randint
from rich.text import Text

console = Console()
table = Table()

table = Table(title="Test", show_lines=True)

names = [
    "ali",
    "vali",
    "shokir",
    "shukur",
    "ilhom",
    "ikrom",
    "botir",
    "jobir",
    "g'olib",
    "axror",
]
kurs = [4, 2, 2, 4, 3, 1, 4, 3, 3, 2]
contry = "uzbekistan"
old = [randint(15, 30) for _ in range(len(names))]
table.add_column(Text("Ism", justify="center", style="bold blue"))
table.add_column(Text("Bosqich", justify="center", style="bold blue"))
table.add_column(Text("Mamlakat", justify="center", style="bold blue"))
table.add_column(Text("Yosh", justify="center", style="bold blue"))
for i in range(len(names)):
    table.add_row(
        Text(names[i].title(), style="bold underline white", justify="center"),
        Text(str(kurs[i]), justify="center", style="on yellow bold"),
        Text(contry.title(), style="reverse bold ", justify="center"),
        Text(str(old[i]), justify="center"),
    )


console.print(table)
