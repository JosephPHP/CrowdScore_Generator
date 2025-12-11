"""Generate Raw Data Crowdscore dari Crowdstrike (Bisa diatur mau brp hari rangenya)
"""
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime, timedelta
import csv
import tabulate
from falconpy import Incidents

def connect_api(key: str, secret: str, base: str):
    return Incidents(client_id=key, client_secret=secret, base_url='auto')


def consume_command_line():
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-t", "--time",
                        dest="time_window",
                        help="Number of days of history to retrieve (Default: 30)",
                        required=False,
                        default=30,
                        type=int
                        )
    
    req = parser.add_argument_group("required arguments")
    req.add_argument("-k", "--falcon_client_id", help="CrowdStrike Client ID", required=True)
    req.add_argument("-s", "--falcon_client_secret", help="CrowdStrike Client Secret", required=True)

    return parser.parse_args()


def get_crowdscore_data(client_id: str, client_secret: str, base_url: str, time_window: int):
    incidents_api = connect_api(client_id, client_secret, base_url)
    
    ts_range = (datetime.now() + timedelta(days=-time_window)).strftime("%Y-%m-%dT%H:%M:%SZ") 
    
    all_scores = []
    offset = 0
    limit = 250

    while True:
        returned = incidents_api.crowdscore(
            sort="timestamp.desc",
            filter=f"timestamp:>='{ts_range}'",
            limit=limit,
            offset=offset
        )

        if returned["status_code"] != 200:
            raise SystemExit(f"Unable to retrieve CrowdScores. Status: {returned['status_code']}")

        resources = returned["body"]["resources"]
        all_scores.extend(resources)

        if len(resources) < limit or len(resources) == 0:
            break

        offset += limit
        
    return {"status_code": 200, "body": {"resources": all_scores}}


def export_csv(dataset: list, filename: str = "crowdscore_data.csv"):
    if not dataset:
        print("Data Kosong")
        return

    fieldnames = ["timestamp", "score"]

    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in dataset:
                clean_row = {
                    "timestamp": row.get("timestamp"),
                    "score": row.get("score"),
                }
                writer.writerow(clean_row)

        print(f"\n[Success] Data telah disimpan ke file: {filename}")
    except Exception as e:
        print(f"\n[FAIL] Error menyimpan Data : {e}")


def format_data_table(crowdscore_lookup: list):
    score_data = []
    
    for score in crowdscore_lookup:
        score_data.append({
            "timestamp": f"\t\t{score['timestamp']}",
            "score": score['score']
        })

    score_headers = {
        "timestamp": "Time",
        "score": "CrowdScore"
    }
    return score_data, score_headers


def display_data_table(dataset: list):
    scores, headers = format_data_table(dataset)
    tabulate.PRESERVE_WHITESPACE = True
    data_table = tabulate.tabulate(scores, headers)
    data_table = data_table.replace(
        "--------------------------",
        "\t\t--------------------------"
        )
    print(f"\n\t\t{data_table}")
    print(f"\n\t\t{len(dataset)} scores returned.\n")


def display_crowdscores(arguments: ArgumentParser):
    
    current_crowdscore_lookup = get_crowdscore_data(arguments.falcon_client_id,
                                                    arguments.falcon_client_secret,
                                                    'auto', 
                                                    arguments.time_window
                                                    )
    
    raw_scores = current_crowdscore_lookup["body"]["resources"]

     display_data_table(raw_scores)

    export_csv(raw_scores)

args = consume_command_line()

display_crowdscores(args)
