"""Switch platform for Anova Precision Ovens."""

from typing import Any
import uuid

from homeassistant.components.switch import SwitchEntity
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
    """Set up the Anova switch platform."""
    client: AnovaClient = hass.data[DOMAIN][entry.entry_id]["client"]
    
    entities = []
    for device_id, device in client.devices.items():
        if device.type == DeviceType.APO:
            entities.extend([
                AnovaElementSwitch(client, device_id, device.name, device.model, "top", "Top Heating Element", "mdi:heating-coil"),
                AnovaElementSwitch(client, device_id, device.name, device.model, "bottom", "Bottom Heating Element", "mdi:heating-coil"),
                AnovaElementSwitch(client, device_id, device.name, device.model, "rear", "Rear Heating Element", "mdi:heating-coil"),
                AnovaVentSwitch(client, device_id, device.name, device.model),
            ])
            
    async_add_entities(entities)


class AnovaElementSwitch(SwitchEntity):
    """Heating element switch for Anova Precision Oven."""

    _attr_has_entity_name = True

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str, element_key: str, entity_name: str, icon: str) -> None:
        """Initialize the switch."""
        self._client = client
        self._device_id = device_id
        self._model = model
        self._element_key = element_key
        
        self._attr_name = entity_name
        self._attr_icon = icon
        self._attr_unique_id = f"anova_apo_{device_id}_heater_{element_key}"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=name,
            manufacturer="Anova",
            model=model,
        )
        self._remove_cb = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._remove_cb = self._client.register_callback(self._handle_update)
        self._handle_update(self._device_id, {})

    async def async_will_remove_from_hass(self) -> None:
        """Clean up."""
        if self._remove_cb:
            self._remove_cb()

    @callback
    def _handle_update(self, device_id: str, payload: dict) -> None:
        """Handle updated data from the websocket."""
        if device_id != self._device_id:
            return
            
        state = self._client.get_apo_state(self._device_id)
        if not state:
            return

        try:
            # e.g., payload.stages[0].do.heatingElements.top.on
            # Fallback speculatively
            heaters = state.raw_state.get("payload", {}).get("heatingElements", {})
            val = heaters.get(self._element_key, {}).get("on")
            if val is not None:
                self._attr_is_on = val
                self.async_write_ha_state()
        except Exception:
            pass

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        # This requires fetching current known states of other heaters and sending a new APO_START
        # Simplified placeholder for hardware interaction logic
        pass

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        pass


class AnovaVentSwitch(SwitchEntity):
    """Exhaust vent switch for Anova Precision Oven."""

    _attr_has_entity_name = True
    _attr_name = "Exhaust Vent"
    _attr_icon = "mdi:fan-off"

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        """Initialize."""
        self._client = client
        self._device_id = device_id
        self._model = model
        self._attr_unique_id = f"anova_apo_{device_id}_vent"
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
                vent = state.raw_state.get("payload", {}).get("vent", {}).get("open")
                if vent is not None:
                    self._attr_is_on = vent
                    self.async_write_ha_state()
            except Exception:
                pass

    async def async_turn_on(self, **kwargs: Any) -> None:
        pass

    async def async_turn_off(self, **kwargs: Any) -> None:
        pass
