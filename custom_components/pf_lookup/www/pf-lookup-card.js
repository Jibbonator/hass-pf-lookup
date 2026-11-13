const DOMAIN = "pf_lookup";
const DHL_RED = "#d21130";
const DHL_YELLOW = "#ffcc07";
const SIZES = [
  ["s", "S"],
  ["m", "M"],
  ["l", "L"],
  ["xl", "XL"],
];

const STRINGS = {
  en: {
    back: "← Back",
    tapToSearch: "Tap to search",
    nearby: "Packstations nearby",
    loadingPersons: "Loading persons …",
    noPersons: "No persons configured — select them in the integration options.",
    searchingFor: "Searching for {name} …",
    searching: "Searching …",
    searchFailed: "Search failed: {error}",
    loadingDetails: "Loading details …",
    detailsFailed: "Details failed: {error}",
    noResults: "No packstation within the selected radius.",
    resultCount: "{count} results",
    freeTotal: "Free total",
    of: "of",
    open: "Open",
    until: "until {time}",
    asOf: "As of",
    type: "Type",
    model: "Model",
    directions: "➤ Directions",
    justNow: "just now",
    minutesAgo: "{count} min ago",
    hoursAgo: "{count} h ago",
    mapFailed: "Map could not be loaded.",
    services: {
      MOBILE_PARCEL_STAMPS: "Stamps",
      PARCEL_ACCEPTANCE: "Drop-off",
      PARCEL_PICKUP: "Pickup",
      POST_FILIALE_DIREKT: "Post office direct",
      PRINT_CUSTOMS_DUTY_LABEL: "Customs label",
      REROUTING: "Rerouting",
      SEND_UNPACKAGED_RETURNS_FROM_PARTICIPATING_RETAILERS: "Returns",
    },
    kinds: {
      LPS: "App",
      "PS-DE": "Display",
      POSTSTATION: "Post office",
    },
  },
  de: {
    back: "← Zurück",
    tapToSearch: "Tippen zum Suchen",
    nearby: "Packstationen in der Nähe",
    loadingPersons: "Personen werden geladen …",
    noPersons:
      "Keine Personen konfiguriert — bitte in den Optionen der Integration auswählen.",
    searchingFor: "Suche für {name} …",
    searching: "Suche läuft …",
    searchFailed: "Suche fehlgeschlagen: {error}",
    loadingDetails: "Details werden geladen …",
    detailsFailed: "Details fehlgeschlagen: {error}",
    noResults: "Keine Packstation im gewählten Radius.",
    resultCount: "{count} Treffer",
    freeTotal: "Frei gesamt",
    of: "von",
    open: "Öffnung",
    until: "bis {time}",
    asOf: "Stand",
    type: "Art",
    model: "Modell",
    directions: "➤ Navigation",
    justNow: "gerade eben",
    minutesAgo: "vor {count} Min",
    hoursAgo: "vor {count} Std",
    mapFailed: "Karte konnte nicht geladen werden.",
    services: {
      MOBILE_PARCEL_STAMPS: "Briefmarken",
      PARCEL_ACCEPTANCE: "Einwurf",
      PARCEL_PICKUP: "Abholung",
      POST_FILIALE_DIREKT: "Postfiliale direkt",
      PRINT_CUSTOMS_DUTY_LABEL: "Zoll-Label",
      REROUTING: "Umleitung",
      SEND_UNPACKAGED_RETURNS_FROM_PARTICIPATING_RETAILERS: "Retouren",
    },
    kinds: {
      LPS: "App",
      "PS-DE": "Bildschirm",
      POSTSTATION: "Poststation",
    },
  },
};

const STYLE = `
  :host { display: block; }
  .wrap {
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color, #212121);
    border-radius: var(--ha-card-border-radius, 12px);
    padding: 16px;
    box-sizing: border-box;
  }
  header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
  }
  header h2 {
    margin: 0; font-size: 1.15rem; font-weight: 600; flex: 1;
    letter-spacing: .2px;
  }
  .sub { color: var(--secondary-text-color, #727272); font-size: .82rem; margin-top: 2px; }
  button.back {
    border: 0; background: var(--secondary-background-color, #f3f3f3);
    color: var(--primary-text-color, #212121);
    border-radius: 999px; padding: 7px 14px; font-size: .85rem; cursor: pointer;
    display: inline-flex; align-items: center; gap: 6px;
  }
  button.back:hover { filter: brightness(.95); }
  .persons { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
  .person {
    border: 1px solid var(--divider-color, #e0e0e0); border-radius: 14px;
    padding: 14px; cursor: pointer; text-align: left;
    background: linear-gradient(180deg, rgba(210,17,48,.06), transparent 65%);
    transition: transform .08s ease, box-shadow .12s ease;
    color: inherit; font: inherit;
  }
  .person:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,.12); }
  .person .initial {
    width: 34px; height: 34px; border-radius: 10px; background: ${DHL_YELLOW};
    color: ${DHL_RED}; font-weight: 700; display: grid; place-items: center;
    margin-bottom: 10px; font-size: 1rem;
  }
  .person .name { font-weight: 600; }
  .person .hint { color: var(--secondary-text-color, #727272); font-size: .78rem; margin-top: 2px; }
  .empty { color: var(--secondary-text-color, #727272); font-size: .9rem; }

  .results { display: flex; flex-direction: column; gap: 8px; }
  .row {
    border: 1px solid var(--divider-color, #e0e0e0); border-radius: 12px;
    overflow: hidden; background: var(--ha-card-background, transparent);
  }
  .rowhead {
    display: flex; gap: 12px; align-items: center; padding: 11px 13px; cursor: pointer;
  }
  .rowhead:hover { background: rgba(127,127,127,.06); }
  .idx {
    width: 26px; height: 26px; border-radius: 8px; flex: 0 0 26px;
    background: ${DHL_YELLOW}; color: ${DHL_RED};
    display: grid; place-items: center; font-weight: 700; font-size: .8rem;
  }
  .rowmain { flex: 1; min-width: 0; }
  .rowtitle { font-weight: 600; font-size: .92rem; }
  .rowsub {
    color: var(--secondary-text-color, #727272); font-size: .78rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .dist {
    font-variant-numeric: tabular-nums; font-size: .85rem; font-weight: 600;
    color: var(--secondary-text-color, #727272); flex: 0 0 auto;
  }
  .chev { color: var(--secondary-text-color, #727272); font-size: .8rem; flex: 0 0 auto; }
  .details { padding: 0 13px 13px; }
  .badges { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px; }
  .badge {
    background: ${DHL_YELLOW}; border-radius: 10px; padding: 8px 4px; text-align: center;
    color: ${DHL_RED};
  }
  .badge .lbl { font-size: .72rem; font-weight: 700; letter-spacing: .5px; opacity: .85; }
  .badge .val { font-size: 1.05rem; font-weight: 700; font-variant-numeric: tabular-nums; }
  .facts { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: .79rem;
           color: var(--secondary-text-color, #727272); margin-bottom: 8px; }
  .facts b { color: var(--primary-text-color, #212121); font-weight: 600; }
  .chips { display: flex; flex-wrap: wrap; gap: 5px; }
  .chip {
    font-size: .71rem; padding: 3px 8px; border-radius: 999px;
    border: 1px solid var(--divider-color, #e0e0e0);
    color: var(--secondary-text-color, #727272);
  }
  .mapwrap { margin-top: 12px; border-radius: 12px; overflow: hidden; }
  .mapwrap hui-map-card { display: block; height: 260px; }
  .actions { margin-top: 10px; }
  .actions a.nav {
    display: inline-flex; align-items: center; gap: 7px;
    background: ${DHL_RED}; color: #fff; text-decoration: none;
    border-radius: 999px; padding: 8px 16px; font-size: .82rem; font-weight: 600;
  }
  .actions a.nav:hover { filter: brightness(1.08); }
  .spinner { color: var(--secondary-text-color, #727272); font-size: .85rem; padding: 10px 0; }
  [hidden] { display: none !important; }
`;

class PfLookupCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._view = "persons";
    this._persons = null;
    this._results = null;
    this._openKey = null;
    this._details = new Map();
    this._built = false;
    this._busy = false;
  }

  setConfig(config) {
    this._config = config || {};
    this._personsConfig = config?.persons || [];
    this._title = config?.title || "Packstation";
    this._built = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._built) {
      this._build();
    }
    if (this._mapEl) {
      this._mapEl.hass = hass;
    }
  }

  getCardSize() {
    return this._view === "persons" ? 3 : 14;
  }

  _build() {
    this._built = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <div class="wrap">
        <header>
          <div style="flex:1;min-width:0">
            <h2></h2>
            <div class="sub"></div>
          </div>
          <button class="back" hidden>← Back</button>
        </header>
        <div class="persons"></div>
        <div class="results" hidden></div>
        <div class="mapwrap" hidden></div>
      </div>`;

    this._titleEl = this.shadowRoot.querySelector("h2");
    this._subEl = this.shadowRoot.querySelector(".sub");
    this._personsEl = this.shadowRoot.querySelector(".persons");
    this._resultsEl = this.shadowRoot.querySelector(".results");
    this._mapWrap = this.shadowRoot.querySelector(".mapwrap");
    this._backBtn = this.shadowRoot.querySelector("button.back");
    this._backBtn.textContent = this._t("back");
    this._backBtn.addEventListener("click", () => this._showPersons());
    this._titleEl.textContent = this._title;

    this._renderPersons();
  }

  _renderPersons() {
    const persons = this._persons ?? this._personsConfig;
    if (!persons || !persons.length) {
      this._subEl.textContent = "";
      this._personsEl.innerHTML = this._personsTried
        ? `<div class="empty">${esc(this._t("noPersons"))}</div>`
        : `<div class="empty">${esc(this._t("loadingPersons"))}</div>`;
      this._loadPersons();
      return;
    }

    this._subEl.textContent = this._t("tapToSearch");
    this._personsEl.innerHTML = "";
    for (const person of persons) {
      const entityId = person.entity_id ?? person;
      const name = person.name ?? this._nameOf(entityId);
      const button = document.createElement("button");
      button.className = "person";
      button.type = "button";
      button.innerHTML = `
        <div class="initial"></div>
        <div class="name"></div>
        <div class="hint">${esc(this._t("nearby"))}</div>`;
      button.querySelector(".initial").textContent = (name || "?").trim().charAt(0).toUpperCase();
      button.querySelector(".name").textContent = name;
      button.addEventListener("click", () => this._search(entityId, name));
      this._personsEl.appendChild(button);
    }
  }

  _nameOf(entityId) {
    const state = this._hass?.states?.[entityId];
    return state?.attributes?.friendly_name || entityId;
  }

  _lang() {
    const raw = this._hass?.locale?.language || this._hass?.language || "en";
    return String(raw).split("-")[0];
  }

  _table() {
    return STRINGS[this._lang()] || STRINGS.en;
  }

  _t(key, vars = {}) {
    const table = this._table();
    let text = table[key] ?? STRINGS.en[key] ?? key;
    for (const [name, value] of Object.entries(vars)) {
      text = text.split(`{${name}}`).join(String(value));
    }
    return text;
  }

  _label(section, key) {
    const table = this._table();
    return table[section]?.[key] ?? STRINGS.en[section]?.[key] ?? key;
  }

  _ageLabel(timestamp) {
    const then = new Date(timestamp);
    if (Number.isNaN(then.getTime())) {
      return timestamp;
    }
    const minutes = Math.max(0, Math.round((Date.now() - then.getTime()) / 60000));
    if (minutes < 1) {
      return this._t("justNow");
    }
    if (minutes < 60) {
      return this._t("minutesAgo", { count: minutes });
    }
    return this._t("hoursAgo", { count: Math.round(minutes / 60) });
  }

  async _loadPersons() {
    if (this._personsLoading || this._personsTried) {
      return;
    }
    this._personsLoading = true;
    this._personsTried = true;
    try {
      const response = await this._callService("persons", {});
      this._persons = response?.persons ?? [];
    } catch (_err) {
      this._persons = this._personsConfig;
    }
    this._personsLoading = false;
    if (this._view === "persons") {
      this._renderPersons();
    }
  }

  async _callService(service, data) {
    const result = await this._hass.callService(
      DOMAIN,
      service,
      data,
      undefined,
      true,
      true,
    );
    return result?.response ?? result;
  }

  async _search(entityId, name) {
    if (this._busy) {
      return;
    }
    this._busy = true;
    this._view = "results";
    this._openKey = null;
    this._details.clear();
    this._personEntity = entityId;
    this._resultsEl.hidden = false;
    this._personsEl.hidden = true;
    this._backBtn.hidden = false;
    this._subEl.textContent = this._t("searchingFor", { name });
    this._resultsEl.innerHTML = `<div class="spinner">${esc(this._t("searching"))}</div>`;
    this._mapWrap.hidden = true;

    try {
      const response = await this._callService("search", { person: entityId });
      this._results = response?.locations ?? [];
      this._renderResults();
    } catch (err) {
      this._resultsEl.innerHTML = `<div class="empty">${esc(
        this._t("searchFailed", { error: err?.message || err }),
      )}</div>`;
      this._subEl.textContent = "";
    } finally {
      this._busy = false;
    }
  }

  _showPersons() {
    this._view = "persons";
    this._resultsEl.hidden = true;
    this._mapWrap.hidden = true;
    this._personsEl.hidden = false;
    this._backBtn.hidden = true;
    this._renderPersons();
  }

  async _toggleDetails(result, rowEl) {
    if (this._busy) {
      return;
    }
    const key = result.key;
    if (this._openKey === key) {
      this._openKey = null;
      this._renderResults();
      return;
    }

    this._openKey = key;
    this._renderResults();
    const detailEl = this._resultsEl.querySelector(`[data-detail="${cssEsc(key)}"]`);
    if (detailEl && !this._details.has(key)) {
      detailEl.innerHTML = `<div class="spinner">${esc(this._t("loadingDetails"))}</div>`;
    }

    this._busy = true;
    try {
      const detail = await this._callService("status", { key });
      this._details.set(key, detail);
      this._renderResults();
    } catch (err) {
      if (detailEl) {
        detailEl.innerHTML = `<div class="empty">${esc(
          this._t("detailsFailed", { error: err?.message || err }),
        )}</div>`;
      }
    } finally {
      this._busy = false;
    }
  }

  _renderResults() {
    const results = this._results ?? [];
    if (!results.length) {
      this._resultsEl.innerHTML = `<div class="empty">${esc(this._t("noResults"))}</div>`;
      this._subEl.textContent = "";
      this._mapWrap.hidden = true;
      return;
    }

    this._subEl.textContent = this._t("resultCount", { count: results.length });
    this._resultsEl.innerHTML = "";

    results.forEach((result, index) => {
      const key = result.key;
      const open = this._openKey === key;
      const detail = this._details.get(key);

      const row = document.createElement("div");
      row.className = "row";

      const head = document.createElement("div");
      head.className = "rowhead";
      head.innerHTML = `
        <div class="idx">${index + 1}</div>
        <div class="rowmain">
          <div class="rowtitle"></div>
          <div class="rowsub"></div>
        </div>
        <div class="dist"></div>
        <div class="chev">${open ? "▲" : "▼"}</div>`;
      head.querySelector(".rowtitle").textContent = addressLine(result);
      head.querySelector(".rowsub").textContent = `${result.zip} ${result.city}${
        result.district ? ` · ${result.district}` : ""
      }`;
      head.querySelector(".dist").textContent =
        result.distance_m != null ? `${result.distance_m} m` : "";
      head.addEventListener("click", () => this._toggleDetails(result, row));
      row.appendChild(head);

      if (open) {
        const details = document.createElement("div");
        details.className = "details";
        details.dataset.detail = key;
        if (detail) {
          details.innerHTML = this._detailsMarkup(result, detail);
        } else {
          details.innerHTML = `<div class="spinner">${esc(this._t("loadingDetails"))}</div>`;
        }
        row.appendChild(details);
      }

      this._resultsEl.appendChild(row);
    });

    if (!this._mapEl) {
      this._createMap();
    } else {
      this._syncMapPerson();
    }
    this._mapWrap.hidden = false;
  }

  _detailsMarkup(result, detail) {
    const compartments = detail?.compartments ?? {};
    const badges = SIZES.map(([field, label]) => {
      const value = compartments[field];
      return `<div class="badge"><div class="lbl">${label}</div><div class="val">${
        value == null ? "–" : value
      }</div></div>`;
    }).join("");

    const freeTotal = compartments.total_free;
    const capacity = compartments.capacity ?? result.capacity;
    const open24 = detail?.open_all_day;
    const until = detail?.next_action?.open_until;
    const timestamp = detail?.source_timestamp;
    const chips = (detail?.services ?? [])
      .map(
        (service) =>
          `<span class="chip">${esc(this._label("services", service))}</span>`,
      )
      .join("");

    const kind = detail?.station_type
      ? this._label("kinds", detail.station_type)
      : null;
    const latitude = detail?.latitude ?? result.latitude;
    const longitude = detail?.longitude ?? result.longitude;
    const mapsUrl =
      latitude != null && longitude != null
        ? `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`
        : null;

    return `
      <div class="badges">${badges}</div>
      <div class="facts">
        <span>${esc(this._t("freeTotal"))}: <b>${freeTotal ?? "–"}</b>${
          capacity ? ` ${esc(this._t("of"))} ${capacity}` : ""
        }</span>
        <span>${esc(this._t("open"))}: <b>${
          open24 ? "24/7" : until ? esc(this._t("until", { time: until })) : "–"
        }</b></span>
        <span>${esc(this._t("asOf"))}: <b>${
          timestamp ? esc(this._ageLabel(timestamp)) : "–"
        }</b></span>
        ${kind ? `<span>${esc(this._t("type"))}: <b>${esc(kind)}</b></span>` : ""}
        ${detail?.model ? `<span>${esc(this._t("model"))}: <b>${esc(detail.model)}</b></span>` : ""}
      </div>
      ${chips ? `<div class="chips">${chips}</div>` : ""}
      ${
        mapsUrl
          ? `<div class="actions"><a class="nav" href="${mapsUrl}" target="_blank" rel="noopener">${esc(this._t("directions"))}</a></div>`
          : ""
      }`;
  }

  _mapEntities() {
    const states = this._hass?.states ?? {};
    return Object.keys(states)
      .filter((entityId) => states[entityId]?.attributes?.pf_result)
      .sort();
  }

  _mapSignature() {
    return `${this._personEntity ?? ""}|${this._mapEntities().join(",")}`;
  }

  _mapConfig() {
    const entities = [this._personEntity, ...this._mapEntities()].filter(Boolean);
    return {
      type: "map",
      entities,
      default_zoom: 14,
      hours_to_show: 0,
      auto_fit: true,
      theme_mode: "auto",
    };
  }

  async _createMap() {
    this._mapEl = document.createElement("div");
    this._mapWrap.appendChild(this._mapEl);
    try {
      const helpers = await window.loadCardHelpers();
      const mapCard = helpers.createCardElement(this._mapConfig());
      mapCard.hass = this._hass;
      this._mapEl.replaceWith(mapCard);
      this._mapEl = mapCard;
      this._mapSig = this._mapSignature();
    } catch (err) {
      this._mapEl.textContent = this._t("mapFailed");
    }
  }

  _syncMapPerson() {
    if (!this._mapEl || typeof this._mapEl.setConfig !== "function") {
      return;
    }
    const signature = this._mapSignature();
    if (this._mapSig === signature) {
      return;
    }
    try {
      this._mapEl.setConfig(this._mapConfig());
      this._mapSig = signature;
    } catch (_err) {
    }
  }
}

function addressLine(result) {
  const street = [result.street, result.house_no].filter(Boolean).join(" ");
  return street || result.name || "DHL Packstation";
}

function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function cssEsc(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

customElements.define("pf-lookup-card", PfLookupCard);
