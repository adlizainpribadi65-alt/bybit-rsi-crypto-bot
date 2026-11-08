import os
from dotenv import load_dotenv

# Muat variabel environment dari file .env
load_dotenv()

# Konfigurasi Kredensial API Bybit
# Kosongkan nilainya kalau hanya mau simulasi baca data ticker.
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# Konfigurasi Notifikasi Telegram (Asisten HP)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Konfigurasi Trading Multi-Koin
# Ekspansi Brutal: 120 Koin (Volume Teratas + Altcoins Liar + Meme Coins)
SYMBOLS = [
    # Top Layer (Liquiditas Super, Biru)
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
    "TRXUSDT", "LTCUSDT", "BCHUSDT", "SHIBUSDT", "UNIUSDT", "ATOMUSDT", "XLMUSDT", "NEARUSDT", "APTUSDT", "ARBUSDT",
    "OPUSDT", "INJUSDT", "FILUSDT", "ICPUSDT", "VETUSDT", "AAVEUSDT", "LDOUSDT", "GALAUSDT", "SANDUSDT", "MANAUSDT",
    "FTMUSDT", "WLDUSDT", "TIAUSDT", "PEPEUSDT", "SUIUSDT", "SEIUSDT", "FETUSDT", "RUNEUSDT", "ALGOUSDT", "EGLDUSDT",
    
    # Mid Layer (Ganas di Pergerakan Harian, Metaverse, DeFi)
    "THETAUSDT", "AXSUSDT", "HBARUSDT", "QNTUSDT", "MKRUSDT", "STXUSDT", "CRVUSDT", "GRTUSDT", "SNXUSDT", "ARUSDT",
    "KASUSDT", "ORDIUSDT", "1000SATSUSDT", "BONKUSDT", "FLOKIUSDT", "WIFUSDT", "BOMEUSDT", "JUPUSDT", "PYTHUSDT", 
    "MANTAUSDT", "ALTUSDT", "DYMUSDT", "STRKUSDT", "PORTALUSDT", "PIXELUSDT", "XAIUSDT", "AEVOUSDT", "ETHFIUSDT",
    
    # Low Layer / New Listings / Layer 2 / AI (Volatility Super Liar)
    "ENAUSDT", "WUSDT", "TNSRUSDT", "GMXUSDT", "GNSUSDT", "MINAUSDT", "IMXUSDT", "PENDLEUSDT", "AGIXUSDT", "OCEANUSDT",
    "PHBUSDT", "CFXUSDT", "STPTUSDT", "ONDOUSDT", "ILVUSDT", "MAGICUSDT", "YGGUSDT", "BIGTIMEUSDT", "ACEUSDT", "NFPUSDT",
    "AIUSDT", "XVSUSDT", "CAKEUSDT", "BAKEUSDT", "1INCHUSDT", "COMPUSDT", "SUSHIUSDT", "ZRXUSDT", "UMAUSDT", "BALUSDT",
    "YFIUSDT", "JASMYUSDT", "KEYUSDT", "RSRUSDT", "NKNUSDT", "ONGUSDT", "ONTUSDT", "ZILUSDT", "IOSTUSDT", "CELRUSDT",
    "COTIUSDT", "REQUSDT", "CTSIUSDT", "DUSKUSDT", "LRCUSDT", "ENJUSDT", "CHZUSDT", "HOTUSDT", "RVNUSDT", "STORJUSDT"
]
# Konfigurasi Multi-Timeframe Trading Khusus SPOT
STRATEGIES = {
    "SPOT_KILAT": {
        "interval": "15m",
        "stop_loss": 0.97,    # -3% (Cut Loss)
        "tp_1": 1.015,        # +1.5% (Aman)
        "tp_2": 1.03,         # +3% (Target)
        "tp_max": 1.05,       # +5% (Moon)
        "label": "⚡ SPOT KILAT (15M)"
    },
    "SPOT_CEPAT": {
        "interval": "1h",
        "stop_loss": 0.95,    # -5% (Cut Loss)
        "tp_1": 1.03,         # +3% (Aman)
        "tp_2": 1.06,         # +6% (Target)
        "tp_max": 1.12,       # +12% (Moon)
        "label": "💎 SPOT CEPAT (1H)"
    },
    "SPOT_SANTAI": {
        "interval": "4h",
        "stop_loss": 0.90,    # -10% (Cut Loss)
        "tp_1": 1.08,         # +8%
        "tp_2": 1.15,         # +15%
        "tp_max": 1.30,       # +30%
        "label": "💎 SPOT SANTAI (4H)"
    }
}

# Konfigurasi Strategi "Pure EMA Scalper" (Triple Layer)
EMA_FAST = 5        # Bereaksi kilat mengikuti harga
EMA_SLOW = 13       # Garis sinyal penyeimbang
EMA_TREND = 34      # Menutup filter jadi lebih sensitif (mengikuti tren jangka menengah)

# Konfigurasi RSI (Rem Mutlak - Ruang Tumbuh Luas)
RSI_PERIOD = 14
RSI_MAX_BUY = 65    # Sedikit dilonggarkan agar tidak kehilangan momentum saat tren kuat
RSI_MIN_SHORT = 40  # Sangat Ketat: Short mutlak dilarang jika RSI sudah sentuh 40 (Oversold)

# Konfigurasi Detektor Volume Anomaly (Sidik Jari Paus)
VOLUME_MA_PERIOD = 20
# Diturunkan ke 1.15x agar sinyal lebih sering muncul saat ada sedikit dorongan volume
VOLUME_SURGE_MULTIPLIER = 1.15  

# Pengaturan tambahan untuk safety
ORDER_QTY = 0.001 # Minimum size BTC Bybit
API_CHECK_INTERVAL = 15 # Ditegaskan ke 15 detik agar jaring 120 koin tidak diblokir limit Binance Server
