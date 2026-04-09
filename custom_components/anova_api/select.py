"""Select platform for Anova APO recipes."""

from typing import Any
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .anova_lib.client import AnovaClient
from .anova_lib.models import DeviceType


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Anova select platform."""
    client: AnovaClient = hass.data[DOMAIN][entry.entry_id]["client"]
    recipes = hass.data[DOMAIN][entry.entry_id]["recipes"]
    
    entities = []
    for device_id, device in client.devices.items():
        if device.type == DeviceType.APO:
            entities.extend([
                AnovaRecipeSelect(client, device_id, device.name, device.model, recipes),
                AnovaHeatingElementSelect(client, device_id, device.name, device.model),
                AnovaFanSpeedSelect(client, device_id, device.name, device.model),
            ])
            
    async_add_entities(entities)


class AnovaRecipeSelect(SelectEntity):
    """Dropdown for selecting a multi-stage recipe."""

    _attr_has_entity_name = True
    _attr_name = "Recipe"
    _attr_icon = "mdi:chef-hat"

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str, recipes: list) -> None:
        self._client = client
        self._device_id = device_id
        self._recipes = recipes
        self._attr_unique_id = f"anova_apo_{device_id}_recipe_select"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
        
        self._attr_options = ["None"] + [r.get("name", "Unnamed") for r in self._recipes]
        self._attr_current_option = "None"

    @property
    def options(self) -> list[str]:
        """Return dynamically loaded recipe options."""
        return ["None"] + [r.get("name", "Unnamed") for r in self._recipes]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()

    @callback
    def _handle_update(self) -> None:
        """Update options if the global recipe list changes."""
        self.async_write_ha_state()


class AnovaHeatingElementSelect(SelectEntity):
    """Heating element selector."""

    _attr_has_entity_name = True
    _attr_name = "Heating Element"
    _attr_icon = "mdi:heating-coil"
    _attr_options = ["Top", "Rear", "Bottom", "Top + Rear", "Bottom + Rear", "Top + Bottom"]

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_heating_element"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
        self._attr_current_option = "Rear"
        self._remove_cb = None

    async def async_added_to_hass(self) -> None:
        self._remove_cb = self._client.register_callback(self._handle_update)
        self._handle_update(self._device_id, {})

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_cb:
            self._remove_cb()

    @callback
    def _handle_update(self, device_id: str, payload: dict) -> None:
        if device_id != self._device_id: return
        state = self._client.get_apo_state(device_id)
        if not state: return
        
        try:
            raw = state.raw_state.get("payload", {})
            stages = raw.get("stages", [])
            active_stage = stages[0] if stages else {}
            for s in stages:
                if s.get("id") == raw.get("activeStageId"):
                    active_stage = s
                    break
            
            elements = active_stage.get("do", active_stage).get("heatingElements", {})
            top = elements.get("top", {}).get("on", False)
            rear = elements.get("rear", {}).get("on", False)
            bot = elements.get("bottom", {}).get("on", False)
            
            if top and bot: self._attr_current_option = "Top + Bottom"
            elif top and rear: self._attr_current_option = "Top + Rear"
            elif bot and rear: self._attr_current_option = "Bottom + Rear"
            elif bot: self._attr_current_option = "Bottom"
            elif top: self._attr_current_option = "Top"
            else: self._attr_current_option = "Rear"
            self.async_write_ha_state()
        except: pass

    async def async_select_option(self, option: str) -> None:
        top, rear, bot = False, False, False
        if "Top" in option: top = True
        if "Rear" in option: rear = True
        if "Bottom" in option: bot = True
        if not (top or rear or bot): rear = True # Fallback

        await self._client.patch_active_stage(self._device_id, {
            "heatingElements": {
                "top": {"on": top},
                "rear": {"on": rear},
                "bottom": {"on": bot}
            }
        })


class AnovaFanSpeedSelect(SelectEntity):
    """Fan speed selector."""

    _attr_has_entity_name = True
    _attr_name = "Fan"
    _attr_icon = "mdi:fan"
    _attr_options = ["Off", "Low", "Medium", "High"]

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_fan_speed"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
        self._attr_current_option = "High"
        self._remove_cb = None

    async def async_added_to_hass(self) -> None:
        self._remove_cb = self._client.register_callback(self._handle_update)
        self._handle_update(self._device_id, {})

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_cb:
            self._remove_cb()

    @callback
    def _handle_update(self, device_id: str, payload: dict) -> None:
        if device_id != self._device_id: return
        state = self._client.get_apo_state(device_id)
        if not state: return
        
        try:
            raw = state.raw_state.get("payload", {})
            stages = raw.get("stages", [])
            active_stage = stages[0] if stages else {}
            for s in stages:
                if s.get("id") == raw.get("activeStageId"):
                    active_stage = s
                    break
            
            speed = active_stage.get("do", active_stage).get("fan", {}).get("speed", 100)
            if speed == 0: self._attr_current_option = "Off"
            elif speed <= 33: self._attr_current_option = "Low"
            elif speed <= 66: self._attr_current_option = "Medium"
            else: self._attr_current_option = "High"
            self.async_write_ha_state()
        except: pass

    async def async_select_option(self, option: str) -> None:
        val = 100
        if option == "Off": val = 0
        elif option == "Low": val = 33
        elif option == "Medium": val = 66
        
        await self._client.patch_active_stage(self._device_id, {
            "fan": {"speed": val}
        })
