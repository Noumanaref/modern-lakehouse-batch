import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
FMP_KEY = os.environ["FMP_API_KEY"]


def fetch_profile(symbol="AAPL"):
    url = "https://financialmodelingprep.com/stable/profile"
    params = {"symbol": symbol, "apikey": FMP_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


call_1 = fetch_profile()
time.sleep(5)
call_2 = fetch_profile()

print("Identical?", call_1 == call_2)

if call_1 != call_2:
    rec1, rec2 = call_1[0], call_2[0]
    for key in rec1:
        if rec1.get(key) != rec2.get(key):
            print(f"DIFFERS: {key} → {rec1.get(key)}  vs  {rec2.get(key)}")