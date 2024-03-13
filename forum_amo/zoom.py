"""
Integração com a API do Zoom
"""
import requests

URL = "https://zoom.us/oauth/token"

data = {
    "eventType": "AAS_PORTAL_START",
    "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"},
}
params = {"grant_type": "account_credentials", "account_id": "Zn2as7GaRGiLdES4eWC5XQ"}

a = requests.post(
    URL,
    params=params,
    auth=("O6BqSdonRFaY3NUnrcaGEA", "6HD1RdjAeKEfCB00k8TAOM8HQ9QGYBKw"),
)

b = a.json()

token = b["access_token"]

payload = {
    "topic": "Monitoria Acadêmica",
    "type": 2,  # 1 for instant meeting, 2 for scheduled meeting
    "start_time": "2024-01-26T12:16:43Z",
    "duration": 60,
    "settings": {
        "host_video": True,
        "participant_video": True,
        "join_before_host": True,
        "mute_upon_entry": True,
        "alternative_hosts_email_notification": False,
    },
}
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}


def create_meeting():
    """
    Função que retorna link do meeting
    """
    aba = requests.post(
        "https://api.zoom.us/v2/users/me/meetings", headers=headers, json=payload
    )
    aba = aba.json()
    return aba["join_url"]
