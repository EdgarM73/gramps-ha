"""Config flow for Gramps Web integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_URL, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.url,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        from .grampsweb_api import GrampsWebAPI
        
        url = data.get(CONF_URL, "").rstrip("/")
        if not url:
            raise ValueError("URL is required")
        
        api = GrampsWebAPI(
            url=url,
            username=data.get(CONF_USERNAME),
            password=data.get(CONF_PASSWORD),
        )

        # Test the connection
        try:
            result = await hass.async_add_executor_job(api.get_people)
            _LOGGER.debug("Successfully connected to Gramps Web")
        except Exception as conn_err:
            _LOGGER.warning("Could not connect to Gramps Web: %s", conn_err)
            # Don't fail on connection error, just log it
            # The integration will retry on setup
            
        return {"title": "Gramps HA"}
    except Exception as err:
        _LOGGER.error("Validation failed: %s", err)
        raise


class GrampsWebConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gramps Web."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            errors = {}
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "invalid_url"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"
                
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors=errors,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )
