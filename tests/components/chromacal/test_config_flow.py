"""Tests for the ChromaCal config flow: Region -> Categories -> First Light.

Exercises config_flow.py the same way HA's frontend "Add Integration"
wizard does — async_init/async_configure through the flow manager — without
needing a browser or an authenticated HA session.
"""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.chromacal.const import (
    CONF_CATEGORIES,
    CONF_END_TYPE,
    CONF_ENTITY,
    CONF_FADE_IN,
    CONF_FADE_OUT,
    CONF_NAME,
    CONF_REGION,
    CONF_START_TYPE,
    CONF_WARMWHITE_ENABLED,
    DOMAIN,
    LIGHT_SUBENTRY_TYPE,
)

LIGHT_INPUT = {
    CONF_NAME: "Front Porch",
    CONF_ENTITY: "light.front_porch",
    CONF_START_TYPE: "sunset",
    CONF_END_TYPE: "time",
    CONF_FADE_IN: "30",
    CONF_FADE_OUT: "120",
    CONF_WARMWHITE_ENABLED: True,
}


async def _complete_flow(hass: HomeAssistant, categories: list[str]):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_REGION: "us"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "categories"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CATEGORIES: categories}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "light"

    return await hass.config_entries.flow.async_configure(
        result["flow_id"], LIGHT_INPUT
    )


async def test_full_flow_creates_entry(hass: HomeAssistant) -> None:
    """Region -> Categories -> Light should complete and create a config entry."""
    hass.states.async_set("light.front_porch", "off")

    result = await _complete_flow(hass, ["federal", "cultural"])

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "ChromaCal"

    data = result["data"]
    assert data[CONF_REGION] == "us"
    assert data[CONF_CATEGORIES]["federal"] is True
    assert data[CONF_CATEGORIES]["cultural"] is True
    assert data[CONF_CATEGORIES]["pride"] is False
    # Lights are Config Subentries (Phase 8), not a data list -- entry.data
    # has no CONF_LIGHTS key at all for a fresh install.
    assert "lights" not in data

    entry = result["result"]
    lights = [s for s in entry.subentries.values() if s.subentry_type == LIGHT_SUBENTRY_TYPE]
    assert len(lights) == 1
    assert lights[0].data[CONF_NAME] == "Front Porch"
    assert lights[0].data[CONF_ENTITY] == "light.front_porch"
    assert lights[0].data[CONF_FADE_IN] == 30
    assert lights[0].data[CONF_FADE_OUT] == 120
    assert lights[0].title == "Front Porch"
    assert lights[0].subentry_id  # HA-generated, non-empty


async def test_single_instance_enforced(hass: HomeAssistant) -> None:
    """A second Add Integration attempt should abort once one entry exists."""
    hass.states.async_set("light.front_porch", "off")

    first = await _complete_flow(hass, ["federal"])
    assert first["type"] is FlowResultType.CREATE_ENTRY

    second = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "single_instance_allowed"


# ── Reconfigure: region + categories (entry.data, not an OptionsFlow --
# see config_flow.py's module docstring for why) ─────────────────────


async def _start_reconfigure_flow(hass: HomeAssistant, entry):
    """entry here is the real ConfigEntry the flow manager created (via
    _complete_flow), not a MockConfigEntry -- start_reconfigure_flow is a
    MockConfigEntry-only test convenience, so this reproduces what it
    does under the hood directly against the flow manager."""
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": entry.entry_id,
        },
    )


async def test_reconfigure_updates_region_and_categories(hass: HomeAssistant) -> None:
    hass.states.async_set("light.front_porch", "off")
    created = await _complete_flow(hass, ["federal"])
    entry = created["result"]

    result = await _start_reconfigure_flow(hass, entry)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure_region"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_REGION: "ca"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure_categories"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CATEGORIES: ["cultural", "pride"]}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.data[CONF_REGION] == "ca"
    assert live_entry.data[CONF_CATEGORIES]["cultural"] is True
    assert live_entry.data[CONF_CATEGORIES]["pride"] is True
    assert live_entry.data[CONF_CATEGORIES]["federal"] is False

    # Lights aren't touched by this flow at all -- still the one
    # subentry from the original wizard.
    lights = [s for s in live_entry.subentries.values() if s.subentry_type == LIGHT_SUBENTRY_TYPE]
    assert len(lights) == 1
    assert lights[0].data[CONF_NAME] == "Front Porch"


async def test_reconfigure_region_step_prefills_the_current_value(hass: HomeAssistant) -> None:
    hass.states.async_set("light.front_porch", "off")
    created = await _complete_flow(hass, ["federal"])
    entry = created["result"]

    result = await _start_reconfigure_flow(hass, entry)
    assert result["data_schema"]({})[CONF_REGION] == "us"
