import random as r
from rich.console import Console
from rich.table import Table
from rich.text import Text
from my_functions.sontop_PC import sontop_PC
from my_functions.sontop_USER import sontop_USER
from helper.language_pack import lang_pack
from my_functions.choose_lang import choose_lang
from openpyxl import Workbook


console = Console()


def play(x=10):
    """Bu funksiyaning maqsadi < sontop_PC() & sontop_USER() >
    funksiyalari uchun play vazifasini bajaradi va
    natijalarni ko'rsatib beradi"""
    # Foydalanuvchidan ismini qabul qilib olamiz
    select_lang = choose_lang()

    while True:
        console3 = Console()
        console3.print(f"\n{lang_pack[select_lang]["T15"]} \n>>> ",style= 'cyan'' bold')
        name = input().lower()
        if name:
            console3.print(f"\n                    {lang_pack[select_lang]["T16"]} {name.lower()} 님 ",style='White bold')
            name = name.capitalize()
            break

    # While yordamida sikl yaratamiz
    flag2 = True
    part = 0
    part_winner_user = 0
    part_winner_pc = 0
    draw = 0

    while flag2:
        part += 1
        # WINNER bizga g'olibni aniqlab beradi
        WINNER = ""

        # O'yinlar start oladi
        taxmin_user = sontop_PC(select_lang,x)
        taxmin_pc = sontop_USER(select_lang,x)

        # # Natijani oddiy qilib chiqaramiz
        # print(f"\nNatija:\n================\n"
        # f" USER: {taxmin_user}\n PC: {taxmin_pc}\n================")

        # G'olibni aniqlaymiz taxmin sonlari yordamida
        if taxmin_pc > taxmin_user:
            WINNER = "USER"
            print(f"{lang_pack [select_lang] ['T17']}")
        elif taxmin_pc < taxmin_user:
            WINNER = "PC"
            print(f"{lang_pack [select_lang] ['T18']}\n")
        else:
            WINNER = "Draw"
            # Draw bizga  durrangni aniqlab beradi
            draw += 1


        # winner_pc va user bizga rich jadvalida yutgan va yutqazganni backgroundini rangini beradi
        winner_pc = "bold blue "
        winner_user = "bold blue "
        if WINNER == "PC":
            winner_user = "bold red"

            # part_winner bizga partiyadagi g'olibni aniqlab beradi
            part_winner_pc += 1

        elif WINNER == "USER":
            winner_pc = "bold red"

            # part_winner bizga partiyadagi g'olibni aniqlab beradi
            part_winner_user += 1

        # Jadval tuzishni boshladik
        console = Console()
        table = Table(title="WordGame", show_lines=False, style="blue bold")

        # Jadvalga ikta ustun qo'shamiz
        table.add_column(Text(r"  \_\_R_E_S_U_L_T_S_/_/  ", style="cyan"), style="white")
        # table.add_column()

        # Jadvalga uchta qator qo'shamiz
        table.add_row(Text("", justify="center"))  # Bo'sh qator uchun
        table.add_row(Text(f"| P a r t |", justify="center"), style="bold blue")
        table.add_row(Text(f"[{str(part)}]", justify="center"), style="bold red")
        table.add_row(Text("", justify="center"))  # Bo'sh qator uchun
        table.add_row(
            Text(f"PC:  guesses: {str(taxmin_pc)}", justify="center", style="italic"),
            style=f"{winner_pc}",
        )
        table.add_row(
            Text(f"{name.upper()}: guesses:{str(taxmin_user)}", style="italic", justify="center"),
            style=f"{winner_user}",
        )
        table.add_row(Text("", justify="center"))  # Bo'sh qator uchun
        table.add_row(
            Text(f"WINNER: {str(WINNER)}", justify="center"), style="bold red on blue"
        )

        # Jadvalni print qilamiz
        console.print(table)


        # Foydalanuvchidan o'yinni davom etish yoki to'xtatishini so'raymiz
        # while True:
        #     javob2 = input('\nYana o\'ynashni hohlaysizmi? \n       '
        #                   'Ha uchun: 1\n       Yo\'q uchun: 0\n>>> ').lower()
        #     if javob2.isdigit():
        #         javob2 = int(javob2)
        #         if javob2 == 1:
        #             break
        #         elif javob2 == 0:
        #             flag2 = False
        #             break
        #     else:
        #         print("\nIltimos faqat 1 yoki 0 ni kiriting")
        while True:
            console.print(                 f"\n{lang_pack [select_lang] ['T19']} \n       "
            f"{lang_pack [select_lang] ['T20']}\n>>> ",style='rgb(38,17,232) bold')
            javob2 = input().strip()
            if javob2 in ["0", "1"]:
                flag2 = javob2 == "1"
                break
            else:
                console.print(f"\n{lang_pack [select_lang] ['T21']}",style='red bold')

    table2 = Table(title="\nTotal score in the game", style="white bold")

    table2.add_column(
        Text("WordGameResults", justify="center", style='rgb(38,17,232) bold'), style="reverse"
    )
    table2.add_row(Text("Total part", justify="center"))
    table2.add_row(Text(str(part), justify="center"))
    table2.add_row(Text("", justify="center"))  # Bo'sh qator uchun
    table2.add_row(
        Text(f"{name.upper()} won the game [{str(part_winner_user)}] times", justify="center")
    )
    table2.add_row(Text("", justify="center"))  # Bo'sh qator uchun
    table2.add_row(
        Text(f"PC won the game [{str(part_winner_pc)}] times", justify="center")
    )
    table2.add_row(Text("", justify="center"))  # Bo'sh qator uchun
    table2.add_row(Text(f"DRAW: [{str(draw)}]", justify="center"))
    table2.add_row(Text("", justify="center"))  # Bo'sh qator uchun

    console.print(table2)

    # Natijalarni exel file orqali yozib boramiz
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    wb = Workbook()
    ws = wb.active
    ws.title = "Game Results"

    # Jadval sarlavhalari
    ws.merge_cells('A1:B1')
    ws['A1'] = "WordGameResults"

    # cell = ws['A1']
    # cell.font = Font(bold=True,size=14,color='FFFF00')

    ws['A1'].alignment = Alignment(horizontal='center')
    ws.append(['Info','Value'])

    # O'yin natijalari
    ws.append(["Total part",part])
    ws.append([name,part_winner_user])
    ws.append(["PC",part_winner_pc])
    ws.append(["Draw",draw])

    # Jadvalni saqlaymiz
    wb.save("game_results.xlsx")

    # Dasturni{ tugatamiz
    console.print(Text(f"\n{lang_pack [select_lang] ['T22']}\n",style='yellow bold'))
    return part,name,part_winner_pc,part_winner_user,draw




