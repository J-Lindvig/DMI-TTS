from __future__ import annotations

import logging

from datetime import timedelta

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DOMAIN,
    CONF_CLIENT,
    CONF_PLATFORM,
    CREDITS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""

    async def async_update_data():
        # try:
        dmi_tts = hass.data[CONF_DOMAIN][CONF_CLIENT]
        await hass.async_add_executor_job(dmi_tts.fetch_data)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=CONF_PLATFORM,
        update_method=async_update_data,
        update_interval=timedelta(minutes=10),
    )

    # Immediate refresh
    await coordinator.async_request_refresh()

    dmi_tts = hass.data[CONF_DOMAIN][CONF_CLIENT]

    entities = []
    forecasts = dmi_tts.get_data()

    entities.append(DMI_Land_Sensor(hass, coordinator, forecasts["land"]))
    entities.append(DMI_7_Days_Sensor(hass, coordinator, forecasts["7_days"]))
    for region in forecasts["regions"]:
        entities.append(
            DMI_Region_Sensor(hass, coordinator, forecasts["regions"][region])
        )

    async_add_entities(entities)


class DMI_Land_Sensor(SensorEntity):
    def __init__(self, hass, coordinator, forecast) -> None:
        self.hass = hass
        self._coordinator = coordinator
        self._data = forecast
        self._name = hass.data[CONF_DOMAIN]["prefix"] + forecast["name"]
        self._state = forecast["date"]
        self._unique_id = forecast["unique_id"]
        self._icon = "mdi:calendar-today"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # return "Example Temperature"
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        # Prepare a dictionary with a list of credits
        attr = {
            "timestamp": self._data["timestamp"],
            "forecast": self._data["forecast"],
            "risk_of_ice": self._data["risk_of_ice"],
            ATTR_ATTRIBUTION: CREDITS,
        }
        return attr

    @property
    def unique_id(self):
        return CONF_PLATFORM + "_" + self._unique_id

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class DMI_7_Days_Sensor(SensorEntity):
    def __init__(self, hass, coordinator, forecast) -> None:
        self.hass = hass
        self._coordinator = coordinator
        self._data = forecast
        self._name = hass.data[CONF_DOMAIN]["prefix"] + forecast["name"]
        self._state = forecast["preface"]
        self._unique_id = forecast["unique_id"]
        self._icon = "mdi:calendar-week"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # return "Example Temperature"
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        # Prepare a dictionary with a list of credits
        attr = {
            "timestamp": self._data["timestamp"],
            "date": self._data["date"],
            "summary": self._data["summary"],
            "uncertainty": self._data["uncertainty"],
            "precipitation": self._data["precipitation"],
            "days": self._data["days"],
            ATTR_ATTRIBUTION: CREDITS,
        }
        return attr

    @property
    def unique_id(self):
        return CONF_PLATFORM + "_" + self._unique_id

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class DMI_Region_Sensor(SensorEntity):
    def __init__(self, hass, coordinator, forecast) -> None:
        self.hass = hass
        self._coordinator = coordinator
        self._data = forecast
        self._name = hass.data[CONF_DOMAIN]["prefix"] + forecast["name"]
        self._state = forecast["summary"]
        self._unique_id = forecast["unique_id"]
        self._icon = "mdi:map-marker-radius"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        # return "Example Temperature"
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        # Prepare a dictionary with a list of credits
        attr = {
            "timestamp": self._data["timestamp"],
            "date": self._data["date"],
            "forecast": self._data["forecast"],
            ATTR_ATTRIBUTION: CREDITS,
        }
        return attr

    @property
    def unique_id(self):
        return CONF_PLATFORM + "_" + self._unique_id

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
