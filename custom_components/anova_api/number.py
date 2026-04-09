"""Number platform for Anova Precision Ovens."""

from typing import Any
import uuid

from homeassistant.components.number import NumberEntity
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
    """Set up the Anova number platform."""
    client: AnovaClient = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = []
    for device_id, device in client.devices.items():
        if device.type == DeviceType.APO:
            entities.extend([
                AnovaSteamPercentage(client, device_id, device.name, device.model),
                AnovaTimerTarget(client, device_id, device.name, device.model),
                AnovaProbeTarget(client, device_id, device.name, device.model),
            ])
            
    async_add_entities(entities)


class AnovaSteamPercentage(NumberEntity):
    """Steam percentage slider for Anova APO."""

    _attr_has_entity_name = True
    _attr_name = "Steam Percentage"
    _attr_icon = "mdi:weather-partly-rainy"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_steam"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
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
            active_id = raw.get("activeStageId")
            stages = raw.get("stages", [])
            active_stage = stages[0] if stages else {}
            for s in stages:
                if s.get("id") == active_id:
                    active_stage = s
                    break
            
            do_block = active_stage.get("do", active_stage)
            mode = do_block.get("steamGenerators", {}).get("mode")
            if mode == "steam-percentage":
                val = do_block.get("steamGenerators", {}).get("steamPercentage", {}).get("setpoint", 0)
                self._attr_native_value = val
            elif mode == "relative-humidity":
                val = do_block.get("steamGenerators", {}).get("relativeHumidity", {}).get("setpoint", 0)
                self._attr_native_value = val
            else:
                self._attr_native_value = 0
                
            self.async_write_ha_state()
        except: pass

    async def async_set_native_value(self, value: float) -> None:
        await self._client.patch_active_stage(self._device_id, {
            "steamGenerators": {
                "mode": "steam-percentage",
                "steamPercentage": {"setpoint": int(value)}
            }
        })


class AnovaTimerTarget(NumberEntity):
    """Timer duration slider in minutes."""

    _attr_has_entity_name = True
    _attr_name = "Timer"
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 1440
    _attr_native_step = 1

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_timer"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
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
            active_id = raw.get("activeStageId")
            stages = raw.get("stages", [])
            active_stage = stages[0] if stages else {}
            for s in stages:
                if s.get("id") == active_id:
                    active_stage = s
                    break
            
            val = active_stage.get("do", active_stage).get("timer", {}).get("initial")
            if val is not None:
                self._attr_native_value = int(val / 60.0) # convert seconds to minutes
                self.async_write_ha_state()
        except: pass

    async def async_set_native_value(self, value: float) -> None:
        await self._client.patch_active_stage(self._device_id, {
            "timer": {"initial": int(value * 60)}
        })


class AnovaProbeTarget(NumberEntity):
    """Probe target temperature slider."""

    _attr_has_entity_name = True
    _attr_name = "Probe Target"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_probe"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
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
            # Look at probe object globally or in stages? Probe is generally at the root or do block
            val = None
            if "probe" in raw:
                val = raw.get("probe", {}).get("setpoint", {}).get("celsius")
                
            if val is not None:
                self._attr_native_value = val
                self.async_write_ha_state()
        except: pass

    async def async_set_native_value(self, value: float) -> None:
        cmd = {
            "command": "CMD_APO_SET_PROBE",
            "requestId": str(uuid.uuid4()),
            "payload": {
                "id": self._device_id,
                "type": "CMD_APO_SET_PROBE",
                "payload": {
                    "setpoint": {
                        "celsius": float(value)
                    }
                }
            }
        }
        await self._client.send_command(cmd)
