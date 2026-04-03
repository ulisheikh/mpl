#!/bin/bash

echo "--- Tizim yangilanmoqda ---"
sudo apt update && sudo apt upgrade -y

echo "--- Asosiy paketlar ---"
sudo apt install -y micro wget curl unzip git python3 python3-pip \
libgl1-mesa-glx libxcb-xinerama0

echo "--- Brauzerlar ---"
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
curl -fsS https://dl.brave.com/install.sh | sudo sh

echo "--- Micro sozlama ---"
echo 'export EDITOR="micro"' >> ~/.bashrc
echo 'alias nano="micro"' >> ~/.bashrc

echo "--- Telegram, VirtualBox, VS Code ---"
sudo rm -f /etc/apt/sources.list.d/vscode.list /etc/apt/sources.list.d/vscode.sources
sudo apt install -y telegram-desktop virtualbox

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list

sudo apt update && sudo apt install -y code
rm packages.microsoft.gpg

echo "--- IBus (Koreys Hangul) ---"
sudo apt install -y ibus ibus-hangul ibus-gtk ibus-gtk3 im-config

echo "--- IBus default ---"
im-config -n ibus

echo "--- Autostart qo‘shilmoqda ---"
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/ibus.desktop <<EOF
[Desktop Entry]
Type=Application
Name=IBus
Exec=ibus-daemon -drx
StartupNotify=false
Terminal=false
EOF

echo "--- Environment fix ---"
cat > ~/.xprofile <<EOF
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
ibus-daemon -drx
EOF

echo "--- Bluetooth fix ---"
sudo apt purge --autoremove -y bluez blueman
sudo apt install -y bluez blueman pulseaudio-module-bluetooth
sudo systemctl enable bluetooth --now

echo "--------------------------------------------------------"
echo "✅ HAMMASI TAYYOR"
echo "👉 REBOOT QILING!"
echo ""
echo "Rebootdan keyin:"
echo "1. ibus-setup"
echo "2. Korean → Hangul qo‘sh"
echo "--------------------------------------------------------"
