import os
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def main():
    if not TOKEN:
        print("Telegram token is not configured.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    response = requests.get(url, timeout=15)
    print(response.json())

if __name__ == "__main__":
    main()
