from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BASE_URL,
    LOCATION_TYPE_PACKSTATION,
    PATH_LOCATION,
    PATH_NEARBY,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class DhlPackstationError(Exception):
    pass


class DhlPackstationConnectionError(DhlPackstationError):
    pass


def _other_info(location: dict[str, Any], info_type: str) -> str | None:
    for entry in location.get("pfOtherinfos", []):
        if entry.get("type") == info_type:
            return entry.get("content")
    return None


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_location(location: dict[str, Any]) -> dict[str, Any]:
    geo = location.get("geoPosition") or {}
    return {
        "key": location.get("primaryKeyPF"),
        "name": location.get("keyWord") or location.get("locationName") or "DHL Packstation",
        "location_type": location.get("locationType"),
        "street": location.get("street"),
        "house_no": location.get("houseNo"),
        "zip": location.get("zipCode"),
        "city": location.get("city"),
        "district": location.get("district"),
        "latitude": geo.get("latitude"),
        "longitude": geo.get("longitude"),
        "distance_m": geo.get("distance"),
        "capacity": _as_int(_other_info(location, "capacity")),
    }


def parse_detail(location: dict[str, Any]) -> dict[str, Any]:
    live = location.get("liveStatus") or {}
    free = {
        "s": live.get("freeCompartmentsS"),
        "m": live.get("freeCompartmentsM"),
        "l": live.get("freeCompartmentsL"),
        "xl": live.get("freeCompartmentsXl"),
    }
    free_values = [value for value in free.values() if isinstance(value, int)]

    opening_hours = [
        {
            "weekday": info.get("weekday"),
            "from": info.get("timeFrom"),
            "to": info.get("timeTo"),
            "service": info.get("type"),
        }
        for info in location.get("pfTimeinfos", [])
    ]

    return {
        **parse_location(location),
        "compartments": {
            **free,
            "total_free": sum(free_values) if free_values else None,
            "capacity": _as_int(_other_info(location, "capacity")),
        },
        "source_timestamp": live.get("sourceTimestamp"),
        "model": _other_info(location, "packstation_model"),
        "station_type": _other_info(location, "packstation_type"),
        "open_all_day": _other_info(location, "open_all_day") == "true",
        "next_action": {
            "type": _other_info(location, "nextAction_type"),
            "day": _other_info(location, "nextAction_day"),
            "open_until": _other_info(location, "nextAction_openUntil"),
        },
        "services": location.get("pfServicetypes", []),
        "accessibility": location.get("pfAccessibilitytypes", []),
        "opening_hours": opening_hours,
    }


class DhlPackstationApi:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._session = async_get_clientsession(hass)

    async def _get(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json", "Sec-Fetch-Dest": "empty"},
                )
                response.raise_for_status()
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise DhlPackstationConnectionError(str(err)) from err
        except ValueError as err:
            raise DhlPackstationError(f"Invalid JSON from {url}") from err

    async def async_search(
        self, latitude: float, longitude: float, radius: int, results: int
    ) -> list[dict[str, Any]]:
        data = await self._get(
            PATH_NEARBY, {"address": f"{latitude:.6f},{longitude:.6f}"}
        )
        packstations = [
            parse_location(item)
            for item in data.get("pfLocations", [])
            if item.get("locationType") == LOCATION_TYPE_PACKSTATION
        ]
        packstations.sort(key=lambda item: item.get("distance_m") or 0)
        if radius:
            packstations = [
                item
                for item in packstations
                if (item.get("distance_m") or 0) <= radius
            ]
        return packstations[:results]

    async def async_status(self, key: str) -> dict[str, Any]:
        data = await self._get(PATH_LOCATION.format(key=key))
        return parse_detail(data)
