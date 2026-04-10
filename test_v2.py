import json
import uuid

def gen_id():
    return f"android-{str(uuid.uuid4())}"

temp_celsius = 100.0

stage = {
    "id": gen_id(),
    "title": "",
    "do": {
        "type": "cook",
        "fan": {
            "speed": 100
        },
        "heatingElements": {
            "top": {"on": False},
            "bottom": {"on": True},
            "rear": {"on": True}
        },
        "exhaustVent": {
            "state": "closed"
        },
        "temperatureBulbs": {
            "mode": "dry",
            "dry": {
                "setpoint": {
                  "celsius": temp_celsius
                }
            }
        }
    },
    "exit": {
        "conditions": {
            "and": {}
        }
    },
    "entry": {
        "conditions": {
            "and": {}
        }
    }
}

payload = {
    "cookId": gen_id(),
    "cookerId": "replace_me",
    "cookableId": "AryI3nL7za8awq9B2eXe",
    "cookTitle": "",
    "type": "oven",
    "originSource": "android",
    "cookableType": "manual",
    "rackPosition": 3,
    "stages": [stage]
}

print(json.dumps(payload, indent=2))
