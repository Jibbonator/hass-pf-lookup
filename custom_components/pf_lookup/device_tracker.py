from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_RESULT_MARKER, DATA_STORE, DOMAIN, RESULT_SLOTS
from .store import ResultStore


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store: ResultStore = hass.data[DOMAIN][DATA_STORE]
    async_add_entities(
        PackstationResultEntity(store, index) for index in range(RESULT_SLOTS)
    )


class PackstationResultEntity(TrackerEntity):
    _attr_should_poll = False
    _attr_source_type = SourceType.GPS

    def __init__(self, store: ResultStore, index: int) -> None:
        self._store = store
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_result_{index + 1}"
        self._attr_name = f"Packstation result {index + 1}"

    async def async_added_to_hass(self) -> None:
        self._store.add_listener(self._handle_store_update)
        self.async_on_remove(
            lambda: self._store.remove_listener(self._handle_store_update)
        )

    @callback
    def _handle_store_update(self) -> None:
        self.async_write_ha_state()

    @property
    def _item(self) -> dict[str, Any] | None:
        return self._store.get(self._index)

    @property
    def icon(self) -> str:
        return f"mdi:numeric-{self._index + 1}"

    @property
    def available(self) -> bool:
        return self._item is not None

    @property
    def latitude(self) -> float | None:
        item = self._item
        return item.get("latitude") if item else None

    @property
    def longitude(self) -> float | None:
        item = self._item
        return item.get("longitude") if item else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        item = self._item
        attributes: dict[str, Any] = {ATTR_RESULT_MARKER: True}
        if not item:
            return attributes

        street = " ".join(
            part for part in (item.get("street"), item.get("house_no")) if part
        )
        attributes.update(
            {
                "key": item.get("key"),
                "address": ", ".join(
                    part
                    for part in (
                        street,
                        f"{item.get('zip')} {item.get('city')}".strip(),
                    )
                    if part
                ),
                "distance_m": item.get("distance_m"),
                "capacity": item.get("capacity"),
            }
        )
        if "compartments" in item:
            attributes["compartments"] = item["compartments"]
            attributes["source_timestamp"] = item.get("source_timestamp")
        return attributes
