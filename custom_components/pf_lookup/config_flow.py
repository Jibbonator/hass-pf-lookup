from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, selector

from .const import (
    ATTR_RESULT_MARKER,
    CONF_PERSONS,
    CONF_RADIUS,
    CONF_RESULTS,
    DEFAULT_RADIUS,
    DEFAULT_RESULTS,
    DOMAIN,
    NAME,
)


def _location_entities(hass: HomeAssistant) -> dict[str, str]:
    persons: dict[str, str] = {}
    person_sources: set[str] = set()
    trackers: dict[str, str] = {}

    for state in hass.states.async_all():
        entity_id = state.entity_id
        if not entity_id.startswith(("person.", "device_tracker.")):
            continue
        if state.attributes.get(ATTR_RESULT_MARKER):
            continue

        latitude = state.attributes.get("latitude")
        longitude = state.attributes.get("longitude")
        if not isinstance(latitude, (int, float)) or not isinstance(
            longitude, (int, float)
        ):
            continue

        name = state.attributes.get("friendly_name") or entity_id
        if entity_id.startswith("person."):
            source = state.attributes.get("source")
            if isinstance(source, str) and source:
                person_sources.add(source)
                persons[entity_id] = f"{name} ({entity_id} → {source})"
            else:
                persons[entity_id] = f"{name} ({entity_id})"
        else:
            trackers[entity_id] = f"{name} ({entity_id})"

    for entity_id in list(trackers):
        if entity_id in person_sources:
            del trackers[entity_id]

    return dict(
        sorted({**persons, **trackers}.items(), key=lambda item: item[1].lower())
    )


def _normalise_persons(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [key for key, flag in value.items() if flag]
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _schema(choices: dict[str, str], defaults: dict[str, Any]) -> vol.Schema:
    persons = [item for item in defaults.get(CONF_PERSONS, []) if item in choices]
    return vol.Schema(
        {
            vol.Required(CONF_PERSONS, default=persons): cv.multi_select(choices),
            vol.Optional(
                CONF_RADIUS, default=defaults.get(CONF_RADIUS, DEFAULT_RADIUS)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=100,
                    max=25000,
                    step=100,
                    unit_of_measurement="m",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_RESULTS, default=defaults.get(CONF_RESULTS, DEFAULT_RESULTS)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=20,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


class PfLookupConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        choices = _location_entities(self.hass)
        if not choices:
            return self.async_abort(reason="no_persons")

        errors: dict[str, str] = {}
        if user_input is not None:
            persons = _normalise_persons(user_input[CONF_PERSONS])
            if not persons:
                errors["base"] = "no_person_selected"
            else:
                return self.async_create_entry(
                    title=NAME,
                    data={
                        CONF_PERSONS: persons,
                        CONF_RADIUS: int(user_input[CONF_RADIUS]),
                        CONF_RESULTS: int(user_input[CONF_RESULTS]),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(choices, user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        return PfLookupOptionsFlow()


class PfLookupOptionsFlow(OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        current = {**self.config_entry.data, **self.config_entry.options}
        choices = _location_entities(self.hass)

        errors: dict[str, str] = {}
        if user_input is not None:
            persons = _normalise_persons(user_input[CONF_PERSONS])
            if not persons:
                errors["base"] = "no_person_selected"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_PERSONS: persons,
                        CONF_RADIUS: int(user_input[CONF_RADIUS]),
                        CONF_RESULTS: int(user_input[CONF_RESULTS]),
                    },
                )

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(choices, user_input or current),
            errors=errors,
        )
