/**
 * Deliberately hand-written, minimal subset of Home Assistant's frontend
 * `HomeAssistant` interface -- just the fields this panel actually reads,
 * rather than depending on the full `home-assistant-frontend` npm package
 * (a large, fast-moving dependency we'd otherwise have to pin/update).
 *
 * Field shapes confirmed directly against the real frontend source
 * (home-assistant/frontend, `src/types.ts` and
 * `src/data/entity/entity_registry.ts`) at the time this was written --
 * see frontend/README.md for how to re-verify if HA's frontend contract
 * ever changes.
 */

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

/** Matches EntityRegistryDisplayEntry -- the trimmed shape actually handed
 * to panels/cards via hass.entities, NOT the full backend registry entry
 * (no unique_id or config_entry_id here; platform + device_id are what we
 * rely on). */
export interface EntityRegistryDisplayEntry {
  entity_id: string;
  name?: string;
  icon?: string;
  device_id?: string;
  area_id?: string;
  platform?: string;
}

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  entities: Record<string, EntityRegistryDisplayEntry>;
  language?: string;
  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: Record<string, unknown>,
  ): Promise<unknown>;
}

/** The `panel` object HA hands a built-in panel's custom element -- only
 * `config` (what we pass at registration time in frontend.py) matters here. */
export interface PanelInfo {
  config?: Record<string, unknown> | null;
}

/** setConfig()'s argument for the compact Lovelace card -- deliberately
 * just `type` (the "custom:chromacal-card" string Lovelace itself always
 * sends). No other fields: the card is zero-config by design, showing
 * every configured light the same way buildViewModel() already
 * self-discovers them for the panel -- see the plan discussion for why
 * an entity-picker config was decided against for v1. */
export interface ChromaCalCardConfig {
  type: string;
}
