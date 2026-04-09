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
                AnovaFanSpeed(client, device_id, device.name, device.model),
                AnovaHumiditySet(client, device_id, device.name, device.model),
            ])
            
    async_add_entities(entities)


class AnovaFanSpeed(NumberEntity):
    """Fan speed number slider for Anova APO."""

    _attr_has_entity_name = True
    _attr_name = "Convection Fan Speed"
    _attr_icon = "mdi:fan"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_fan_speed"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
        self._remove_cb = None

    async def async_added_to_hass(self) -> None:
        self._remove_cb = self._client.register_callback(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_cb:
            self._remove_cb()

    @callback
    def _handle_update(self, device_id: str, payload: dict) -> None:
        if device_id != self._device_id:
            return
        state = self._client.get_apo_state(self._device_id)
        if state:
            try:
                speed = state.raw_state.get("payload", {}).get("fan", {}).get("speed")
                if speed is not None:
                    self._attr_native_value = speed
                    self.async_write_ha_state()
            except Exception:
                pass

    async def async_set_native_value(self, value: float) -> None:
        """Set fan speed."""
        pass


class AnovaHumiditySet(NumberEntity):
    """Humidity setpoint slider for Anova APO."""

    _attr_has_entity_name = True
    _attr_name = "Target Humidity"
    _attr_icon = "mdi:water-percent"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        self._client = client
        self._device_id = device_id
        self._attr_unique_id = f"anova_apo_{device_id}_humidity"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})
        self._remove_cb = None

    async def async_added_to_hass(self) -> None:
        self._remove_cb = self._client.register_callback(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        if self._remove_cb:
            self._remove_cb()

    @callback
    def _handle_update(self, device_id: str, payload: dict) -> None:
        if device_id != self._device_id:
            return
        state = self._client.get_apo_state(self._device_id)
        if state:
            try:
                humidity = state.raw_state.get("payload", {}).get("steamGenerators", {}).get("relativeHumidity", {}).get("setpoint")
                if humidity is not None:
                    self._attr_native_value = humidity
                    self.async_write_ha_state()
            except Exception:
                pass

    async def async_set_native_value(self, value: float) -> None:
        pass
