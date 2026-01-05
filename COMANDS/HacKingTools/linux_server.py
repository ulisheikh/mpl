#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import requests
import socket

# Telegram sozlamalari
BOT_TOKEN = "8284065959:AAEB1_8uVcXpMZCCQEfM8g2ZjKrDOh4ytY4"
CHAT_ID = "5830567800"

def send_telegram(url):
    """Public URL ni Telegram orqali yuborish"""
    message = f"🌍 Server ishga tushdi!\n\n🔗 {url}"
    url_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url_api, data=data)
        if r.status_code == 200:
            print("✅ Telegramga yuborildi!")
        else:
            print("❌ Yuborishda xato:", r.text)
    except Exception as e:
        print("❌ Telegram yuborishda muammo:", e)

def get_free_port(start=8000, end=8100):
    """Bo‘sh portni topish"""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError("Bo'sh port topilmadi!")

def start_local_server(port):
    """Python HTTP serverni ishga tushirish"""
    print(f"🌐 Lokal serverni ishga tushiryapman... port: {port}")
    subprocess.Popen(["python3", "-m", "http.server", str(port)])
    time.sleep(2)

def start_localtunnel(port):
    """LocalTunnel orqali public URL olish"""
    print("🚀 LocalTunnel ishga tushiryapman...")
    result = subprocess.Popen(
        ["lt", "--port", str(port), "--local-host", "127.0.0.1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True
    )
    for line in result.stdout:
        if "https://" in line:
            url = line.strip()
            print("🔗 Public URL:", url)
            with open("server_url.txt", "w") as f:
                f.write(url)
            send_telegram(url)
            break

if __name__ == "__main__":
    port = get_free_port()
    start_local_server(port)
    start_localtunnel(port)
