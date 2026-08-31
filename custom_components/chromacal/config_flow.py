"""Config flow for ChromaCal — ports the v1 HTML wizard's setup steps.

The v1 wizard's Connect (HA URL + long-lived token) and Theme steps are
dropped here: this integration runs in-process, so there's no token to
paste and no page to theme. Region -> Categories -> First Light is what's
left, matching wz-step 3/4/5 in chromacal.html. Advanced per-light fields
(startOffset, fadeInKelvin, intensityOverride, salute/emergency-broadcast
flags) stay out of first-run setup, same as v1 kept them in the "edit
light" modal rather than the wizard.

Phase 8 adds post-setup editing, split the way HA's own current docs
draw the line (confirmed against the actual frontend source, not just
docs -- ha-config-entry-row.ts renders a "Reconfigure" dropdown item when
supports_reconfigure and a separate gear-icon "Configure" button when
supports_options): region/categories are core setup data living in
entry.data, so they're edited via a Reconfigure Flow
(async_step_reconfigure), not an OptionsFlow. This integration has no
genuinely optional settings yet, so there's no OptionsFlow at all.

Lights are Config Subentries (ConfigSubentryFlow), not a list inside
entry.data -- each light is independently addable/editable/removable
from its own native HA UI, and gets an HA-generated stable subentry_id
(a ULID) for free, which is what sensor.py/button.py now key unique_ids
on instead of a light's `entity` string. See __init__.py's
async_migrate_entry for how already-configured lights move from the old
CONF_LIGHTS list into real subentries without disturbing their existing
entities' entity_ids.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CATEGORIES,
    CONF_CATEGORIES,
    CONF_END_TIME,
    CONF_END_TYPE,
    CONF_ENTITY,
    CONF_FADE_IN,
    CONF_FADE_OUT,
    CONF_NAME,
    CONF_REGION,
    CONF_START_TIME,
    CONF_START_TYPE,
    CONF_VERIFY_CHECK_DELAY,
    CONF_VERIFY_ENABLED,
    CONF_VERIFY_RETRY_COUNT,
    CONF_WARMWHITE_ENABLED,
    CONF_WARMWHITE_TIME,
    CONF_ZONE,
    DEFAULT_END_TIME,
    DEFAULT_FADE_IN,
    DEFAULT_FADE_OUT,
    DEFAULT_START_TIME,
    DEFAULT_VERIFY_CHECK_DELAY,
    DEFAULT_VERIFY_RETRY_COUNT,
    DEFAULT_WARMWHITE_TIME,
    DOMAIN,
    END_TYPES,
    FADE_IN_OPTIONS,
    FADE_OUT_OPTIONS,
    LIGHT_SUBENTRY_TYPE,
    REGIONS,
    START_TYPES,
    VERIFY_CHECK_DELAY_OPTIONS,
    VERIFY_RETRY_COUNT_OPTIONS,
)


def _region_schema(*, default: str = "us") -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_REGION, default=default): selector.SelectSelector(
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


def _categories_schema(*, default: list[str] | None = None) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_CATEGORIES, default=default if default is not None else list(CATEGORIES)
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


def _light_schema(light: dict[str, Any] | None = None) -> vol.Schema:
    """Schema for adding a light (light=None) or editing one (pre-filled
    from its current subentry data). Name/entity get no default when
    adding -- vol.UNDEFINED means "no default", forcing a real choice,
    same as the original add-light form always required.
    """
    light = light or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=light.get(CONF_NAME, vol.UNDEFINED)): selector.TextSelector(),
            vol.Optional(CONF_ZONE, default=light.get(CONF_ZONE, "")): selector.TextSelector(),
            vol.Required(
                CONF_ENTITY, default=light.get(CONF_ENTITY, vol.UNDEFINED)
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain=["light", "switch"])),
            vol.Required(
                CONF_START_TYPE, default=light.get(CONF_START_TYPE, "sunset")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=START_TYPES, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(
                CONF_START_TIME, default=light.get(CONF_START_TIME, DEFAULT_START_TIME)
            ): selector.TimeSelector(),
            vol.Required(
                CONF_END_TYPE, default=light.get(CONF_END_TYPE, "time")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=END_TYPES, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(
                CONF_END_TIME, default=light.get(CONF_END_TIME, DEFAULT_END_TIME)
            ): selector.TimeSelector(),
            vol.Required(
                CONF_FADE_IN, default=str(light.get(CONF_FADE_IN, DEFAULT_FADE_IN))
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in FADE_IN_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_FADE_OUT, default=str(light.get(CONF_FADE_OUT, DEFAULT_FADE_OUT))
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in FADE_OUT_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_WARMWHITE_TIME, default=light.get(CONF_WARMWHITE_TIME, DEFAULT_WARMWHITE_TIME)
            ): selector.TimeSelector(),
            vol.Required(
                CONF_WARMWHITE_ENABLED, default=light.get(CONF_WARMWHITE_ENABLED, True)
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_VERIFY_ENABLED, default=light.get(CONF_VERIFY_ENABLED, True)
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_VERIFY_RETRY_COUNT,
                default=str(light.get(CONF_VERIFY_RETRY_COUNT, DEFAULT_VERIFY_RETRY_COUNT)),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in VERIFY_RETRY_COUNT_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_VERIFY_CHECK_DELAY,
                default=str(light.get(CONF_VERIFY_CHECK_DELAY, DEFAULT_VERIFY_CHECK_DELAY)),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(v) for v in VERIFY_CHECK_DELAY_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _light_dict_from_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Same field set _light_schema() collects, as the plain dict shape
    stored in a subentry's `data` (mirrors v1's saveLight() object)."""
    return {
        CONF_NAME: user_input[CONF_NAME],
        CONF_ZONE: user_input.get(CONF_ZONE, ""),
        CONF_ENTITY: user_input[CONF_ENTITY],
        CONF_START_TYPE: user_input[CONF_START_TYPE],
        CONF_START_TIME: user_input.get(CONF_START_TIME, DEFAULT_START_TIME),
        CONF_END_TYPE: user_input[CONF_END_TYPE],
        CONF_END_TIME: user_input.get(CONF_END_TIME, DEFAULT_END_TIME),
        CONF_FADE_IN: int(user_input[CONF_FADE_IN]),
        CONF_FADE_OUT: int(user_input[CONF_FADE_OUT]),
        CONF_WARMWHITE_TIME: user_input.get(CONF_WARMWHITE_TIME, DEFAULT_WARMWHITE_TIME),
        CONF_WARMWHITE_ENABLED: user_input[CONF_WARMWHITE_ENABLED],
        CONF_VERIFY_ENABLED: user_input[CONF_VERIFY_ENABLED],
        CONF_VERIFY_RETRY_COUNT: int(user_input[CONF_VERIFY_RETRY_COUNT]),
        CONF_VERIFY_CHECK_DELAY: int(user_input[CONF_VERIFY_CHECK_DELAY]),
    }


class ChromaCalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ChromaCal setup wizard: Region -> Categories -> First Light."""

    VERSION = 2

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
        """Step 3: first light (wz-step-5 in chromacal.html) -- created as
        a real subentry from the start, not a data-list item."""
        if user_input is not None:
            light = _light_dict_from_input(user_input)
            return self.async_create_entry(
                title="ChromaCal",
                data={
                    CONF_REGION: self._region,
                    CONF_CATEGORIES: {
                        key: key in self._categories for key in CATEGORIES
                    },
                },
                subentries=[
                    {
                        "subentry_type": LIGHT_SUBENTRY_TYPE,
                        "title": light[CONF_NAME],
                        "unique_id": None,
                        "data": light,
                    }
                ],
            )

        return self.async_show_form(step_id="light", data_schema=_light_schema())

    # ── Reconfigure: region + categories live in entry.data, so they're
    # edited via a Reconfigure Flow, not an OptionsFlow -- confirmed
    # against HA's current docs and the frontend source that this is the
    # documented, current distinction, not just a naming preference. ──

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Entry point for the "Reconfigure" menu item."""
        entry = self._get_reconfigure_entry()
        self._region = entry.data[CONF_REGION]
        return await self.async_step_reconfigure_region()

    async def async_step_reconfigure_region(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_reconfigure_categories()

        return self.async_show_form(
            step_id="reconfigure_region",
            data_schema=_region_schema(default=entry.data[CONF_REGION]),
        )

    async def async_step_reconfigure_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            categories = {key: key in user_input[CONF_CATEGORIES] for key in CATEGORIES}
            return self.async_update_reload_and_abort(
                entry,
                data_updates={CONF_REGION: self._region, CONF_CATEGORIES: categories},
            )

        current = [key for key, enabled in entry.data[CONF_CATEGORIES].items() if enabled]
        return self.async_show_form(
            step_id="reconfigure_categories",
            data_schema=_categories_schema(default=current),
        )

    @staticmethod
    @callback
    def async_get_supported_subentry_types(
        config_entry: config_entries.ConfigEntry,
    ) -> dict[str, type[config_entries.ConfigSubentryFlow]]:
        """Lights are the only subentry type -- one per configured light."""
        return {LIGHT_SUBENTRY_TYPE: LightSubentryFlowHandler}


class LightSubentryFlowHandler(config_entries.ConfigSubentryFlow):
    """Add a new light, or edit/remove an existing one.

    Removal needs no code here -- HA's own subentry UI (a delete action
    per subentry in the device list) calls
    hass.config_entries.async_remove_subentry directly.
    """

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.SubentryFlowResult:
        """Add a new light.

        Unlike editing (async_update_reload_and_abort), there's no
        built-in create-and-reload helper -- ConfigSubentryFlowManager
        only adds the new subentry to the entry AFTER this step returns
        (see its async_finish_flow, which calls async_add_subentry
        itself once our result comes back). Without a reload afterward,
        the new light gets a subentry but no sensor/button entities at
        all until the next manual reload or HA restart, since those
        platforms only add entities once, at async_setup_entry time --
        confirmed via test_add_light_creates_a_new_subentry_and_entities.

        hass.async_create_task defaults to eager_start=True, which runs
        the reload inline, synchronously, as part of *this* call --
        before async_finish_flow's async_add_subentry has run. That
        raced the reload against the subentry actually being added and
        the new light lost, silently missing its own first setup. Passing
        eager_start=False defers the reload to the next event-loop
        iteration, which only happens after this whole synchronous call
        chain (including async_finish_flow) has completed.
        """
        if user_input is not None:
            light = _light_dict_from_input(user_input)
            result = self.async_create_entry(title=light[CONF_NAME], data=light)
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry_id),
                "chromacal_add_light_reload",
                eager_start=False,
            )
            return result

        return self.async_show_form(step_id="user", data_schema=_light_schema())

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.SubentryFlowResult:
        """Edit an existing light's settings."""
        subentry = self._get_reconfigure_subentry()
        if user_input is not None:
            light = _light_dict_from_input(user_input)
            return self.async_update_reload_and_abort(
                self._get_entry(),
                subentry,
                title=light[CONF_NAME],
                data=light,
            )

        return self.async_show_form(
            step_id="reconfigure", data_schema=_light_schema(dict(subentry.data))
        )
