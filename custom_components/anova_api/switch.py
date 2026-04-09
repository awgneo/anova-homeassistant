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
            entities.append(AnovaSousVideSwitch(client, device_id, device.name, device.model))
            
    async_add_entities(entities)


class AnovaSousVideSwitch(SwitchEntity):
    """Sous Vide mode switch for Anova Precision Oven."""

    _attr_has_entity_name = True
    _attr_name = "Sous Vide Mode"
    _attr_icon = "mdi:water-boiler"

    def __init__(self, client: AnovaClient, device_id: str, name: str, model: str) -> None:
        """Initialize."""
        self._client = client
        self._device_id = device_id
        self._model = model
        self._attr_unique_id = f"anova_apo_{device_id}_sous_vide"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=name,
            manufacturer="Anova",
            model=model,
        )
        self._attr_is_on = False
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
            raw_payload = state.raw_state.get("payload", {})
            active_id = raw_payload.get("activeStageId")
            stages = raw_payload.get("stages", [])
            active_stage = stages[0] if stages else {}
            for s in stages:
                if s.get("id") == active_id:
                    active_stage = s
                    break
            
            do_block = active_stage.get("do", active_stage)
            mode = do_block.get("temperatureBulbs", {}).get("mode")
            if mode:
                self._attr_is_on = (mode == "wet")
                self.async_write_ha_state()
        except Exception:
            pass

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self._client.patch_active_stage(self._device_id, {
            "temperatureBulbs": {"mode": "wet"}
        })

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self._client.patch_active_stage(self._device_id, {
            "temperatureBulbs": {"mode": "dry"}
        })
