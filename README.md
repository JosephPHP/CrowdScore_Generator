# CrowdScore_Generator

# Requirements
- crowdstrike-falconpy
- tabulate (Diperlukan jika opsi tabel (-d) digunakan)

# Kredensial API
Diperlukan kunci API CrowdStrike Falcon dengan hak akses minimal:
- Incidents: read:incidents

# Instalasi dan Setup

1. Kloning Repositori:
   git clone https://github.com/JosephPHP/CrowdScore_Generator.git
   cd CrowdScore_Generator

2. Virtual Environment & Dependencies:
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -r requirements.txt
   
3. Perintah Penggunaan
   python3 crowdscore_simple.py -k <CLIENT_ID> -s <CLIENT_SECRET> [OPTIONS] 

# Option

-d, --show-data	Shows the data table display
-r, --reverse	Reverse the data table sort
-k FALCON_CLIENT_ID, --falcon_client_id FALCON_CLIENT_ID	Falcon Client ID
-s FALCON_CLIENT_SECRET, --falcon_client_secret FALCON_CLIENT_SECRET	Falcon Client Secret
