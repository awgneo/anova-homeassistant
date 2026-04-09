"""Config flow for Anova API integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .anova_lib.client import AnovaClient
from .anova_lib.exceptions import AnovaAuthError, AnovaConnectionError
from .const import DOMAIN, CONF_TOKEN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    token = data[CONF_TOKEN]
    if not token.startswith("anova-"):
        raise ValueError("invalid_format")

    session = async_get_clientsession(hass)
    client = AnovaClient(token=token, session=session)

    try:
        # We try connecting briefly to ensure token works
        success = await client.connect()
        if not success:
            raise AnovaConnectionError("Connection returned false")
    except AnovaAuthError:
        raise ValueError("invalid_auth")
    except Exception:
        _LOGGER.exception("Unexpected exception")
        raise ValueError("cannot_connect")
    finally:
        await client.close()

    # Return info to store in the entry
    return {"title": "Anova WiFi Devices"}


class AnovaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Anova API."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_TOKEN: user_input[CONF_TOKEN]})

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ValueError as err:
                errors["base"] = str(err)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
