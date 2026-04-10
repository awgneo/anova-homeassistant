with open(".agent/research/anova/anova-interactive.py", "r") as f:
    content = f.read()

content = content.replace('''            elif choice == "6":
                await self.set_temperature_unit()
            elif choice == "7":
                await self.export_telemetry()
            elif choice == "0":''', '''            elif choice == "6":
                await self.set_temperature_unit()
            elif choice == "7":
                await self.export_telemetry()
            elif choice == "8":
                await self.start_spoofed_android_cook()
            elif choice == "9":
                await self.start_ultra_spoof()
            elif choice == "0":''')

content = content.replace('''6. TEST PERFECT ANDROID SPOOF
7. TEST ULTRA SPOOF (EXACT MATCH)
0. Exit''', '''8. TEST PERFECT ANDROID SPOOF
9. TEST ULTRA SPOOF (EXACT MATCH)
0. Exit''')

with open(".agent/research/anova/anova-interactive.py", "w") as f:
    f.write(content)
