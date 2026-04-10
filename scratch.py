import json
import uuid

def generate_uuid():
    return str(uuid.uuid4())

command = {
    "command": "CMD_APO_START",
    "payload": {
        "id": "device_id",
        "payload": {
            "stages": [
                {
                    "id": generate_uuid(),
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
                                    "celsius": 100
                                }
                            }
                        },
                        "steamGenerators": {
                            "mode": "relative-humidity",
                            "relativeHumidity": {
                                "setpoint": 0
                            }
                        },
                        "timer": {
                            "initial": 1800
                        }
                    },
                    "exit": {
                        "conditions": {
                            "and": {
                                "nodes.timer.mode": {
                                    "=": "completed"
                                }
                            }
                        }
                    },
                    "title": "",
                    "description": "",
                    "rackPosition": 3
                }
            ],
            "cookId": generate_uuid(),
            "cookerId": "device_id",
            "cookableId": "",
            "title": "",
            "type": "oven",
            "originSource": "api",
            "cookableType": "manual"
        },
        "type": "CMD_APO_START"
    },
    "requestId": generate_uuid()
}

print(json.dumps(command, indent=2))
