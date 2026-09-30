import socketio
from max30102 import MAX30102
import hrcalc
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sio = socketio.Client(ssl_verify=False)

try:
   
    sio.connect('http://localhost:3000')
    print("[+] Sunucuya GÜVENLİ (HTTPS) bağlantı sağlandı.")
except Exception as e:
    print(f"[!] Sunucuya bağlanılamadı! Hata: {e}")

sensor = MAX30102()
nabiz_gecmisi = []

print("[*] Sistem hazır, veriler gönderiliyor...")

try:
    while True:
        red_liste, ir_liste = sensor.read_sequential()
        nabiz, nabiz_gecerli, oksijen, oksijen_gecerli = hrcalc.calc_hr_and_spo2(ir_liste, red_liste)
        
        if nabiz_gecerli and oksijen_gecerli:
            temiz_oksijen = int(oksijen)
            
            if 40 < nabiz < 130:
                nabiz_gecmisi.append(nabiz)
                if len(nabiz_gecmisi) > 5:
                    nabiz_gecmisi.pop(0)
                
                if len(nabiz_gecmisi) >= 3:
                    ortalama_nabiz = int(sum(nabiz_gecmisi) / len(nabiz_gecmisi))
                    
                    # SUNUCUYA VERİ GÖNDERME
                    if sio.connected:
                        sio.emit('yeni_veri_geldi', {
                            'nabiz': ortalama_nabiz,
                            'oksijen': temiz_oksijen,
                            'durum': '📡 Canlı Veri Alınıyor'
                        })
                        print(f"[*] Gönderildi: {ortalama_nabiz} BPM")
                    else:
                        print("[!] Bağlantı koptuğu için veri gönderilemedi!")

except KeyboardInterrupt:
    print("\n[!] Kapatılıyor...")
    sio.disconnect()
    sensor.shutdown()
