from flask import Flask, request, jsonify
import time
from datetime import datetime
import os
import logging


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
ip_db = {} 
LOG_DOSYASI = os.path.join(os.path.dirname(__file__), "guvenlik_loglari.txt")

def ekran_yaz(ip, user, durum, mesaj):
    zaman = datetime.now().strftime("%H:%M:%S")
    etiket = f"[{durum}]"
    print(f"[{zaman}] {ip.ljust(15)} | {user.ljust(15)} | {etiket.ljust(10)} -> {mesaj}")
    with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
        f.write(f"[{zaman}] IP: {ip} | User: {user} | Durum: {durum} | {mesaj}\n")

@app.route('/kontrol', methods=['POST'])
def kontrol_et():
    veriler = request.json
    ip = veriler.get('ip', 'unknown').replace('::ffff:', '')
    user = veriler.get('user', 'unknown')
    basarili = veriler.get('basarili')

    if ip not in ip_db:
        ip_db[ip] = {"hata": 0, "banli": False}

    # 1. BAN KONTROLÜ
    if ip_db[ip]["banli"]:
        return jsonify({"durum": "engellendi"})

    # 2. BAŞARILI GİRİŞ
    if basarili:
        ip_db[ip]["hata"] = 0
        ekran_yaz(ip, user, "BAŞARILI", "Giriş yapıldı, puanlar sıfırlandı.")
        return jsonify({"durum": "izin_verildi"})
    
    # 3. HATA VE CEZA MANTIĞI
    ip_db[ip]["hata"] += 1
    hata = ip_db[ip]["hata"]

    if hata >= 4:
        ip_db[ip]["banli"] = True
        print("-" * 80)
        ekran_yaz(ip, user, "KRİTİK", "🚫 4. HATA! IP ADRESİ SİSTEMDEN BANLANDI!")
        print("-" * 80)
        return jsonify({"durum": "engellendi"})

    if "'" in user or "=" in user:
        ekran_yaz(ip, user, "UYARI", f"⚠️ SQL Injection şüphesi! ({hata}. deneme)")
    else:
        ekran_yaz(ip, user, "DENEME", f"Hatalı şifre denemesi. ({hata}. deneme)")

    return jsonify({"durum": "yavaslat", "hata": hata})

@app.route('/log_yaz', methods=['POST'])
def log_kapisi():
    data = request.json
    ekran_yaz(data['ip'], data['user'], "CEZA", "10 saniye bekleme bitti, erişim açıldı.")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("\n" + "="*80)
    print(" RASPBERRY PI IPS (SALDIRI ENGELLEME SİSTEMİ) AKTİF")
    print(f" Log Dosyası: {LOG_DOSYASI}")
    print("="*80 + "\n")
    app.run(port=5000, host='0.0.0.0')
