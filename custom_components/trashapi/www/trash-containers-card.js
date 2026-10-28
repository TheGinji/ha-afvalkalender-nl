/* HA Dutch Trash Calendar - dashboard card with container icons.
 *
 *   type: custom:trash-containers-card
 *
 * Without options it shows every sensor of the integration. Options:
 *   title: Afval
 *   show_date: true          # small date under the countdown
 *   group_by_address: true   # with several addresses: one heading per address
 *   sort: true               # soonest pickup first
 *   entities:                # limit / order the containers yourself
 *     - sensor.afvalkalender_1234ab_12_restafval
 *     - entity: sensor.afvalkalender_1234ab_12_gft
 *       name: Groen
 *       color: "#2e9e4f"     # lid colour
 *   colors:                   # lid colour per waste type
 *     restafval: "#8e44ad"
 */

const DEFAULT_COLORS = {
  restafval: "#8e44ad", // paars
  gft: "#2e9e4f", // groen
  papier: "#1e78d6", // blauw
  pmd: "#f28c28",
  plastic: "#f28c28",
  glas: "#16a085",
  textiel: "#d4a017",
  grofvuil: "#8d6e63",
  kerstbo: "#2e7d32",
};
const FALLBACK_COLOR = "#607d8b";

const binSvg = (lid) => `
<svg viewBox="0 0 64 84" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M13 26h38l-4.2 49.2a4 4 0 0 1-4 3.6H21.2a4 4 0 0 1-4-3.6z" fill="#a9afb6"/>
  <path d="M13 26h8.5l3.3 52.8h-3.6a4 4 0 0 1-4-3.6z" fill="#9097a0"/>
  <rect x="27" y="36" width="10" height="3" rx="1.5" fill="#0000002b"/>
  <rect x="27" y="44" width="10" height="3" rx="1.5" fill="#0000002b"/>
  <rect x="27" y="52" width="10" height="3" rx="1.5" fill="#0000002b"/>
  <rect x="20" y="8" width="24" height="9" rx="4.5" fill="${lid}"/>
  <rect x="20" y="8" width="24" height="9" rx="4.5" fill="#00000030"/>
  <rect x="8" y="14" width="48" height="14" rx="4.5" fill="${lid}"/>
  <rect x="8" y="14" width="48" height="5" rx="2.5" fill="#ffffff38"/>
  <circle cx="21" cy="79" r="5" fill="#2f343a"/>
  <circle cx="43" cy="79" r="5" fill="#2f343a"/>
  <circle cx="21" cy="79" r="2" fill="#7b838c"/>
  <circle cx="43" cy="79" r="2" fill="#7b838c"/>
</svg>`;

const isTrashSensor = (st) =>
  st && st.attributes && "days_until" in st.attributes && "upcoming_dates" in st.attributes;

const escapeHtml = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

class TrashContainersCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._sig = null;
  }

  setConfig(config) {
    this._config = { show_date: true, sort: true, ...config };
    this._sig = null;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    // Masonry view: roughly 4 units per row of containers, plus headings
    return this._cardSize || 4;
  }

  getGridOptions() {
    // "auto": the card is as tall as its content (several rows when there are many containers)
    return { columns: 12, rows: "auto", min_columns: 6 };
  }

  static getStubConfig() {
    return {};
  }

  _color(type, override) {
    if (override) return override;
    const key = String(type || "").toLowerCase();
    const custom = this._config.colors || {};
    for (const [k, v] of Object.entries(custom)) if (key.includes(k.toLowerCase())) return v;
    for (const [k, v] of Object.entries(DEFAULT_COLORS)) if (key.includes(k)) return v;
    return FALLBACK_COLOR;
  }

  _items() {
    const hass = this._hass;
    if (!hass || !this._config) return [];
    let refs = this._config.entities;
    if (!refs || !refs.length) {
      refs = Object.keys(hass.states).filter((id) => id.startsWith("sensor.") && isTrashSensor(hass.states[id]));
    }
    const lang = hass.locale?.language || hass.language || undefined;
    const items = [];
    for (const ref of refs) {
      const opts = typeof ref === "string" ? { entity: ref } : ref;
      const st = hass.states[opts.entity];
      if (!st) continue;
      const a = st.attributes || {};
      const type = opts.name || a.waste_type || String(a.friendly_name || opts.entity).split(" ").pop();
      const days = typeof a.days_until === "number" ? a.days_until : null;
      let dateLabel = "";
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(st.state);
      if (m && this._config.show_date) {
        const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
        dateLabel = d.toLocaleDateString(lang, { weekday: "short", day: "numeric", month: "short" });
      }
      const friendly = String(a.friendly_name || "");
      const group =
        a.waste_type && friendly.endsWith(a.waste_type)
          ? friendly.slice(0, friendly.length - a.waste_type.length).trim()
          : "";
      items.push({
        id: opts.entity,
        type,
        group,
        days,
        text: a.days_text || (days === null ? "–" : String(days)),
        dateLabel,
        color: this._color(type, opts.color),
      });
    }
    if (this._config.sort) items.sort((x, y) => (x.days ?? 9999) - (y.days ?? 9999));
    return items;
  }

  _render() {
    if (!this._config || !this._hass) return;
    const items = this._items();
    const sig = JSON.stringify([items, this._config.title, this._config.group_by_address]);
    if (sig === this._sig) return;
    this._sig = sig;

    const renderItem = (i) => {
      const cls = i.days === 0 ? "today" : i.days === 1 ? "tomorrow" : i.days === null ? "none" : "";
      return `
        <div class="item ${cls}" data-entity="${escapeHtml(i.id)}" style="--lid:${escapeHtml(i.color)}">
          ${binSvg(i.color)}
          <div class="type">${escapeHtml(i.type)}</div>
          <div class="when">${escapeHtml(i.text)}</div>
          ${i.dateLabel ? `<div class="date">${escapeHtml(i.dateLabel)}</div>` : ""}
        </div>`;
    };

    // With several addresses: one heading per address, in a fixed (alphabetical) order
    const groups = [...new Set(items.map((i) => i.group))].sort((x, y) => x.localeCompare(y));
    const showHeadings = this._config.group_by_address !== false && groups.length > 1;

    let body;
    let rows = 0;
    if (!items.length) {
      body = '<div class="empty">Geen afvalsensoren gevonden</div>';
      rows = 1;
    } else if (showHeadings) {
      body = groups
        .map((g) => {
          const own = items.filter((i) => i.group === g);
          rows += 1 + Math.ceil(own.length / 4);
          return `<div class="group">${escapeHtml(g || "Overig")}</div><div class="row">${own.map(renderItem).join("")}</div>`;
        })
        .join("");
    } else {
      rows = Math.ceil(items.length / 4);
      body = `<div class="row">${items.map(renderItem).join("")}</div>`;
    }
    this._cardSize = (this._config.title ? 1 : 0) + Math.max(1, rows) * 4;

    this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 16px; }
        .title { font-size: 1.15rem; font-weight: 600; margin: 0 0 12px 4px; color: var(--primary-text-color); }
        .group { font-size: .85rem; font-weight: 600; letter-spacing: .02em; margin: 10px 4px 6px;
                 color: var(--secondary-text-color); }
        .group:first-of-type { margin-top: 0; }
        .row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: space-around; }
        .item { flex: 1 1 0; min-width: 78px; max-width: 150px; display: flex; flex-direction: column;
                align-items: center; text-align: center; padding: 10px 6px 8px; cursor: pointer;
                border-radius: 14px; border: 2px solid transparent; box-sizing: border-box; }
        .item.tomorrow { background: color-mix(in srgb, var(--lid) 14%, transparent); }
        .item.today { background: color-mix(in srgb, var(--lid) 24%, transparent); border-color: var(--lid); }
        .item.none { opacity: .45; }
        svg { width: 56px; height: 74px; }
        .today svg { animation: hop 1.6s ease-in-out infinite; transform-origin: 50% 100%; }
        .type { font-weight: 600; margin-top: 6px; color: var(--primary-text-color); }
        .when { font-size: .9rem; color: var(--primary-text-color); }
        .today .when, .tomorrow .when { font-weight: 700; }
        .date { font-size: .8rem; color: var(--secondary-text-color); }
        .empty { padding: 8px; color: var(--secondary-text-color); }
        @keyframes hop { 0%, 100% { transform: translateY(0) } 50% { transform: translateY(-5px) } }
        @media (prefers-reduced-motion: reduce) { .today svg { animation: none; } }
      </style>
      <ha-card>
        ${this._config.title ? `<div class="title">${escapeHtml(this._config.title)}</div>` : ""}
        ${body}
      </ha-card>`;

    this.shadowRoot.querySelectorAll(".item").forEach((el) =>
      el.addEventListener("click", () =>
        this.dispatchEvent(
          new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId: el.dataset.entity } })
        )
      )
    );
  }
}

if (!customElements.get("trash-containers-card")) {
  customElements.define("trash-containers-card", TrashContainersCard);
}
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "trash-containers-card")) {
  window.customCards.push({
    type: "trash-containers-card",
    name: "HA Dutch Trash Calendar",
    description: "Afvalcontainers met gekleurde deksels en het aantal dagen tot de ophaling",
  });
}
