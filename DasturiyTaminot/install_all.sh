#!/bin/bash

# 1. Repozitoriylarni yangilash va GPG kalit muammosini hal qilish
echo "--- Tizimni tayyorlash va kalitlarni yangilash ---"
wget -q -O - https://archive.kali.org/archive-key.asc | sudo apt-key add -
sudo apt update -y

# 2. Google Chrome o'rnatish
echo "--- Google Chrome o'rnatilmoqda ---"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
rm google-chrome-stable_current_amd64.deb

# 3. Telegram Desktop o'rnatish
echo "--- Telegram o'rnatilmoqda ---"
sudo apt install telegram-desktop -y

# 4. VirtualBox o'rnatish
echo "--- VirtualBox o'rnatilmoqda ---"
sudo apt install virtualbox -y

# 5. Visual Studio Code o'rnatish
echo "--- VS Code o'rnatilmoqda ---"
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt install apt-transport-https -y
sudo apt update -y
sudo apt install code -y
rm packages.microsoft.gpg

# 6. Koreys tili shriftlari va klaviaturasi (IBus va Fcitx)
echo "--- Koreys tili paketlari o'rnatilmoqda ---"
sudo apt install fonts-nanum fonts-noto-cjk ibus-hangul fcitx-hangul -y

# 7. Bluetooth (Oldin tozalab, keyin yangidan o'rnatish)
echo "--- Bluetooth qayta o'rnatilmoqda ---"
sudo systemctl stop bluetooth
sudo apt purge --autoremove -y bluez blueman pulseaudio-module-bluetooth
rm -rf ~/.config/blueman
sudo apt install -y bluez blueman pulseaudio-module-bluetooth
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

echo "--- Barcha dasturlar muvaffaqiyatli o'rnatildi! ---"
