import os
import time
import json
import boto3
import requests
from datetime import date
from dotenv import load_dotenv
from canonical_hash import canonical_hash

load_dotenv()  # reads .env from the current or parent directory into os.environ


TWELVE_DATA_KEY = os.environ["TWELVE_DATA_API_KEY"]
S3_BUCKET = os.environ["S3_RAW_BUCKET"]

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# Twelve Data's /time_series response has no noise/envelope fields to strip.
EXCLUDE_KEYS = set()

RATE_LIMIT_DELAY_SECONDS = 0.5  # Twelve Data allows 8 req/sec; this keeps us well under that
MAX_RETRIES = 4

s3 = boto3.client("s3")


#  Fetch - with retry , exponential backoff 
def fetch_prices(symbol: str) -> dict:
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": 5,
        "apikey": TWELVE_DATA_KEY,
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s
            print(f"Request failed for {symbol} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise  # failed


# Write one record to S3, content-hash idempotent-
def write_record_to_s3(record: dict, dt: str) -> bool:
    file_hash = canonical_hash(record, EXCLUDE_KEYS)
    key = f"landing_zone/twelvedata/dt={dt}/{file_hash}.json"

    existing = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=key, MaxKeys=1)
    file_already_existed = existing.get("KeyCount", 0) > 0

    if not file_already_existed:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(record).encode("utf-8"),
            ContentType="application/json",
        )
        return file_already_existed



def run():
    today = date.today().isoformat()
    new_file_count = 0
    already_existed_count = 0

    for symbol in TICKERS:
        print(f"Fetching {symbol}...")
        data = fetch_prices(symbol)

        for value_record in data["values"]:
            record = {"symbol": symbol, **value_record}
            file_already_existed = write_record_to_s3(record, today)

            if file_already_existed:
                already_existed_count += 1
            else:
                new_file_count += 1

        time.sleep(RATE_LIMIT_DELAY_SECONDS)

    print(f"\nDone. New files: {new_file_count}, already existed: {already_existed_count}")


if __name__ == "__main__":
    run()