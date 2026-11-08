import time
import math
import requests
import warnings
import concurrent.futures
from urllib3.exceptions import InsecureRequestWarning
from pybit.unified_trading import HTTP
import config

# Fix for Windows SSL cert error "CERTIFICATE_VERIFY_FAILED" (requests library patching)
warnings.simplefilter('ignore', InsecureRequestWarning)
old_request = requests.Session.request
def new_request(*args, **kwargs):
    kwargs['verify'] = False
    return old_request(*args, **kwargs)
requests.Session.request = new_request
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    rsi_list = [None] * period
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        rsi_list.append(100.0)
    else:
        rs = avg_gain / avg_loss
        rsi_list.append(100 - (100 / (1 + rs)))
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi_list.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi_list.append(100 - (100 / (1 + rs)))
            
    return rsi_list

def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    ema_list = [None] * (period - 1)
    sma = sum(prices[:period]) / period
    ema_list.append(sma)
    
    multiplier = 2 / (period + 1)
    ema = sma
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
        ema_list.append(ema)
        
    return ema_list

def send_telegram_message(message_text):
    """
    Mengirimkan pesan teks murni ke ruangan chat Telegram Anda.
    """
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        # Jika pengguna belum memasukkan kuncinya, abaikan pengiriman.
        return
        
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message_text
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"⚠️ Gagal mengirim pesan: {e}")

def get_historical_data(symbol, interval, limit=210):
    """
    Mengambil data berdasarkan interval murni Binance dengan proteksi anti-block ISP.
    """
    base_urls = [
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com"
    ]
    
    data = None
    for base_url in base_urls:
        url = f"{base_url}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                break
        except requests.exceptions.RequestException:
            continue
            
    if data is None:
        return None, None
        
    try:
        # Ekstrak data 'Close price' dan 'Volume' menjadi list
        close_prices = [float(candle[4]) for candle in data]
        volumes = [float(candle[5]) for candle in data]
        return close_prices, volumes
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None, None

def main():
    print("🚀 Mulai Start: Mesin Radar Multi-Timeframe (Scalp, Day, Spot)...")
    print(f"📊 Mengawasi {len(config.SYMBOLS)} Koin secara Paralel.")
    
    # Simpan status posisi tiap koin, DIPISAH per Kategori Strategi
    # Status bisa berwujud: None, "LONG", "SHORT"
    positions = {s_name: {symbol: None for symbol in config.SYMBOLS} for s_name in config.STRATEGIES.keys()}
    
    while True:
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Memindai pasar di berbagai dimensi waktu...")
            
            # Mengurangi max_workers menjadi 5 untuk menghindari "Read timed out" API Binance
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Daftarkan penarikan data 40 koin dikali 3 timeframe = 120 task sekaligus
                future_to_job = {}
                for symbol in config.SYMBOLS:
                    for s_name, s_info in config.STRATEGIES.items():
                        fut = executor.submit(get_historical_data, symbol, s_info["interval"])
                        future_to_job[fut] = (symbol, s_name, s_info)
                
                for future in concurrent.futures.as_completed(future_to_job):
                    symbol, s_name, s_info = future_to_job[future]
                    try:
                        result = future.result()
                        if result == (None, None):
                            continue
                            
                        close_prices, volumes = result
                        
                        if close_prices and len(close_prices) > getattr(config, 'EMA_TREND', 50):
                            # 2. Menghitung Triple EMA, RSI, & Volume MA
                            last_close = close_prices[-1]
                            ema_fast = calculate_ema(close_prices, getattr(config, 'EMA_FAST', 5))
                            ema_slow = calculate_ema(close_prices, getattr(config, 'EMA_SLOW', 13))
                            ema_trend = calculate_ema(close_prices, getattr(config, 'EMA_TREND', 50))
                            rsi_data = calculate_rsi(close_prices, getattr(config, 'RSI_PERIOD', 14))
                            
                            if ema_fast and ema_slow and ema_trend and rsi_data:
                                
                                # Mengambil data terakhir untuk memvalidasi pemotongan & volume
                                curr_fast, prev_fast = ema_fast[-1], ema_fast[-2]
                                curr_slow, prev_slow = ema_slow[-1], ema_slow[-2]
                                curr_trend = ema_trend[-1]
                                curr_rsi = rsi_data[-1]
                                
                                # Volume Anomaly Logic
                                vol_ma_period = getattr(config, 'VOLUME_MA_PERIOD', 20)
                                avg_vol = sum(volumes[-vol_ma_period-1:-1]) / vol_ma_period # Rata-rata 20 lilin tertutup sebelumnya
                                curr_vol = volumes[-1]
                                vol_multiplier = getattr(config, 'VOLUME_SURGE_MULTIPLIER', 1.5)
                                is_volume_surge = curr_vol >= (avg_vol * vol_multiplier)
                                
                                # Taktik "Triple EMA Scalper" + RSI Safe Zone
                                is_fast_golden = (prev_fast <= prev_slow) and (curr_fast > curr_slow)
                                is_fast_death = (prev_fast >= prev_slow) and (curr_fast < curr_slow)
                                
                                rsi_max_buy = getattr(config, 'RSI_MAX_BUY', 65)
                                rsi_min_short = getattr(config, 'RSI_MIN_SHORT', 35)
                                
                                # Sinyal LONG: Golden Cross + EMA 13 > EMA 50 (Triple Gear Mutlak) + RSI AMAN + VOLUME PAUS
                                is_buy_long = is_fast_golden and (curr_slow > curr_trend) and (curr_rsi <= rsi_max_buy) and is_volume_surge
                                
                                # Eksekusi TAKE PROFIT / STOP LOSS Darurat jika tren berbalik murni
                                is_exit_long = is_fast_death
                                
                                curr_pos = positions[s_name][symbol]
                                
                                # 3A. Menganalisis Sinyal ENTRY BARU
                                if curr_pos is None:
                                    if is_buy_long:
                                        entry_price = last_close
                                        stop_loss = entry_price * s_info["stop_loss"]
                                        tp_1 = entry_price * s_info["tp_1"]
                                        tp_2 = entry_price * s_info["tp_2"]
                                        tp_max = entry_price * s_info["tp_max"]
                                        
                                        vol_pct = (curr_vol / avg_vol) * 100 if avg_vol > 0 else 0
                                        alasan = f"TRIPLE EMA CROSSOVER NAIK + RSI ({curr_rsi:.1f}) AMAN"
    
                                        text_log = (
                                            f"\n==============================================\n"
                                            f"🟢 {s_info['label']} | [ BUKA LONG 🚀 ] : {symbol} \n"
                                            f"==============================================\n"
                                            f"✨ Bukti Sinyal   : {alasan}\n"
                                            f"🛡️ Triple Gear    : EMA 13 > EMA 50 | RSI < {rsi_max_buy}\n"
                                            f"🐋 DETEKSI PAUS   : Lonjakan Volume {vol_pct:.0f}% dari rata-rata!\n"
                                            f"👉 MASUK SEKARANG : ${entry_price:,.4f}\n"
                                            f"📉 PASANG SL      : ${stop_loss:,.4f}\n"
                                            f"🎯 PASANG TP 1    : ${tp_1:,.4f} (Aman)\n"
                                            f"🎯 PASANG TP 2    : ${tp_2:,.4f} (Target)\n"
                                            f"🚀 PASANG TP MAX  : ${tp_max:,.4f} (Moon)\n"
                                            f"==============================================\n"
                                        )
                                        print(text_log)
                                        send_telegram_message(text_log)
                                        positions[s_name][symbol] = "LONG"
                                        
                                # 3B. Menganalisis Sinyal EXIT KEDADARATAN
                                elif curr_pos == "LONG" and is_exit_long:
                                    text_log = (
                                        f"\n==============================================\n"
                                        f"⚠️ {s_info['label']} | [ TUTUP LONG 🛡️ ] : {symbol}\n"
                                        f"==============================================\n"
                                        f"✨ Bukti Sinyal   : LONG MOMENTUM HILANG (DEATH CROSS)\n"
                                        f"💡 Info Tambahan  : Segera Amankan Profit/Cut Loss sebelum jatuh lebih parah!\n"
                                        f"👉 HARGA KELUAR   : ${last_close:,.4f}\n"
                                        f"==============================================\n"
                                    )
                                    print(text_log)
                                    send_telegram_message(text_log)
                                    positions[s_name][symbol] = None
                    
                    except Exception as e:
                        print(f"Error memproses {symbol} ({s_name}): {e}")
                
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            
        print("⏳ Selesai mengecek semua koin. Menunggu putaran berikutnya...")
        time.sleep(config.API_CHECK_INTERVAL)

if __name__ == "__main__":
    main()
