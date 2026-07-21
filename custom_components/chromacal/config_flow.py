"""Config flow for ChromaCal — ports the v1 HTML wizard's setup steps.

The v1 wizard's Connect (HA URL + long-lived token) and Theme steps are
dropped here: this integration runs in-process, so there's no token to
paste and no page to theme. Region -> Categories -> First Light is what's
left, matching wz-step 3/4/5 in chromacal.html. Advanced per-light fields
(startOffset, fadeInKelvin, intensityOverride, salute/emergency-broadcast
flags) stay out of first-run setup, same as v1 kept them in the "edit
light" modal rather than the wizard — they'll arrive via an options flow
in a later phase.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CATEGORIES,
    CONF_CATEGORIES,
    CONF_END_TIME,
    CONF_END_TYPE,
    CONF_ENTITY,
    CONF_FADE_IN,
    CONF_FADE_OUT,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_REGION,
    CONF_START_TIME,
    CONF_START_TYPE,
    CONF_WARMWHITE_ENABLED,
    CONF_WARMWHITE_TIME,
    CONF_ZONE,
    DEFAULT_END_TIME,
    DEFAULT_FADE_IN,
    DEFAULT_FADE_OUT,
    DEFAULT_START_TIME,
    DEFAULT_WARMWHITE_TIME,
    DOMAIN,
    END_TYPES,
    FADE_IN_OPTIONS,
    FADE_OUT_OPTIONS,
    REGIONS,
    START_TYPES,
)


def _region_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_REGION, default="us"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=label)
                        for key, label in REGIONS.items()
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
    )


def _categories_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_CATEGORIES, default=list(CATEGORIES)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=label)
                        for key, label in CATEGORIES.items()
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                    multiple=True,
                )
            ),
        }
    )


def _light_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME): selector.TextSelector(),
            vol.Optional(CONF_ZONE, default=""): selector.TextSelector(),
            vol.Required(CONF_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["light", "switch"])
            ),
            vol.Required(CONF_START_TYPE, default="sunset"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=START_TYPES, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(
                CONF_START_TIME, default=DEFAULT_START_TIME
            ): selector.TimeSelector(),
            vol.Required(CONF_END_TYPE, default="time"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=END_TYPES, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(
                CONF_END_TIME, default=DEFAULT_END_TIME
            ): selector.TimeSelector(),
            vol.Required(
                CONF_FADE_IN, default=str(DEFAULT_FADE_IN)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in FADE_IN_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_FADE_OUT, default=str(DEFAULT_FADE_OUT)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in FADE_OUT_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_WARMWHITE_TIME, default=DEFAULT_WARMWHITE_TIME
            ): selector.TimeSelector(),
            vol.Required(
                CONF_WARMWHITE_ENABLED, default=True
            ): selector.BooleanSelector(),
        }
    )


class ChromaCalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ChromaCal setup wizard: Region -> Categories -> First Light."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow's in-progress state."""
        self._region: str | None = None
        self._categories: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: region (wz-step-3 in chromacal.html)."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_categories()

        return self.async_show_form(step_id="user", data_schema=_region_schema())

    async def async_step_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: categories (wz-step-4 in chromacal.html)."""
        if user_input is not None:
            self._categories = user_input[CONF_CATEGORIES]
            return await self.async_step_light()

        return self.async_show_form(
            step_id="categories", data_schema=_categories_schema()
        )

    async def async_step_light(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 3: first light (wz-step-5 in chromacal.html)."""
        if user_input is not None:
            light = {
                CONF_NAME: user_input[CONF_NAME],
                CONF_ZONE: user_input.get(CONF_ZONE, ""),
                CONF_ENTITY: user_input[CONF_ENTITY],
                CONF_START_TYPE: user_input[CONF_START_TYPE],
                CONF_START_TIME: user_input.get(CONF_START_TIME, DEFAULT_START_TIME),
                CONF_END_TYPE: user_input[CONF_END_TYPE],
                CONF_END_TIME: user_input.get(CONF_END_TIME, DEFAULT_END_TIME),
                CONF_FADE_IN: int(user_input[CONF_FADE_IN]),
                CONF_FADE_OUT: int(user_input[CONF_FADE_OUT]),
                CONF_WARMWHITE_TIME: user_input.get(
                    CONF_WARMWHITE_TIME, DEFAULT_WARMWHITE_TIME
                ),
                CONF_WARMWHITE_ENABLED: user_input[CONF_WARMWHITE_ENABLED],
            }
            return self.async_create_entry(
                title="ChromaCal",
                data={
                    CONF_REGION: self._region,
                    CONF_CATEGORIES: {
                        key: key in self._categories for key in CATEGORIES
                    },
                    CONF_LIGHTS: [light],
                },
            )

        return self.async_show_form(step_id="light", data_schema=_light_schema())
