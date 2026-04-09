# Anova API Integration for Home Assistant

A Platinum-tier Home Assistant custom component to control Anova Precision Cookers (APC) and Anova Precision Ovens (APO) locally over WebSockets.

## Features
- **Complete Oven Control:** Includes custom modes for multi-stage cooking.
- **Granular Exposure:** Exposes native HA entities for switches (heating elements, vents), numbers (fan speed, humidity), and climate control.
- **Sous Vide Support:** Seamless integration for Precision cookers mapped to Water Heaters.
- **Family Friendly UI:** Injectable custom panel to generate and execute recipes via an interactive GUI.

## Installation

### HACS (Recommended)
1. Go to HACS -> Integrations -> 3 dots (upper right) -> Custom repositories.
2. Add the URL of this repository and select 'Integration'.
3. Click Download.
4. Restart Home Assistant and navigate to **Settings -> Devices & Services -> Add Integration -> Anova**.

### Authentication
You will need your Personal Access Token. Open the **Anova Oven App** -> **More** -> **Developer** -> **Generate Personal Access Token**. (Sous vide cooker users will need to temporarily download the oven app just to retrieve this token).

---
*Developed purely in asynchronous Python to map exactly with Home Assistant standards.*
