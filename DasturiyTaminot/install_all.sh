#!/bin/bash

# 1. Tizimni yangilash
echo "--- Tizim tayyorlanmoqda ---"
sudo apt update -y

# 2. Asosiy asboblar va Micro
echo "--- Micro va Kerakli paketlar o'rnatilmoqda ---"
sudo apt install micro wget curl unzip git python3 python3-pip libgl1-mesa-glx libxcb-xinerama0 -y

# 3. Brauzerlar (Chrome va Brave)
echo "--- Brauzerlar o'rnatilmoqda ---"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
rm google-chrome-stable_current_amd64.deb
curl -fsS https://dl.brave.com/install.sh | sudo sh

# 4. Micro sozlamalari
echo 'export EDITOR="micro"' >> ~/.bashrc
echo 'alias nano="micro"' >> ~/.bashrc

# 5. Telegram, VirtualBox va VS Code (Warningni tuzatish bilan)
echo "--- Telegram, VirtualBox va VS Code o'rnatilmoqda ---"
sudo rm -f /etc/apt/sources.list.d/vscode.list /etc/apt/sources.list.d/vscode.sources # Eskilarini tozalash
sudo apt install telegram-desktop virtualbox -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update && sudo apt install code -y
rm packages.microsoft.gpg

# 6. Koreys tili hangul
sudo apt update
sudo apt install ibus ibus-hangul im-config -y

# 8. Bluetooth Fix
echo "--- Bluetooth qayta o'rnatilmoqda ---"
sudo apt purge --autoremove -y bluez blueman
sudo apt install -y bluez blueman pulseaudio-module-bluetooth
sudo systemctl enable bluetooth --now

echo "--------------------------------------------------------"
echo "--- SKRIPT YAKUNLANDI! ---"
echo "--- 1. Kompyuterni REBOOT qiling (MUHIM!). ---"
echo "--- 2. Rebootdan keyin 'fcitx5-configtool'ni oching. ---"
echo "--- 3. 'Only Show Current Language'ni o'chirib, Hangul qo'shing. ---"
echo "--------------------------------------------------------"
