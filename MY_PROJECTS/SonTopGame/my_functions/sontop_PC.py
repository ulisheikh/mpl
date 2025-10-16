import random as r
from rich.console import Console
from rich.table import Table
from rich.text import Text
from helper.language_pack import lang_pack
# from FUNCTIONS.choose_lang import choose_lang


console = Console()

def sontop_PC(lang,x):
    """Bu funksiyada kompyuter 1 dan x gacha son o'ylaydi
    user esa u sonni topishi kerak.Argument sifatida
    x ga 10 standart qiymati berilgan
    uni o'zgartirishingiz mumkin.
    Masalan: sontop_PC(50) " bu yerda
    1 dan 50 gacha sonlar o'ynaladi "
    """
    

    

    # O'yinni boshlaymiz, kompyuter son o'yladi
    # Men 1dan x gacha son o'yladim topishga harakat qiling
    console.print(f"\n{lang_pack[lang]['T1'].format(x=x)}", style='bold yellow')

    # console.print(f"\nMen 1 dan {x} gacha bir son o'yladim topishga harakat qilib ko'ring",style='bold yellow')
    
    # Son esa tasodifiy bo'lib tanlanadi
    son = r.randint(1, x)

    # Siklni to'xtatish uchun flag dan foydalanamiz
    flag = 1

    # Taxminlarni 0 dan boshlab hisoblaymiz
    taxmin_user = 0

    # Start
    while flag:

        print(son)
        javob = console.input(">>>\n")

        # Javob raqamligini tekshirib olamiz
        if javob.isdigit():

            javob = int(javob)
            if javob < son:
                # katta
                console.print(f"{lang_pack [lang] ['T2'].format(javob=javob)}",style='bold yellow')
                taxmin_user += 1
            elif javob > son:
                # kichik
                console.print(f"{lang_pack [lang] ['T3'].format(javob=javob)}",style='bold yellow')
                taxmin_user += 1
            elif javob == son:
                # topdingiz
                console.print(f"{lang_pack [lang] ['T4']}",style='rgb(0,255,0) bold')
                taxmin_user += 1
                flag = 0

        # Raqam bo'lmasa...
        else:
            # iltimos butun son kiriting
            console.print(f"\n{lang_pack [lang] ['T5']}",style='red bold')

    # funksiya tuggaydi va bizga foydalanuvchining taxminlar sonini qaytaradi
    return taxmin_user