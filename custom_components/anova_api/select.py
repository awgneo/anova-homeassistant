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
            entities.append(AnovaRecipeSelect(client, device_id, device.name, device.model, recipes))
            
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
