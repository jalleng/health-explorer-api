import json
import os
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv()

SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")
BASE_URL = "https://chronicdata.cdc.gov/resource/swc5-untb.json"
OUTPUT_PATH = os.path.join("data", "wa_health.json")


def fetch_wa_health_data():
    params = {
        "stateabbr": "WA",
        "$limit": 1000,
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"

    headers = {}
    if SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = SOCRATA_APP_TOKEN

    print("Fetching WA health data from CDC PLACES API...")
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        records = json.loads(response.read().decode())

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Saved {len(records)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    fetch_wa_health_data()
