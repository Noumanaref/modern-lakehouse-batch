import os
import time
import json
import boto3
import requests
from datetime import date
from dotenv import load_dotenv
from canonical_hash import canonical_hash


load_dotenv()
FMP_KEY = os.environ["FMP_API_KEY"]
S3_BUCKET = os.environ["S3_RAW_BUCKET"]


TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# we are excluding the changing fields from this source because this will be our descriptive data.
EXCLUDE_KEYS = {
    "price", "volume", "marketCap", "beta",
    "change", "changePercentage", "averageVolume", "lastDividend", "range",
}


RATE_LIMIT_DELAY_SECONDS = 0.5
MAX_RETRIES = 4

s3 = boto3.client("s3")

#  Fetch, with retry + exponential backoff 
def fetch_profile(symbol: str) -> dict:
    url = "https://financialmodelingprep.com/stable/profile"
    params = {"symbol": symbol, "apikey": FMP_KEY}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            print(f"Request failed for {symbol} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise


# Write one record to S3, content-hash idempotent 
def write_record_to_s3(record: dict, dt: str) -> bool:
    file_hash = canonical_hash(record, EXCLUDE_KEYS)
    key = f"landing_zone/fmp/dt={dt}/{file_hash}.json"

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
        print(f"Fetching profile for -> {symbol}")
        data = fetch_profile(symbol)   # FMP returns a list with one record
        record = data[0]

        file_already_existed = write_record_to_s3(record, today)

        if file_already_existed:
            already_existed_count += 1
        else:
            new_file_count += 1

        time.sleep(RATE_LIMIT_DELAY_SECONDS)

    print(f"\nDone. New files: {new_file_count}, already existed (no-op): {already_existed_count}")


if __name__ == "__main__":
    run()