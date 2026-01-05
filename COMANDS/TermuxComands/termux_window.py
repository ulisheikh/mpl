def main():
    text = """
TMUX QO‘LLANMASI (SESSION / WINDOW / PANE)

================ SESSION =================
tmux new -s bot1
	Yangi session ochish (nomi: bot1)

tmux ls
	Barcha sessionlarni ko‘rish

tmux attach -t bot1
	Mavjud sessionga kirish

tmux detach   (Ctrl + b  keyin  d)
	Sessiondan chiqish (o‘chmaydi)

tmux kill-session -t bot1
	Sessionni to‘liq o‘chirish

tmux kill-server
	BARCHA sessionlarni o‘chirish


================ WINDOW =================
Ctrl + b  keyin  c
	Yangi window ochish

Ctrl + b  keyin  n
	Keyingi window

Ctrl + b  keyin  p
	Oldingi window

Ctrl + b  keyin  0-9
	Raqam bo‘yicha window tanlash

Ctrl + b  keyin  ,
	Window nomini o‘zgartirish

Ctrl + b  keyin  &
	Window’ni yopish


================ PANE =================
Ctrl + b  keyin  %
	Vertikal bo‘lish (yonma-yon)

Ctrl + b  keyin  "
	Gorizontal bo‘lish (tepaga/pastga)

Ctrl + b  keyin  o
	Keyingi pane’ga o‘tish

Ctrl + b  keyin  ← ↑ ↓ →
	Yo‘nalish bilan pane almashtirish

Ctrl + b  keyin  x
	Paneni yopish

Ctrl + b  keyin  z
	Paneni fullscreen qilish (yana bosilsa qaytadi)


================ AMALIY MISOL =================
1 ta sessionda 3 ta bot:

tmux new -s bots
	Ctrl+b c   → 1-window (dictbot)
	Ctrl+b c   → 2-window (quizbot)
	Ctrl+b c   → 3-window (otherbot)

Har window ichida:
	python main.py


================ FOYDALI =================
tmux rename-session -t old new
	Session nomini almashtirish

tmux move-window -t 1
	Window tartibini o‘zgartirish

tmux info
	Tmux info


================ ESLATMA =================
Ctrl + b  — tmux prefix
Avval Ctrl + b, keyin buyruq bosiladi
"""
    print(text)


if __name__ == "__main__":
    main()
