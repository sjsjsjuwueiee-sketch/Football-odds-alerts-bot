import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
ODDS_URL = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"

previous_odds = {}


def send_message(message):
    if not TOKEN or not CHAT_ID:
        print("Missing Telegram configuration.")
        return

    try:
        response = requests.post(
            TELEGRAM_URL,
            data={"chat_id": CHAT_ID, "text": message},
            timeout=20
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print("Telegram delivery failed:", error)


def get_odds():
    if not ODDS_API_KEY:
        print("Missing ODDS_API_KEY secret.")
        return []

    try:
        response = requests.get(
            ODDS_URL,
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "uk,eu",
                "markets": "h2h",
                "oddsFormat": "decimal"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Odds API error:", error)
        return []


def scan_matches():
    matches = get_odds()

    for match in matches:
        home = match.get("home_team", "Home")
        away = match.get("away_team", "Away")
        commence = match.get("commence_time", "")

        for bookmaker in match.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") != "h2h":
                    continue

                for outcome in market.get("outcomes", []):
                    name = outcome.get("name", "")
                    odds = outcome.get("price")

                    if not isinstance(odds, (int, float)):
                        continue

                    key = f"{match.get('id')}:{bookmaker.get('key')}:{name}"
                    old = previous_odds.get(key)

                    previous_odds[key] = odds

                    if old and odds < old * 0.95:
                        drop = (old - odds) / old * 100

                        message = (
                            "🚨 ODDS MOVEMENT ALERT\n\n"
                            f"⚽ {home} vs {away}\n"
                            f"🗓️ {commence}\n"
                            f"🏢 Bookmaker: {bookmaker.get('title', 'Unknown')}\n"
                            f"🎯 Outcome: {name}\n"
                            f"📉 Previous odds: {old:.2f}\n"
                            f"📉 Current odds: {odds:.2f}\n"
                            f"📊 Drop: {drop:.1f}%\n\n"
                            "⚠️ Signal to investigate, not a guaranteed bet. "
                            "Odds movement alone does not reveal betting volume "
                            "or prove match manipulation."
                        )
                        send_message(message)


def main():
    send_message(
        "✅ Football Alert Mauritius started.\n"
        "Monitoring available football odds every 5 minutes."
    )

    while True:
        scan_matches()
        time.sleep(300)


if __name__ == "__main__":
    main()
