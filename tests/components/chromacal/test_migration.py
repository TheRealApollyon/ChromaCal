"""Tests for the version 1 -> 2 migration: entry.data["lights"] -> real
Config Subentries (Phase 8).

This is the real bar for the whole phase, not an afterthought: an
already-configured install has REAL, LIVE entities keyed on the old
light_entity-based unique_id scheme. The migration must move that light
into a subentry and repoint those entities' unique_ids WITHOUT changing
their entity_id, state, or any customization -- anything else silently
orphans real users' history and dashboards the same way the original
Phase 5a bug did.
"""

from __future__ import annotations

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.chromacal.const import (
    CONF_ENTITY,
    CONF_NAME,
    DOMAIN,
    LIGHT_SUBENTRY_TYPE,
)

LIGHT_ENTITY = "light.front_porch"

OLD_SHAPE_ENTRY_DATA = {
    "region": "us",
    "categories": {"federal": True},
    "lights": [
        {
            "name": "Front Porch",
            "zone": "",
            "entity": LIGHT_ENTITY,
            "start_type": "sunset",
            "start_time": "19:00",
            "end_type": "time",
            "end_time": "23:00",
            "fade_in": 30,
            "fade_out": 120,
            "warmwhite_time": "22:00",
            "warmwhite_enabled": True,
        }
    ],
}


async def test_migration_preserves_existing_entity_identity(hass, freezer):
    """Seed a real pre-Phase-8 install (old-shape data, live entities
    already registered under the old unique_id scheme) and confirm the
    migration preserves entity_id/history while moving the light into a
    subentry -- the actual bar for this phase, checked before anything
    else about it gets called done.
    """
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = MockConfigEntry(
        domain=DOMAIN, data=OLD_SHAPE_ENTRY_DATA, entry_id="test_migration", version=1
    )
    entry.add_to_hass(hass)

    # Simulate a real already-deployed install: these entities exist under
    # the OLD light_entity-keyed unique_id scheme BEFORE this entry is
    # ever set up under the new (subentry-aware) code -- exactly what an
    # existing user's registry looks like the moment they update.
    registry = er.async_get(hass)
    old_sensor_unique_id = f"test_migration_{LIGHT_ENTITY}_schedule"
    old_button_unique_id = f"test_migration_{LIGHT_ENTITY}_force_white"
    sensor_reg_entry = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        old_sensor_unique_id,
        config_entry=entry,
        suggested_object_id="front_porch_schedule",
    )
    button_reg_entry = registry.async_get_or_create(
        "button",
        DOMAIN,
        old_button_unique_id,
        config_entry=entry,
        suggested_object_id="front_porch_force_white",
    )
    original_sensor_entity_id = sensor_reg_entry.entity_id
    original_button_entity_id = button_reg_entry.entity_id
    assert original_sensor_entity_id == "sensor.front_porch_schedule"
    assert original_button_entity_id == "button.front_porch_force_white"

    # Deliberately NOT calling hass.states.async_set() here to fake prior
    # history -- tried that first and it broke the exact thing this test
    # proves works: a raw state write makes HA treat that entity_id as
    # already claimed by something else, so the real entity then collides
    # with it instead of reattaching ("Platform chromacal does not
    # generate unique IDs... already exists - ignoring"). A real restart
    # never has that problem (the previous run's entity cleanly vacates
    # the slot on shutdown) -- the registry entry alone is the right and
    # sufficient way to simulate "this already existed."

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)

    # ── entity_id: byte-for-byte unchanged ──────────────────────────
    assert registry.async_get(original_sensor_entity_id) is not None
    assert registry.async_get(original_button_entity_id) is not None

    # ── unique_id: moved to the new subentry-based scheme ───────────
    light_subentries = [
        s for s in live_entry.subentries.values() if s.subentry_type == LIGHT_SUBENTRY_TYPE
    ]
    assert len(light_subentries) == 1
    subentry = light_subentries[0]

    new_sensor_reg_entry = registry.async_get(original_sensor_entity_id)
    new_button_reg_entry = registry.async_get(original_button_entity_id)
    assert new_sensor_reg_entry.unique_id == f"test_migration_{subentry.subentry_id}_schedule"
    assert new_button_reg_entry.unique_id == f"test_migration_{subentry.subentry_id}_force_white"
    assert new_sensor_reg_entry.config_subentry_id == subentry.subentry_id
    assert new_button_reg_entry.config_subentry_id == subentry.subentry_id

    # ── entry.data: lights list gone; the light's data survived intact
    # inside the new subentry instead ───────────────────────────────
    assert "lights" not in live_entry.data
    assert live_entry.version == 2
    assert subentry.data[CONF_NAME] == "Front Porch"
    assert subentry.data[CONF_ENTITY] == LIGHT_ENTITY
    assert subentry.title == "Front Porch"

    # ── genuinely live and working post-migration, not just registered ──
    final_state = hass.states.get(original_sensor_entity_id)
    assert final_state is not None
    assert final_state.state not in (None, "unknown", "unavailable")


async def test_migration_is_idempotent_on_a_second_setup(hass, freezer):
    """Reloading an already-migrated entry must not re-migrate or touch
    unique_ids a second time -- entry.version already being 2 is the
    guard, confirmed directly rather than just trusted."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = MockConfigEntry(
        domain=DOMAIN, data=OLD_SHAPE_ENTRY_DATA, entry_id="test_migration_reload", version=1
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    subentry_id_before = next(iter(live_entry.subentries.values())).subentry_id
    assert live_entry.version == 2

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    live_entry_after = hass.config_entries.async_get_entry(entry.entry_id)
    subentries_after = list(live_entry_after.subentries.values())
    assert len(subentries_after) == 1
    assert subentries_after[0].subentry_id == subentry_id_before
    assert live_entry_after.version == 2


async def test_fresh_install_has_no_migration_to_do(hass, freezer):
    """A config entry created fresh under the current code (via the real
    config flow, which already creates subentries directly) has no
    CONF_LIGHTS to migrate -- async_migrate_entry's early return for
    entry.version > 1 covers this, checked directly."""
    freezer.move_to("2026-07-04 12:00:00-05:00")
    await hass.config.async_set_time_zone("America/Chicago")

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"region": "us", "categories": {"federal": True}},
        entry_id="test_fresh",
        version=2,
        subentries_data=[
            {
                "subentry_type": LIGHT_SUBENTRY_TYPE,
                "title": "Front Porch",
                "unique_id": None,
                "data": OLD_SHAPE_ENTRY_DATA["lights"][0],
            }
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    live_entry = hass.config_entries.async_get_entry(entry.entry_id)
    assert live_entry.version == 2
    assert len(live_entry.subentries) == 1
