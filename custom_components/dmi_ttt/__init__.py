"""Example Load Platform integration."""
from __future__ import annotations

import logging

import asyncio

from .dmi_tts import dmi_tts

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

from .const import (
    CONF_DOMAIN,
    CONF_CLIENT,
    CONF_PLATFORM,
)


@asyncio.coroutine
def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    """Your controller/hub specific code."""
    # Data that you want to share with your platforms
    client = dmi_tts()
    hass.data[CONF_DOMAIN] = {CONF_CLIENT: client}

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            CONF_PLATFORM, CONF_DOMAIN, {}, config
        )
    )

    return True
