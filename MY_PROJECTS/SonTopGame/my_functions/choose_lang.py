from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def choose_lang():
    text = "\nPlease select language: (ex: uz,ko,ru,en)\n>>>"
    while True:
        console.print(text,style='rgb(0,255,0) bold')
        select_lang = console.input()
        langs = ['uz','en','eng','ru','rus','kor','ko']
        if select_lang:
            if select_lang in langs:
                return select_lang

