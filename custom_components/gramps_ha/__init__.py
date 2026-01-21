"""The Gramps HA integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_URL, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

SCAN_INTERVAL = timedelta(hours=6)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gramps HA from a config entry."""
    try:
        from .grampsweb_api import GrampsWebAPI
        
        hass.data.setdefault(DOMAIN, {})
        
        api = GrampsWebAPI(
            url=entry.data.get(CONF_URL),
            username=entry.data.get(CONF_USERNAME),
            password=entry.data.get(CONF_PASSWORD),
        )
        
        coordinator = GrampsWebCoordinator(hass, api)
        await coordinator.async_config_entry_first_refresh()
        
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        return True
    except Exception as err:
        _LOGGER.error("Failed to setup Gramps HA: %s", err)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    try:
        if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
            hass.data[DOMAIN].pop(entry.entry_id)
        
        return unload_ok
    except Exception as err:
        _LOGGER.error("Failed to unload Gramps HA: %s", err)
        return False


class GrampsWebCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gramps Web data."""

    def __init__(self, hass: HomeAssistant, api) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.hass.async_add_executor_job(self.api.get_birthdays)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
