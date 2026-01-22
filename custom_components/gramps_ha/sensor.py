"""Sensor platform for Gramps Web integration."""
from __future__ import annotations

import logging
from datetime import datetime, date

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_PERSON_NAME,
    ATTR_BIRTH_DATE,
    ATTR_AGE,
    ATTR_DAYS_UNTIL,
    CONF_URL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Gramps Web sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        GrampsWebNextBirthdaySensor(coordinator, entry, i)
        for i in range(5)  # Create 5 sensors for next 5 birthdays
    ]
    
    sensors.append(GrampsWebAllBirthdaysSensor(coordinator, entry))
    
    async_add_entities(sensors)


class GrampsWebNextBirthdaySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Gramps Web next birthday sensor."""

    def __init__(self, coordinator, entry: ConfigEntry, index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._index = index
        self._attr_name = f"Next Birthday {index + 1}"
        self._attr_unique_id = f"{entry.entry_id}_birthday_{index}"
        self._entry = entry

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        if self._index >= len(self.coordinator.data):
            return None
        
        birthday = self.coordinator.data[self._index]
        name = birthday.get("person_name", "Unknown")
        next_birthday = birthday.get("next_birthday")
        ordinal = self._index + 1  # 1st, 2nd, 3rd, 4th, 5th birthday
        
        if next_birthday:
            try:
                # Parse ISO date and format as DD.MM.YYYY
                dt = datetime.fromisoformat(next_birthday)
                formatted_date = dt.strftime("%d.%m.%Y")
                return f"{name} - {formatted_date} ({ordinal})"
            except Exception:
                return name
        
        return name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for grouping in HA UI."""
        config_url = self._entry.data.get(CONF_URL)
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title or "Gramps HA",
            manufacturer="Gramps Web",
            model="Birthdays",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=config_url,
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        if self._index >= len(self.coordinator.data):
            return {}
        
        birthday = self.coordinator.data[self._index]
        
        return {
            ATTR_PERSON_NAME: birthday.get("person_name"),
            ATTR_BIRTH_DATE: birthday.get("birth_date"),
            ATTR_AGE: birthday.get("age"),
            ATTR_DAYS_UNTIL: birthday.get("days_until"),
            "next_birthday": birthday.get("next_birthday"),
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:cake-variant"


class GrampsWebAllBirthdaysSensor(CoordinatorEntity, SensorEntity):
    """Representation of all upcoming birthdays sensor."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "All Upcoming Birthdays"
        self._attr_unique_id = f"{entry.entry_id}_all_birthdays"
        self._entry = entry

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
        
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {"birthdays": []}
        
        return {
            "birthdays": self.coordinator.data,
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:calendar-multiple"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for grouping in HA UI."""
        config_url = self._entry.data.get(CONF_URL)
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title or "Gramps HA",
            manufacturer="Gramps Web",
            model="Birthdays",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=config_url,
        )
