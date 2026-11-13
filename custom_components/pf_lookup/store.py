from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ResultStore:
    def __init__(self, slots: int) -> None:
        self._slots = slots
        self._data: list[dict[str, Any] | None] = [None] * slots
        self._listeners: set[Callable[[], None]] = set()

    def get(self, index: int) -> dict[str, Any] | None:
        return self._data[index]

    def add_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.add(listener)

    def remove_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.discard(listener)

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def set_results(self, locations: list[dict[str, Any]]) -> None:
        self._data = [None] * self._slots
        for index, location in enumerate(locations[: self._slots]):
            self._data[index] = dict(location)
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
                self._notify()
                return
