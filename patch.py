import json

def patch_interactive():
    with open(".agent/research/anova/anova-interactive.py", "r") as f:
        content = f.read()
        
    block = """
    async def start_spoofed_android_cook(self):
        \"\"\"Start a spoofed perfect Android 2-stage cook\"\"\"
        try:
            temp = float(input("Enter roasting temperature (°C): "))
            
            payload_dict = {
                "cookId": f"android-{self.generate_uuid()}",
                "cookerId": self.selected_device["id"],
                "cookableId": "AryI3nL7za8awq9B2eXe",
                "cookTitle": "",
                "type": "oven",
                "originSource": "android",
                "cookableType": "manual",
                "rackPosition": 3,
                "stages": [
                    {
                        "id": f"android-{self.generate_uuid()}",
                        "title": "",
                        "do": {
                            "type": "cook",
                            "fan": {
                                "speed": 100
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": False},
                                "rear": {"on": True}
                            },
                            "exhaustVent": {
                                "state": "closed"
                            },
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp
                                    }
                                }
                            },
                            "timer": {
                                "initial": 10,
                                "entry": {
                                    "conditions": {
                                        "and": {
                                            "nodes.temperatureBulbs.dry.current.celsius": {
                                                ">=": 10.0
                                            }
                                        }
                                    }
                                }
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
                        "entry": {
                            "conditions": {
                                "and": {
                                    "nodes.temperatureBulbs.dry.current.celsius": {
                                        ">=": 10.0
                                    }
                                }
                            }
                        }
                    },
                    {
                        "id": f"android-{self.generate_uuid()}",
                        "title": "",
                        "do": {
                            "type": "cook",
                            "fan": {
                                "speed": 100
                            },
                            "heatingElements": {
                                "top": {"on": False},
                                "bottom": {"on": False},
                                "rear": {"on": True}
                            },
                            "exhaustVent": {
                                "state": "closed"
                            },
                            "temperatureBulbs": {
                                "mode": "dry",
                                "dry": {
                                    "setpoint": {
                                        "celsius": temp
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
                                "and": {
                                    "nodes.temperatureBulbs.dry.current.celsius": {
                                        ">=": temp
                                    }
                                }
                            }
                        }
                    }
                ]
            }
            
            command = {
                "command": "CMD_APO_START",
                "payload": {
                    "id": self.selected_device["id"],
                    "payload": payload_dict,
                    "type": "CMD_APO_START"
                },
                "requestId": self.generate_uuid()
            }
            
            await self.send_command_and_wait_for_response(command)
            
        except Exception as e:
            print(f"❌ Error: {e}")
"""
    
    if "start_spoofed_android_cook" not in content:
        content = content.replace('print("0. Exit")', 'print("6. TEST PERFECT ANDROID SPOOF")\n            print("0. Exit")')
        content = content.replace('elif choice == "5":\n                await self.export_telemetry()', 'elif choice == "5":\n                await self.export_telemetry()\n            elif choice == "6":\n                await self.start_spoofed_android_cook()')
        
        # Insert the method before export_telemetry
        content = content.replace("async def export_telemetry", block + "\n    async def export_telemetry")
        
        with open(".agent/research/anova/anova-interactive.py", "w") as f:
            f.write(content)
        print("Patched interactive script.")

patch_interactive()
