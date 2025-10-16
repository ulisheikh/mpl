from colorama import Fore, init , Style
print("======================================================"
      "\nFaqat ranglar\n")
init()  # Rangli matnni to'g'ri ko'rsatish uchun

print(Fore.RED + "Bu qizil rangdagi matn")
print(Fore.GREEN + "Bu yashil rangdagi matn")
print(Fore.YELLOW + "Bu sariq rangdagi matn")
print(Fore.BLUE + "Bu ko'k rangdagi matn")
print(Fore.MAGENTA + "Bu pushti rangdagi matn")
print(Fore.CYAN + "Bu moviy rangdagi matn")
print(Fore.WHITE + "Bu oq rangdagi matn")

print("\n======================================================"
      "\nYorqinligi va qalinligi\n")

# Ranglar va uslublar
init(autoreset=True)  # Avtomatik reset qilish

print(Fore.RED + 'Bu qizil rangda matn')         # Qizil rang
print(Fore.GREEN + 'Bu yashil rangda matn')      # Yashil rang
print(Fore.YELLOW + Style.BRIGHT + 'Bu yorqin sariq matn')  # Yorqin sariq rang
print(Fore.CYAN + Style.DIM + 'Bu kam yorqin ko\'k matn')  # Kam yorqin ko'k rang
print("\n======================================================\nTermocolor\n")

from termcolor import colored

# Rangli va qalin formatda matn chiqarish
print(colored('Matn qizil rangda va qalin', 'red', attrs=['bold']))

# Rangli va taglik ostidagi matn
print(colored('Matn yashil rangda va taglik ostida', 'green', attrs=['underline']))

# Ko'k rangda va teskari ranglar bilan matn
print(colored('Matn ko\'k rangda va teskari', 'red', attrs=['reverse']))
print(colored('Matn sariq fon va qora rangda', 'yellow', 'on_black'))
print("======================================================")
