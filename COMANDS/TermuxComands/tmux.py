#!/usr/bin/env python3
"""
TMUX QO‘LLANMASI (QISQA VA TARTIBLI)

1. TMUX NIMA?
	Tmux — terminal session manager
	Serverdan chiqib ketsang ham botlar ishlayveradi

2. TMUX O‘RNATISH
	Ubuntu / Kali / Debian:
		sudo apt update
		sudo apt install tmux -y

	Tekshirish:
		tmux -V

3. YANGI SESSION OCHISH
	Buyruq:
		tmux new -s bot1

	Ichida botni ishga tushirish:
		cd bot_folder
		source venv/bin/activate
		python main.py

4. SESSIONDAN CHIQISH (BOT TO‘XTAMAYDI)
	CTRL + B  keyin  D

5. BOR SESSIONLARNI KO‘RISH
	tmux ls

6. SESSIONGA QAYTA KIRISH
	tmux attach -t bot1

7. BITTA BOTNI TO‘XTATISH
	tmux kill-session -t bot1

8. HAMMA BOTLARNI TO‘XTATISH
	tmux kill-server

9. 3 TA BOTNI ALOHIDA ISHLATISH
	tmux new -s dictbot
	tmux new -s gamebot
	tmux new -s statsbot

10. ENG KERAKLI ESLATMA
	SSH uzilsa ham tmux ichidagi bot ishlaydi
	Server o‘chsa — hammasi to‘xtaydi
"""

def main():
	print(__doc__)

if __name__ == "__main__":
	main()
