from max30102 import MAX30102
import time


sensor = MAX30102()

print("Sensör başlatıldı! Lütfen parmağınızı kırmızı ışığın üzerine koyun...")
print("-" * 50)

try:
    while True:
        
        red, ir = sensor.read_sequential()
        
        
        print(f"Kırmızı Işık (Kan Hacmi): {red} | Kızılötesi: {ir}")
        
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nTest sonlandırıldı.")
    sensor.shutdown()
