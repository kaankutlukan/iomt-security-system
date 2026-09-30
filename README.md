# Güvenli IoMT (Sağlık Nesnelerinin İnterneti) Ağı ve IPS Mimarisi

Bu proje, tıbbi IoT cihazlarının (IoMT) ürettiği hassas sağlık verilerini güvenli bir şekilde toplamak, işlemek ve ağ üzerindeki siber tehditlere karşı otonom olarak korumak amacıyla geliştirilmiş uçtan uca bir sistemdir.

## Proje Mimarisi ve Özellikler

Sistem üç temel katmandan oluşmaktadır:

1. **Donanım ve Gömülü Sistem (Hardware):**
   * Raspberry Pi ve MAX30102 nabız/oksijen sensörü entegrasyonu.
   * Fiziksel kararlılığı sağlamak ve gürültüyü (noise) filtrelemek için **KiCad** ile özel, tek yüzlü PCB (Baskılı Devre Kartı) tasarımı ve üretimi.
   * I2C protokolü üzerinden donanımsal haberleşme.

2. **Veri İşleme ve Sunucu (Node.js):**
   * Sensörden gelen ham sinyallerin anlık BPM ve SpO2 değerlerine dönüştürülmesi.
   * Verilerin web arayüzüne ve veritabanına aktarımı için RESTful API mimarisi.

3. **Saldırı Engelleme Sistemi - IPS (Python & Scapy):**
   * Ağ trafiğini gerçek zamanlı analiz eden otonom güvenlik duvarı.
   * SQL Enjeksiyonu (SQLi) ve Kaba Kuvvet (Brute-Force) saldırılarının anında tespiti ve otonom IP engelleme (Ban).
   * Ortadaki Adam (MitM - ARP Spoofing) saldırılarının tespiti ve ağ izolasyonu.

##  Kullanılan Teknolojiler
* **Donanım:** Raspberry Pi 3B+, MAX30102, KiCad EDA
* **Yazılım & Backend:** Node.js, Express.js, SQLite
* **Siber Güvenlik:** Python, Scapy (Packet Sniffing), Kali Linux
