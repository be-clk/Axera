"""
TUA AXERA - Backend API Server
Flask ile çalışır. Frontend'e hava verisi, analiz ve log sağlar.
Kurulum: pip install flask flask-cors requests
Çalıştır: python backend.py
"""

import csv
import math
import os
from datetime import datetime, timedelta, timezone
import json

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = "00f3e5d17ea4bfe41281088702aee3fb"

def fetch_noaa_data():
    """NOAA açık API'lerinden Kp, S ve R ölçeklerini çeker."""
    result = {
        "kp_index": 2.0,
        "g_scale": 0,
        "s_scale": 1,
        "r_scale": 1,
        "timestamp": ""
    }

    # ── 1. Kp Index (G-Ölçeği buradan türetilir) ──
    try:
        res = requests.get(
            "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
            timeout=10
        )
        res.raise_for_status()
        data = res.json()
        latest = data[-1]
        kp = float(latest.get("kp_index", 2.0))
        result["kp_index"]  = kp
        result["g_scale"]   = max(0, int(kp) - 4) if kp >= 5 else 0
        result["timestamp"] = latest.get("time_tag", "")
    except Exception as e:
        print(f"NOAA Kp Hatası: {e}")

    # ── 2. S-Ölçeği (Solar Radyasyon Fırtınası) ──
    try:
        res = requests.get(
            "https://services.swpc.noaa.gov/products/noaa-scales.json",
            timeout=10
        )
        res.raise_for_status()
        scales = res.json()
        # scales["0"] = güncel değerler
        s_val = int(scales["0"]["S"]["Scale"])
        r_val = int(scales["0"]["R"]["Scale"])
        result["s_scale"] = s_val if s_val >= 1 else 1
        result["r_scale"] = r_val if r_val >= 1 else 1
    except Exception as e:
        print(f"NOAA S/R Ölçeği Hatası: {e}")

    return result



LAUNCH_SITES = {
    "Kismaayo (Somali - TUA)": {"lat": -0.35, "lon": 42.54, "desc": "Ana Ekvator Ussu", "rakim": 15},
    "Kennedy Space Center (ABD)": {"lat": 28.57, "lon": -80.64, "desc": "Atlantik Kiyisi", "rakim": 3},
    "Kourou (Fransiz Guyanasi)": {"lat": 5.23, "lon": -52.76, "desc": "ESA Ana Ussu", "rakim": 14},
    "Hambantota (Sri Lanka)": {"lat": 6.12, "lon": 81.12, "desc": "Hint Okyanusu", "rakim": 20},
}

ENVANTER = {
    "Yorungesel Firlatma (Roket)": {
        "Falcon-9 (Block 5)": 34,
    },
    "Gorev Yuku (Payload)": {
        "Astra-5 (Haberlesme Uydusu)": 32,
    },
}

LOG_FILE = "axera_firlatma_loglari.csv"

def get_site_local_hour(tz_sec):
    utc_now = datetime.now(timezone.utc)
    return (utc_now + timedelta(seconds=tz_sec)).hour

def detect_theme(hour_value):
    if 6 <= hour_value < 17: return "gunduz"
    if 17 <= hour_value < 20: return "aksam"
    return "gece"

def save_to_log(site, model, status, hatalar):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Tarih", "Liman", "Model", "Durum", "Nedenler"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            site, model, status,
            " | ".join(hatalar) if hatalar else "Basarili",
        ])

@app.route("/api/sites", methods=["GET"])
def get_sites():
    return jsonify({"sites": list(LAUNCH_SITES.keys())})

@app.route("/api/envanter", methods=["GET"])
def get_envanter():
    return jsonify({"envanter": ENVANTER})

@app.route("/api/weather", methods=["GET"])
def get_weather():
    site_name = request.args.get("site")
    if not site_name or site_name not in LAUNCH_SITES:
        return jsonify({"error": "Gecersiz site"}), 400
    site = LAUNCH_SITES[site_name]
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={site['lat']}&lon={site['lon']}&appid={API_KEY}&units=metric&lang=tr"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        tz_offset = data.get("timezone", 0)
        local_hour = get_site_local_hour(tz_offset)
        geo_speed = round(1670 * math.cos(math.radians(site["lat"])), 1)
        return jsonify({
            "site": site_name, "desc": site["desc"], "lat": site["lat"],
            "rakim": site["rakim"], "geo_speed": geo_speed,
            "theme": detect_theme(local_hour), "local_hour": local_hour,
            "weather": {
                "wind_kt": round(data["wind"]["speed"] * 1.94384, 2),
                "wind_deg": int(data["wind"].get("deg", 0)),
                "temp_c": round(data["main"]["temp"], 1),
                "visibility_km": round(data.get("visibility", 10000) / 1000, 1),
                "description": data["weather"][0]["description"].capitalize(),
                "clouds_pct": data["clouds"]["all"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
            }
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

# YENİ ENDPOINT: UZAY HAVASI VERİSİNİ FRONTEND'E YOLLAR
@app.route("/api/space_weather", methods=["GET"])
def get_space_weather():
    data = fetch_noaa_data()
    return jsonify({
        "success":       True,
        "kp_index":      data["kp_index"],
        "g_scale":       data["g_scale"],
        "s_scale":       data["s_scale"],
        "r_scale":       data["r_scale"],
        "lightning_dist": 35.0,
        "last_lightning": 60,
        "electric_field": 300,
        "timestamp":     data["timestamp"]
    })

@app.route("/api/analyze", methods=["POST"])
def analyze_launch():
    body = request.get_json()
    hatalar = []

    site_name = body.get("site", "")
    kategori = body.get("kategori", "")
    model = body.get("model", "")
    weather = body.get("weather", {})
    
    # Payload'dan NOAA verisini doğrudan okur
    kp_val = float(body.get("kp_index", 2))
    g_scale = int(body.get("geomagnetic_g_scale", 1))

    # 1. Hava limitleri
    limit = ENVANTER.get(kategori, {}).get(model, 35)
    if weather.get("wind_kt", 0) > limit:
        hatalar.append(f"Yuksek ruzgar ({weather['wind_kt']} kt > {limit} kt)")
    if weather.get("visibility_km", 10) < 6.0:
        hatalar.append("Dusuk gorus mesafesi (<6 km)")
    if weather.get("clouds_pct", 0) > 85:
        hatalar.append("Kritik bulut kalinligi (>%85)")

    # 2. Atmosferik ve Uzay Havası Riskleri
    if kp_val >= 7.0:
        hatalar.append(f"KRİTİK UZAY HAVASI: NOAA Verisi Kp {kp_val} (İyonosferik Risk)")
    if kp_val >= 5:
        if f"KRİTİK UZAY HAVASI" not in str(hatalar):
            hatalar.append(f"Jeomanyetik firtina riski (Kp: {kp_val})")
    
    if body.get("cumulus_risk"):
        hatalar.append("Ucus hattinda kumulus bulutu")
    if float(body.get("lightning_dist", 25)) < 19.0:
        hatalar.append("Simsek menzil ihlali (<19 km)")
    if float(body.get("electric_field", 500)) > 1500.0:
        hatalar.append("Yuksek yuzey elektrik alani")

    # 3. Yakıt
    if body.get("fuel_status", 100) < 98.0:
        hatalar.append("Yakit doluluk orani yetersiz")
    if body.get("fuel_temp", -185) > -183:
        hatalar.append("Kritik yakit sicakligi")

    # 4. Güvenlik
    if not body.get("range_clear", True):
        hatalar.append("Menzil ihlali")
    if not body.get("telemetry_ok", True):
        hatalar.append("Telemetri hazir degil")
    if not body.get("pad_ready", True):
        hatalar.append("Rampa kilitleri acilmadi")

    go = len(hatalar) == 0
    status = "GO" if go else "SCRUB"
    save_to_log(site_name, model, status, hatalar)

    return jsonify({
        "status": status, "go": go, "errors": hatalar,
        "fuel_cost": int(body.get("fuel_status", 100) * 12500),
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    if not os.path.exists(LOG_FILE): return jsonify({"logs": []})
    logs = []
    with open(LOG_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader: logs.append(row)
    return jsonify({"logs": list(reversed(logs[-50:]))})

if __name__ == "__main__":
    print("=" * 50)
    print("  TUA AXERA Backend API Sunucusu (NOAA Aktif)")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)