from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later


class ResultStore:
    def __init__(self, hass: HomeAssistant, slots: int, ttl: int) -> None:
        self._hass = hass
        self._slots = slots
        self._ttl = ttl
        self._data: list[dict[str, Any] | None] = [None] * slots
        self._listeners: set[Callable[[], None]] = set()
        self._cancel_expiry: Callable[[], None] | None = None

    def get(self, index: int) -> dict[str, Any] | None:
        return self._data[index]

    def add_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.add(listener)

    def remove_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.discard(listener)

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def _schedule_expiry(self) -> None:
        if self._cancel_expiry is not None:
            self._cancel_expiry()
        self._cancel_expiry = async_call_later(self._hass, self._ttl, self._expire)

    @callback
    def _expire(self, _now: Any = None) -> None:
        self._cancel_expiry = None
        if any(item is not None for item in self._data):
            self._data = [None] * self._slots
            self._notify()

    def set_results(self, locations: list[dict[str, Any]]) -> None:
        self._data = [None] * self._slots
        for index, location in enumerate(locations[: self._slots]):
            self._data[index] = dict(location)
        self._schedule_expiry()
        self._notify()

    def update_status(self, detail: dict[str, Any]) -> None:
        key = detail.get("key")
        for index, item in enumerate(self._data):
            if item and item.get("key") == key:
                merged = dict(item)
                merged["compartments"] = detail.get("compartments")
                merged["source_timestamp"] = detail.get("source_timestamp")
                merged["open_all_day"] = detail.get("open_all_day")
                merged["services"] = detail.get("services")
                self._data[index] = merged
                self._schedule_expiry()
                self._notify()
                return
