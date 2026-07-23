import json
import os
import urllib.parse
import urllib.request

from dotenv import load_dotenv

from config import DATA_PATH

load_dotenv()

SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN")
BASE_URL = "https://chronicdata.cdc.gov/resource/swc5-untb.json"
REQUEST_TIMEOUT_SECONDS = 30


def fetch_wa_health_data():
    params = {
        "$limit": 2000,
        "$select": "stateabbr,statedesc,locationname,category,short_question_text,data_value,totalpopulation,year",
        "$where": "stateabbr='WA' AND data_value_type='Crude prevalence'",
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    print(f"Fetching data from URL: {url}")

    headers = {}
    if SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = SOCRATA_APP_TOKEN

    print("Fetching WA health data from CDC PLACES API...")
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        records = json.loads(response.read().decode())

    if not isinstance(records, list):
        raise ValueError(
            f"Expected a list of records from the Socrata API, got {type(records).__name__}: {records}"
        )

    if len(records) == params["$limit"]:
        print(
            f"Warning: received exactly the $limit of {params['$limit']} records. "
            "There may be more data available than was fetched."
        )

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Saved {len(records)} records to {DATA_PATH}")


if __name__ == "__main__":
    fetch_wa_health_data()
