from rich.console import Console
from rich.text import Text
from rich.progress import Progress
from rich.table import Table

# Console obyektini yaratish
console = Console()

table = Table(title="Rich Ranglar va Uslublar Metodlari")

table.add_column("Metod", justify="left", style="cyan", no_wrap=True)
table.add_column("Tavsif", style="magenta")
table.add_column("Namuna", style="white")

table.add_row("red", "Matnni qizil rangga bo‘yaydi", "[red]Qizil matn[/red]")
table.add_row("blue", "Matnni ko‘k rangga bo‘yaydi", "[blue]Ko‘k matn[/blue]")
table.add_row("green", "Matnni yashil rangga bo‘yaydi", "[green]Yashil matn[/green]")
table.add_row("yellow", "Matnni sariq rangga bo‘yaydi", "[yellow]Sariq matn[/yellow]")
table.add_row("bold", "Matnni qalin qiladi", "[bold]Qalin matn[/bold]")
table.add_row("dim", "Matnni xira qiladi", "[dim]Xira matn[/dim]")
table.add_row("italic", "Matnni kursiv qiladi", "[italic]Kursiv matn[/italic]")
table.add_row(
    "underline",
    "Matn ostiga chiziq qo‘yadi",
    "[underline]Ostiga chizilgan matn[/underline]",
)
table.add_row("blink", "Matnni miltillovchi qiladi", "[blink]Miltillovchi matn[/blink]")
table.add_row(
    "reverse",
    "Matn fon va matn rangini almashtiradi",
    "[reverse]O‘zgargan fon va matn[/reverse]",
)
table.add_row(
    "strikethrough",
    "Matn ustidan chiziq chizadi",
    "[strikethrough]Ustidan chizilgan matn[/strikethrough]",
)
table.add_row(
    "default", "Standart rangga qaytaradi", "[default]Standart matn[/default]"
)

console.print(table)


# 1. Rangli matn chiqarish
console.print("Bu matn qizil rangda.", style="red")
console.print("Bu matn yashil rangda.", style="green")
console.print("Bu matn ko'k rangda.", style="blue")

# 2. Bold va Italic matn
console.print("Bu matn qalin (bold) formatda.", style="bold")
console.print("Bu matn kursiv (italic) formatda.", style="italic")

# 3. Kattalikni o'zgartirish
text = Text("Bu matn katta o'lchamda", style="bold red")
console.print(text)

# 4. Underline va Reverse uslublari
console.print("Bu matn taglik ostida.", style="underline")
console.print("Bu matn teskari rangda.", style="reverse")

# 5. Qalin va rangli matn
console.print("Bu matn qizil rangda va qalin.", style="bold red")
console.print("Bu matn yashil rangda va qalin.", style="bold green")

# 6. Highlight (Ta'kidlash) matn
console.print("Bu matn ta'kidlangan (highlighted).", style="on yellow")

# 7. Kichik va katta matn
text1 = Text("Kichik matn", style="bold green")
console.print(text1)

text2 = Text("Katta matn", style="bold blue")
console.print(text2)

# 8. Progress bar (Yuklash animatsiyasi)
with Progress(transient=True) as progress:
    task = progress.add_task("[cyan]Yuklanmoqda...", total=100)
    while not progress.finished:
        progress.update(task, advance=1)

# 9. Yirik matn va boshlang'ich formatlash
text3 = Text("Yirik Matn", style="bold magenta")
console.print(text3)

# 10. Rangli va atributlar birlashishi
console.print(
    "Bu matn bir nechta rang va atributlar bilan.", style="bold underline on yellow red"
)

# 11. Jadval yaratish
table = Table(title="Matn jadvali")
table.add_column("Ism", style="cyan", no_wrap=True)
table.add_column("Yosh", style="magenta")
table.add_column("Shahar", style="green")
table.add_row("John Doe", "25", "New York")
table.add_row("Jane Doe", "28", "Los Angeles")
# console.print(table)


from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Rich Ranglar va Uslublar Metodlari", show_lines=True)

table.add_column("Metod", justify="left", style="cyan", no_wrap=True)
table.add_column("Tavsif", style="magenta")
table.add_column("Namuna", style="white")

table.add_row("red", "Matnni qizil rangga bo‘yaydi", "[red]Qizil matn[/red]")
table.add_row("blue", "Matnni ko‘k rangga bo‘yaydi", "[blue]Ko‘k matn[/blue]")
table.add_row("green", "Matnni yashil rangga bo‘yaydi", "[green]Yashil matn[/green]")
table.add_row("yellow", "Matnni sariq rangga bo‘yaydi", "[yellow]Sariq matn[/yellow]")
table.add_row("bold", "Matnni qalin qiladi", "[bold]Qalin matn[/bold]")
table.add_row("dim", "Matnni xira qiladi", "[dim]Xira matn[/dim]")
table.add_row("italic", "Matnni kursiv qiladi", "[italic]Kursiv matn[/italic]")
table.add_row(
    "underline",
    "Matn ostiga chiziq qo‘yadi",
    "[underline]Ostiga chizilgan matn[/underline]",
)
table.add_row("blink", "Matnni miltillovchi qiladi", "[blink]Miltillovchi matn[/blink]")
table.add_row(
    "strikethrough",
    "Matn ustidan chiziq chizadi",
    "[strikethrough]Ustidan chizilgan matn[/strikethrough]",
)
table.add_row(
    "reverse",
    "Matn fon va matn rangini almashtiradi",
    "[reverse]O‘zgargan fon va matn[/reverse]",
)
table.add_row(
    "default", "Standart rangga qaytaradi", "[default]Standart matn[/default]"
)

# console.print(table)
