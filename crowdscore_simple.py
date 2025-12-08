"""Generate Raw Data Crowdscore dari Crowdstrike (Bisa diatur mau brp hari rangenya)
"""
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime, timedelta
import csv
import tabulate 
from falconpy import Incidents

def connect_api(key: str, secret: str, base: str):
    """Return a connected instance of the Incidents Service Class."""
    return Incidents(client_id=key, client_secret=secret, base_url=base)


def consume_command_line():
    """Ingest and parse any provided command line arguments."""
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-d", "--show-data",
                        help="Shows the data table display (Terminal Output)",
                        required=False,
                        action="store_true",
                        dest="show_data"
                        )
    parser.add_argument("-r", "--reverse",
                        help="Reverse the data table sort",
                        required=False,
                        action="store_true"
                        )
    parser.add_argument("-b", "--base-url",
                        dest="base_url",
                        help="CrowdStrike cloud region. (auto or usgov1, Default: auto)",
                        required=False,
                        default="auto"
                        )
    req = parser.add_argument_group("required arguments")
    req.add_argument("-k", "--falcon_client_id", help="CrowdStrike Client ID", required=True)
    req.add_argument("-s", "--falcon_client_secret", help="CrowdStrike Client Secret", required=True)

    return parser.parse_args()


def get_crowdscore_data(client_id: str, client_secret: str, base_url: str):
    """Retrieve the CrowdScore dataset using the Incidents Service Class via Paging (7 days)."""
    
    incidents_api = connect_api(client_id, client_secret, base_url)
    
    # Buatt ganti Rangenya (Next mungkin bisa dibikinin syntax biar gantinya gausah dari raw file)
    ts_range = (datetime.now() + timedelta(days=-7)).strftime("%Y-%m-%dT%H:%M:%SZ") 
    
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


def export_csv(dataset: list, filename: str = "crowdscore_raw_data.csv"):
    """Export the raw CrowdScore 10-minute data to a clean CSV file."""
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
        print(f"\n[FAIL] Terjadi error saat menulis CSV: {e}")


def format_data_table(crowdscore_lookup: list, do_reverse: bool):
    """Format the values in our data table (Dihapus kode warna)."""
    score_data = []
    
    for score in crowdscore_lookup:
        score_data.append({
            "timestamp": f"\t\t{score['timestamp']}",
            "score": score['score'] 
        })
    if do_reverse:
        score_data.reverse()

    score_headers = {
        "timestamp": "Time",
        "score": "CrowdScore"
    }
    return score_data, score_headers


def display_data_table(dataset: list, reverse: bool):
    """Display our data table."""

    scores, headers = format_data_table(dataset, reverse)
    tabulate.PRESERVE_WHITESPACE = True
    data_table = tabulate.tabulate(scores, headers)
    data_table = data_table.replace(
        "--------------------------",
        "\t\t--------------------------"
        )
    print(f"\n\t\t{data_table}")
    print(f"\n\t\t{len(dataset)} scores returned.\n")


def display_crowdscores(arguments: ArgumentParser):
    """Execute main routine: grab data, export CSV, and optionally display table."""
    
    current_crowdscore_lookup = get_crowdscore_data(arguments.falcon_client_id,
                                                    arguments.falcon_client_secret,
                                                    arguments.base_url
                                                    )
    
    raw_scores = current_crowdscore_lookup["body"]["resources"]

    if arguments.show_data:
        display_data_table(raw_scores, arguments.reverse)

    export_csv(raw_scores)

args = consume_command_line()

# Run the main routine
display_crowdscores(args)
