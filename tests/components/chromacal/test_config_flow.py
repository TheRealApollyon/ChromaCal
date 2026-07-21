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
    CONF_LIGHTS,
    CONF_NAME,
    CONF_REGION,
    CONF_START_TYPE,
    CONF_WARMWHITE_ENABLED,
    DOMAIN,
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

    lights = data[CONF_LIGHTS]
    assert len(lights) == 1
    assert lights[0][CONF_NAME] == "Front Porch"
    assert lights[0][CONF_ENTITY] == "light.front_porch"
    assert lights[0][CONF_FADE_IN] == 30
    assert lights[0][CONF_FADE_OUT] == 120


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
