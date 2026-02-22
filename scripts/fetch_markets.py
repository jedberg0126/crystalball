import sys
import os

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from difflib import SequenceMatcher

from cb_models import Article


# -----------------------------
# DATABASE SETUP
# -----------------------------

engine = create_engine("sqlite:///crystalball.db")
SessionLocal = sessionmaker(bind=engine)


# -----------------------------
# FETCH REAL MARKETS
# -----------------------------

import requests

def fetch_real_markets():
    markets = []

    headers = {"User-Agent": "CRYSTALBALL/1.0"}

    # --- Polymarket ---
    try:
        r = requests.get("https://api.polymarket.com/markets", headers=headers, timeout=10)
        if r.status_code == 200 and r.text.strip():
            for m in r.json():
                if m.get("probability") is not None:
                    markets.append({
                        "name": m["question"],
                        "probability": float(m["probability"]),
                        "section": "politics"
                    })
        else:
            print("Polymarket returned empty or invalid response")
    except Exception as e:
        print("Polymarket error:", e)

    # --- Kalshi ---
    try:
        r = requests.get(
            "https://trading-api.kalshi.com/trade-api/v2/markets",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200 and r.text.strip():
            for m in r.json().get("markets", []):
                if m.get("yes_bid") is not None:
                    markets.append({
                        "name": m["title"],
                        "probability": float(m["yes_bid"]) / 100,
                        "section": "politics"
                    })
        else:
            print("Kalshi returned empty or invalid response")
    except Exception as e:
        print("Kalshi error:", e)

    # --- PredictIt ---
    try:
        r = requests.get(
            "https://www.predictit.org/api/marketdata/all/",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200 and r.text.strip():
            for market in r.json().get("markets", []):
                for c in market.get("contracts", []):
                    if c.get("lastTradePrice") is not None:
                        markets.append({
                            "name": c["name"],
                            "probability": float(c["lastTradePrice"]),
                            "section": "politics"
                        })
        else:
            print("PredictIt returned empty or invalid response")
    except Exception as e:
        print("PredictIt error:", e)

    return markets



# -----------------------------
# NORMALIZE + AVERAGE
# -----------------------------

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def average_markets(markets, threshold=0.85):
    groups = []

    for m in markets:
        matched = False

        for g in groups:
            if similarity(m["name"].lower(), g["name"].lower()) >= threshold:
                g["probs"].append(m["probability"])
                matched = True
                break

        if not matched:
            groups.append({
                "name": m["name"],
                "section": m["section"],
                "probs": [m["probability"]]
            })

    averaged = []

    for g in groups:
        avg_prob = sum(g["probs"]) / len(g["probs"])

        averaged.append({
            "name": g["name"],
            "probability": round(avg_prob, 4),
            "section": g["section"]
        })

    return averaged


    for m in markets:
        key = normalize_question(m["name"])

        if key not in grouped:
            grouped[key] = {
                "name": m["name"],
                "section": m["section"],
                "probs": []
            }

        grouped[key]["probs"].append(m["probability"])

    averaged = []

    for g in grouped.values():
        avg_prob = sum(g["probs"]) / len(g["probs"])

        averaged.append({
            "name": g["name"],
            "probability": round(avg_prob, 4),
            "section": g["section"]
        })

    return averaged


# -----------------------------
# ARTICLE LOGIC
# -----------------------------

def generate_article(name, probability, label):
    paragraph_1 = (
        f"{name} is currently assessed as {label.lower()}, "
        f"with an estimated probability of {int(probability * 100)}%. "
        f"This reflects the collective expectations of prediction markets."
    )

    paragraph_2 = (
        "Recent movement in the odds suggests changing sentiment, potentially "
        "driven by new information, shifting public opinion, or emerging trends "
        "related to the event."
    )

    return paragraph_1 + "\n\n" + paragraph_2


# -----------------------------
# UPDATE LOOP
# -----------------------------

def update_markets():
    session = SessionLocal()

    raw_markets = fetch_real_markets()
    markets = average_markets(raw_markets)

    for m in markets:
        prob = m["probability"]
        label = None

        if prob >= 0.60:
            label = "LIKELY"

        article = session.query(Article).filter_by(headline=m["name"]).first()

        if not article:
            if label:
                new_article = Article(
                    headline=f"{label}: {m['name']}",
                    label=label,
                    section=m["section"],
                    probability=prob,
                    content=generate_article(m["name"], prob, label),
                    last_updated=datetime.utcnow()
                )
                session.add(new_article)
        else:
            delta = prob - article.probability

            if delta >= 0.125:
                article.headline = f"TRENDING: {m['name']}?"
                article.label = "TRENDING"

            article.probability = prob
            article.last_updated = datetime.utcnow()

    session.commit()
    session.close()

    print(f"[{datetime.now()}] CRYSTALBALL updated")


# -----------------------------
# SCHEDULER
# -----------------------------

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_markets, "interval", minutes=5)
    scheduler.start()

    print("CRYSTALBALL live updater running. Ctrl+C to stop.")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
