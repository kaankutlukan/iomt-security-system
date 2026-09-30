
from scapy.all import sniff, TCP, IP, Raw
import json
import re
from datetime import datetime

bpm_listesi = []
son_veri = None 

def paket_isle(paket):
    global son_veri
    
    if paket.haslayer(Raw) and paket.haslayer(TCP) and paket.haslayer(IP):
        try:
            veri = paket[Raw].load.decode('utf-8', errors='ignore')
            
            eslesme = re.search(r'\{"nabiz":(\d+),"oksijen":(\d+)', veri)
            if eslesme:
                nabiz = int(eslesme.group(1))
                oksijen = int(eslesme.group(2))
                
                
                anahtar = f"{nabiz}{oksijen}"
                if anahtar == son_veri:
                    return
                son_veri = anahtar
                
                bpm_listesi.append(nabiz)
                
               
                zaman = datetime.now().strftime("%H:%M:%S")
                print(f"[{zaman}] NABIZ: {nabiz} BPM | OKSİJEN: {oksijen}%")
                
        except:
            pass

print("[*] Nabız dinleniyor... (Ctrl+C ile durdur)\n")

try:
    sniff(
        iface="eth0",
        filter="tcp and host 172.20.10.14 and port 3000",
        prn=paket_isle,
        store=False
    )
except KeyboardInterrupt:
    print(f"\n{'='*40}")
    print(f"Toplam ölçüm : {len(bpm_listesi)}")
    if bpm_listesi:
        print(f"Ortalama     : {sum(bpm_listesi)//len(bpm_listesi)} BPM")
        print(f"Min          : {min(bpm_listesi)} BPM")
        print(f"Max          : {max(bpm_listesi)} BPM")
    print(f"{'='*40}")
