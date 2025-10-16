import random as r
from rich.console import Console
from rich.table import Table
from rich.text import Text
from helper.language_pack import lang_pack


console = Console()

def sontop_USER(lang,x):
    """Bu funksiyada User 1 dan x gacha son o'ylaydi
    kompyuter esa u sonni topishi kerak.Argument sifatida
    x ga 10 standart qiymati berilgan
    uni o'zgartirishingiz mumkin.
    Masalan: sontop_USER(50) " bu yerda
    1 dan 50 gacha sonlar o'ynaladi "
    """

    # Endi kopyuter son o'ylaydi
    # Endi siz 1 dan {x} gacha sonlar ichidan birini o'ylang men topaman
    console.print(f"\n{lang_pack [lang] ['T6'].format(x=x)}",style='yellow bold')

    # gar men aytgan son siznikidan katta bo'lsa '-', kichik bo'lsa '+' ni kiriting.
    # Agar tog'ri topgan bo'lsam, 'ok' deb yozing
    console.print(f"{lang_pack [lang] ['T7']}",style='yellow bold')

    taxmin_pc = 0

    # Yuqori va quyi nuqtani belgilab olamiz
    max = x
    min = 1
    console.print(f"\n{lang_pack [lang] ['T8']}\n>>> ",style='yellow bold')
    input()

    while True:
        # Yuqori va quyi nuqta teng emasligini aniqlaymiz
        if min != max:
            son = r.randint(min, max)
        # Agar teng bo'lib qolsa quyi chegarani son ga yuklaymiz
        else:
            son = min

        # javobni foydalanuvchidan qabul qilib olamiz
        console.print(f"\n{lang_pack [lang] ['T9'].format(son=son)}\n>>> ",style='yellow bold')
        javob = input().lower()
        # if javob != '+' or 'ok' or '-':
        #     console.print(f"\n{lang_pack [lang] ['T11']}",style='red bold')

        # Agar javob bo'lsa kod ishlaydi bo'lmasa else qismi ishlaydi
        if javob:
            if not javob.isdigit() and javob in ['-','+','ok']:
                if javob == "-":
                    max = son - 1
                    # Quyi chegarani manfiy songa aylanib ketishidan himoyalaymiz
                    if min > max:
                        console.print(f"\n{lang_pack [lang] ['T11']}",style = 'red bold')
                        # Birinchi taxmin qilgan sonidan ayirib ayirib \
                        # oxiri qayta qayta bir sonni chiqaradi
                        max = son

                    # Taxminni aniqligini ta'minlaymiz
                    else:
                        taxmin_pc += 1
                elif javob == "+":
                    min = son + 1
                    if min > max:
                        console.print(f"\n{lang_pack [lang] ['T12']}",style='red bold')
                        min = son
                    else:
                        taxmin_pc += 1
                elif javob == "ok":
                    console.print(f"\n{lang_pack [lang] ['T13']}\n",style='rgb(0,255,0)')
                    taxmin_pc += 1
                    break
            else:
                console.print(f"\n{lang_pack [lang] ['T11']}",style='red bold ')
                
        else:
            console.print(f"\n{lang_pack [lang] ['T14']}",style='red bold ')

    # Dasturni tugatamiz va bizga dastur kompyuterning taxminlar sonini qaytaradi
    return taxmin_pc