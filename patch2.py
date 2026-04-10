import json

def patch_interactive():
    with open(".agent/research/anova/anova-interactive.py", "r") as f:
        content = f.read()
        
    block = """
    async def start_ultra_spoof(self):
        \"\"\"Start a spoofed perfect Android 2-stage cook EXACTLY mapped to JSON log\"\"\"
        try:
            payload_dict = {
                "cookId": f"android-{self.generate_uuid()}",
                "cookableId": "",
                "cookableType": "manual",
                "cookTitle": "",
                "originSource": "android",
                "rackPosition": 3,
                "stages": [
                    {
                        "do": {
                            "heatingElements": {"top": {"on": False}, "bottom": {"on": False}, "rear": {"on": True}},
                            "steamGenerators": {"mode": "relative-humidity", "relativeHumidity": {"setpoint": 100}},
                            "temperatureBulbs": {"mode": "wet", "wet": {"setpoint": {"celsius": 54.44}}},
                            "fan": {"speed": 100},
                            "timer": {"initial": 300},
                            "exhaustVent": {"state": "closed"},
                            "type": "cook"
                        },
                        "id": f"android-{self.generate_uuid()}",
                        "exit": {"conditions": {"and": {"nodes.timer.mode": {"=": "completed"}}}},
                        "title": ""
                    },
                    {
                        "title": "",
                        "do": {
                            "fan": {"speed": 100},
                            "steamGenerators": {"relativeHumidity": {"setpoint": 100}, "mode": "relative-humidity"},
                            "heatingElements": {"bottom": {"on": False}, "rear": {"on": True}, "top": {"on": False}},
                            "type": "cook",
                            "exhaustVent": {"state": "closed"},
                            "temperatureBulbs": {"mode": "wet", "wet": {"setpoint": {"celsius": 54.44}}}
                        },
                        "entry": {"conditions": {"and": {"nodes.temperatureBulbs.wet.current.celsius": {">=": 54.44}}}},
                        "exit": {"conditions": {"and": {}}},
                        "id": f"android-{self.generate_uuid()}"
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
    
    if "start_ultra_spoof" not in content:
        content = content.replace('print("0. Exit")', 'print("7. TEST ULTRA SPOOF (EXACT MATCH)")\n            print("0. Exit")')
        content = content.replace('elif choice == "6":\n                await self.start_spoofed_android_cook()', 'elif choice == "6":\n                await self.start_spoofed_android_cook()\n            elif choice == "7":\n                await self.start_ultra_spoof()')
        
        # Insert the method before export_telemetry
        content = content.replace("async def export_telemetry", block + "\n    async def export_telemetry")
        
        with open(".agent/research/anova/anova-interactive.py", "w") as f:
            f.write(content)
        print("Patched interactive script.")

patch_interactive()
