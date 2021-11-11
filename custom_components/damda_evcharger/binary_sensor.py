"""Damda EV's binary_sensor entity."""
from homeassistant.components.binary_sensor import DOMAIN, BinarySensorEntity
from homeassistant.core import callback

import logging

from .const import DEVICE_CLASS, DEVICE_ICON, NAME, DEVICE_UNIQUE
from .devcharger_device import DEVChargerDevice
from .api_devcharger import get_api


_LOGGER = logging.getLogger(__name__)


def log(flag, val):
    """0:debug, 1:info, 2:warning, 3:error."""
    if flag == 0:
        _LOGGER.debug(f"[{NAME}] Sensor > {val}")
    elif flag == 1:
        _LOGGER.info(f"[{NAME}] Sensor > {val}")
    elif flag == 2:
        _LOGGER.warning(f"[{NAME}] Sensor > {val}")
    elif flag == 3:
        _LOGGER.error(f"[{NAME}] Sensor > {val}")


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up binary_sensor for Damda EV component."""

    @callback
    def async_add_entity(devices=[]):
        """Add binary_sensor from api_devcharger."""
        entities = []
        api = get_api(hass, config_entry)
        if api:
            try:
                if len(devices) == 0:
                    devices = api.binary_sensors()
            except Exception:
                devices = []
            for device in devices:
                if DEVICE_UNIQUE not in device:
                    continue
                if not api.search_entity(DOMAIN, device[DEVICE_UNIQUE]):
                    entities.append(DEVChargerBinarySensor(device, api))

        if entities:
            async_add_entities(entities)

    api = get_api(hass, config_entry)
    if api:
        api.load(DOMAIN, async_add_entity)

    async_add_entity()


class DEVChargerBinarySensor(DEVChargerDevice, BinarySensorEntity):
    """Representation of a Damda EV binary sensor."""

    TYPE = DOMAIN

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self.api.get_state(self.unique_id)

    @property
    def device_class(self):
        """Return the class of the sensor."""
        value = self.api.get_state(self.unique_id, DEVICE_CLASS)
        if value == "":
            return None
        return value

    @property
    def icon(self):
        """Return the icon of the sensor."""
        value = self.api.get_state(self.unique_id, DEVICE_ICON)
        if value == "":
            return None
        return value
