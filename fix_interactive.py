import re

with open(".agent/research/anova/anova-interactive.py", "r") as f:
    text = f.read()

# Fix the printing of the menu
menu_block_old = """1. Show message stream
            print("2. Start sous vide cook (wet bulb)")
            print("3. Start roasting (dry bulb)")
            print("4. Start steam cooking")
            print("5. Stop cooking")
            print("6. Set temperature unit")
            print("7. Export telemetry data")
            print("6. TEST PERFECT ANDROID SPOOF")
            print("7. TEST ULTRA SPOOF (EXACT MATCH)")
            print("0. Exit")"""

menu_block_new = """1. Show message stream
            print("2. Start sous vide cook (wet bulb)")
            print("3. Start roasting (dry bulb)")
            print("4. Start steam cooking")
            print("5. Stop cooking")
            print("6. Set temperature unit")
            print("7. Export telemetry data")
            print("8. TEST PERFECT ANDROID SPOOF")
            print("9. TEST ULTRA SPOOF (EXACT MATCH)")
            print("0. Exit")"""

text = text.replace('print("6. TEST PERFECT ANDROID SPOOF")\n            print("7. TEST ULTRA SPOOF (EXACT MATCH)")', 'print("8. TEST PERFECT ANDROID SPOOF")\n            print("9. TEST ULTRA SPOOF (EXACT MATCH)")')

with open(".agent/research/anova/anova-interactive.py", "w") as f:
    f.write(text)
