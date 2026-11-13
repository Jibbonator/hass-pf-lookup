# DHL Packstation

Home Assistant integration with a bundled Lovelace card: find packstations
nearby and read the free compartments (S/M/L/XL) of a station.

Everything runs on demand — no polling, no history. The data comes from the
public endpoints behind the DHL postfinder website.

## Features

- **Search** for packstations around a `person.*` entity or around
  coordinates, sorted by distance.
- **Status** of one station: free compartments S/M/L/XL, capacity, opening
  hours, services, model and kind (app / display / post office).
- **Map**: five `device_tracker` entities carry the search results including
  their coordinates, so they show up on the Home Assistant map.
- **Card** (`custom:pf-lookup-card`): tap a person, see the results with their
  distance, expand a row for details, open Google Maps directions, go back.

## Installation

Via the Home Assistant Marketplace:

1. Settings → Marketplace → add repository
2. Add `https://github.com/Jibbonator/hass-pf-lookup` as a custom repository
3. Install the integration and restart Home Assistant
4. Settings → Devices & services → Add integration → "DHL Packstation"
5. The card resource is registered by the integration; use
   `type: custom:pf-lookup-card` in a dashboard

## Setup

The setup assistant offers every person and every GPS capable device tracker.
Only the selected persons are used — new entities never appear on their own.
Radius and number of results are set there and can be changed later through
"Configure".

## Services

| Service | Purpose |
|---|---|
| `pf_lookup.search` | Nearest packstations for a person or coordinates |
| `pf_lookup.status` | Details and free compartments of one station by primary key |
| `pf_lookup.persons` | Persons from the integration options |

`search` and `status` return their result as a service response.

## Card options

```yaml
type: custom:pf-lookup-card
title: Packstation
```

The person list comes from the integration. Without a search the card only
shows the person tiles; after a tap the five results appear, together with the
embedded map showing the person and every result, plus a back button.

## Requirements

- Home Assistant 2026.11 or newer
- Germany (the endpoints only cover German locations)
- A person or device tracker with `latitude`/`longitude`

## Note

The endpoints used here are undocumented and may change at any time.
Unofficial project, use at your own risk.

## License

Private, no license granted.
