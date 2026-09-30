const express = require('express');
const http = require('http');
const fs = require('fs');
const socketIo = require('socket.io');
const sqlite3 = require('sqlite3').verbose();
const axios = require('axios');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// --- 1. HTTP VE VERİTABANI ---
const server = http.createServer(app); 
const io = socketIo(server, { cors: { origin: "*" } });
const db = new sqlite3.Database('./users.db');

// --- 2. GÜVENLİK VE OTURUM AYARLARI ---
let isLoggedIn = false;

const bekle = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const xssTemizle = (metin) => {
    if (typeof metin !== 'string') return metin;
    return metin.replace(/</g, "&lt;").replace(/>/g, "&gt;");
};

const merkeziLog = async (ip, user, mesaj) => {
    try {
        await axios.post('http://localhost:5000/log_yaz', { ip, user, mesaj });
    } catch (e) {}
};

// --- 3. GÜVENLİ ROTALAR ---

app.get('/monitor', (req, res) => {
    if (!isLoggedIn) {
        console.log("⚠️ Yetkisiz erişim: /monitor engellendi!");
        return res.redirect('/');
    }
    res.sendFile(path.join(__dirname, 'monitor.html'));
});

app.get('/ayarlar', (req, res) => {
    if (!isLoggedIn) {
        console.log("⚠️ Yetkisiz erişim: /ayarlar engellendi!");
        return res.redirect('/');
    }
    res.sendFile(path.join(__dirname, 'ayarlar.html'));
});

// --- 4. GİRİŞ VE ÇIKIŞ İŞLEMLERİ ---

app.get('/', (req, res) => {
    isLoggedIn = false;
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/login', async (req, res) => {
    const { user, pass } = req.body;
    const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    const temizIp = clientIp.replace('::ffff:', '');

    db.get("SELECT * FROM users WHERE username = ? AND password = ?", [user, pass], async (err, row) => {
        if (row) {
            isLoggedIn = true;
            await axios.post('http://localhost:5000/kontrol', { ip: temizIp, user: user, basarili: true });
            return res.redirect('/monitor');
        } else {
            const savunma = await axios.post('http://localhost:5000/kontrol', { ip: temizIp, user: user, basarili: false });
            
            if (savunma.data.durum === "engellendi") return res.status(403).send("<h1>🚫 BAN</h1>");
            
            if (savunma.data.durum === "yavaslat") {
                await bekle(10000);
                await merkeziLog(temizIp, user, "10sn ceza bitti.");
                return res.send("<h2>❌ Hatalı Giriş!</h2><p>10sn bekletildiniz.</p><a href='/'>Geri Dön</a>");
            }
            return res.send("<h2>❌ Hatalı Giriş!</h2><a href='/'>Geri Dön</a>");
        }
    });
});

// --- 5. GÜNCELLEME ---
app.post('/guncelle', async (req, res) => {
    if (!isLoggedIn) return res.status(401).send("Yetkisiz işlem!");

    let { eski_kullanici, yeni_kullanici, yeni_sifre } = req.body;
    const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    const temizIp = clientIp.replace('::ffff:', '');

    yeni_kullanici = xssTemizle(yeni_kullanici);

    db.get("SELECT * FROM users WHERE username = ?", [eski_kullanici], async (err, row) => {
        if (row) {
            db.run("UPDATE users SET username = ?, password = ? WHERE username = ?", 
            [yeni_kullanici, yeni_sifre, eski_kullanici], async () => {
                await merkeziLog(temizIp, yeni_kullanici, "Kullanıcı bilgileri güncellendi.");
                res.send("<h2>✅ Başarıyla Güncellendi!</h2><a href='/monitor'>Panele Dön</a>");
            });
        } else {
            res.send("<h2>❌ Hata: Mevcut kullanıcı bulunamadı!</h2>");
        }
    });
});

// --- 6. SOCKET VE BAŞLAT ---
io.on('connection', (socket) => {
    socket.on('yeni_veri_geldi', (data) => { io.emit('ekrana_bas', data); });
});

const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Sunucu Aktif: http://172.20.10.14:${PORT}`);
});
