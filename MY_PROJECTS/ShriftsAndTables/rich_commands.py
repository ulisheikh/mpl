from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text

console = Console()

# 🔹 Rangli matn chiqarish
print("[bold red]Salom, bu Rich kutubxonasi![/bold red]")

# 🔹 Jadval yaratish
table = Table(title="Foydalanuvchilar")
table.add_column("ID", style="cyan")
table.add_column("Ism", style="magenta")
table.add_column("Yosh", style="green")
table.add_row("1", "Ali", "25")
table.add_row("2", "Vali", "30")
console.print(table)

# 🔹 Progress bar
with Progress() as progress:
    task = progress.add_task("[cyan]Yuklanmoqda...", total=100)
    for i in range(100):
        progress.update(task, advance=1)

# 🔹 Panel yaratish
panel = Panel("[bold green]Bu Rich kutubxonasining paneli![/bold green]")
console.print(panel)

# 🔹 Matnni o'zgacha formatda chiqarish
styled_text = Text("Bu maxsus formatdagi matn!", style="bold underline blue")
console.print(styled_text)
