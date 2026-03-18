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

# 5. Telegram, VirtualBox va VS Code
echo "--- Telegram, VirtualBox va VS Code o'rnatilmoqda ---"
sudo apt install telegram-desktop virtualbox -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update && sudo apt install code -y
rm packages.microsoft.gpg

# 6. Koreys tili va Fcitx5 (Klaviatura)
echo "--- Koreys tili va Fcitx5 sozlanmoqda ---"
sudo apt install fonts-nanum* fonts-noto-cjk fcitx5 fcitx5-hangul fcitx5-config-qt im-config -y
im-config -n fcitx5

# 7. Cisco Packet Tracer uchun muhitni tayyorlash
# (Eski Sicko Tracker papkasini o'chirib tashlaymiz)
echo "--- Cisco Packet Tracer uchun kutubxonalar tayyorlanmoqda ---"
rm -rf ~/sickotracker
sudo apt install libdouble-conversion3 libqt5gui5 libqt5network5 libqt5widgets5 libqt5printsupport5 libqt5multimedia5 libqt5x11extras5 libqt5sql5 libqt5svg5 libqt5xml5 libqt5pdf5 -y

# 8. Bluetooth Fix
echo "--- Bluetooth qayta o'rnatilmoqda ---"
sudo apt purge --autoremove -y bluez blueman
sudo apt install -y bluez blueman pulseaudio-module-bluetooth
sudo systemctl enable bluetooth --now

echo "--------------------------------------------------------"
echo "--- SKRIPT YAKUNLANDI! ---"
echo "--- 1. Kompyuterni REBOOT qiling. ---"
echo "--- 2. Cisco Packet Tracer .deb faylini yuklab olgan bo'lsangiz: ---"
echo "---    'sudo apt install ./CiscoPacketTracer.deb' deb yozing. ---"
echo "--- 3. Koreys tili: Fcitx5-dan 'Hangul'ni qo'shing. ---"
echo "--------------------------------------------------------"
