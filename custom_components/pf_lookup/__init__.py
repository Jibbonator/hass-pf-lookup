from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.loader import async_get_integration

from .api import DhlPackstationApi, DhlPackstationError
from .const import (
    ATTR_KEY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_PERSON,
    CARD_FILENAME,
    CONF_PERSONS,
    CONF_RADIUS,
    CONF_RESULTS,
    DATA_API,
    DATA_CONFIG,
    DATA_FRONTEND,
    DATA_STORE,
    DEFAULT_RADIUS,
    DEFAULT_RESULTS,
    DOMAIN,
    FRONTEND_URL_PATH,
    RESULT_SLOTS,
    RESULT_TTL,
    SERVICE_PERSONS,
    SERVICE_SEARCH,
    SERVICE_STATUS,
)
from .store import ResultStore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER]

SERVICE_SEARCH_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_PERSON): cv.entity_id,
        vol.Optional(ATTR_LATITUDE): vol.Coerce(float),
        vol.Optional(ATTR_LONGITUDE): vol.Coerce(float),
        vol.Optional(CONF_RADIUS): vol.All(
            vol.Coerce(int), vol.Range(min=100, max=25000)
        ),
        vol.Optional(CONF_RESULTS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=20)
        ),
    }
)

SERVICE_STATUS_SCHEMA = vol.Schema({vol.Required(ATTR_KEY): cv.string})


def _config(hass: HomeAssistant) -> dict[str, Any]:
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return {}
    entry = entries[0]
    return {**entry.data, **entry.options}


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][DATA_API] = DhlPackstationApi(hass)
    hass.data[DOMAIN][DATA_STORE] = ResultStore(hass, RESULT_SLOTS, RESULT_TTL)

    async def _async_search(call: ServiceCall) -> ServiceResponse:
        api: DhlPackstationApi = hass.data[DOMAIN][DATA_API]
        settings = _config(hass)

        person = call.data.get(ATTR_PERSON)
        latitude = call.data.get(ATTR_LATITUDE)
        longitude = call.data.get(ATTR_LONGITUDE)

        if person:
            state = hass.states.get(person)
            if state is None:
                raise HomeAssistantError(f"Entity {person} not found")
            latitude = state.attributes.get("latitude")
            longitude = state.attributes.get("longitude")
            if latitude is None or longitude is None:
                raise HomeAssistantError(f"Entity {person} has no location")

        if latitude is None or longitude is None:
            raise HomeAssistantError(
                "Either 'person' or latitude+longitude is required"
            )

        radius = call.data.get(CONF_RADIUS, settings.get(CONF_RADIUS, DEFAULT_RADIUS))
        results = call.data.get(
            CONF_RESULTS, settings.get(CONF_RESULTS, DEFAULT_RESULTS)
        )

        try:
            locations = await api.async_search(latitude, longitude, radius, results)
        except DhlPackstationError as err:
            raise HomeAssistantError(str(err)) from err

        store: ResultStore = hass.data[DOMAIN][DATA_STORE]
        store.set_results(locations)

        return {
            "person": person,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "count": len(locations),
            "locations": locations,
        }

    async def _async_status(call: ServiceCall) -> ServiceResponse:
        api: DhlPackstationApi = hass.data[DOMAIN][DATA_API]
        try:
            detail = await api.async_status(call.data[ATTR_KEY])
        except DhlPackstationError as err:
            raise HomeAssistantError(str(err)) from err

        store: ResultStore = hass.data[DOMAIN][DATA_STORE]
        store.update_status(detail)
        return detail

    async def _async_persons(call: ServiceCall) -> ServiceResponse:
        settings = _config(hass)
        people: list[dict[str, Any]] = []
        for entity_id in settings.get(CONF_PERSONS, []):
            state = hass.states.get(entity_id)
            if state is None:
                continue
            people.append(
                {
                    "entity_id": entity_id,
                    "name": state.attributes.get("friendly_name") or entity_id,
                    "state": state.state,
                    "latitude": state.attributes.get("latitude"),
                    "longitude": state.attributes.get("longitude"),
                }
            )
        return {"persons": people}

    hass.services.async_register(
        DOMAIN,
        SERVICE_PERSONS,
        _async_persons,
        schema=vol.Schema({}),
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH,
        _async_search,
        schema=SERVICE_SEARCH_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STATUS,
        _async_status,
        schema=SERVICE_STATUS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    if hass.data[DOMAIN].get(DATA_FRONTEND):
        return

    card_dir = Path(__file__).parent / "www"
    if not (card_dir / CARD_FILENAME).is_file():
        _LOGGER.debug("No bundled card found, skipping frontend registration")
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL_PATH, str(card_dir), False)]
    )
    integration = await async_get_integration(hass, DOMAIN)
    version = integration.version or "0"
    add_extra_js_url(hass, f"{FRONTEND_URL_PATH}/{CARD_FILENAME}?v={version}")
    hass.data[DOMAIN][DATA_FRONTEND] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][DATA_CONFIG] = {**entry.data, **entry.options}
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await _async_register_frontend(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(DATA_CONFIG, None)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    hass.data[DOMAIN][DATA_CONFIG] = {**entry.data, **entry.options}
