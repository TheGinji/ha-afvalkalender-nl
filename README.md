# HA Dutch Trash Calendar

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheGinji&repository=ha-dutch-trash-calendar&category=integration)

Home Assistant integration voor de afvalkalender-API op
<https://trashapi.azurewebsites.net>. Je vult plaats, postcode en huisnummer in en
krijgt per afvalsoort een sensor met de volgende ophaaldatum.

## Installeren via HACS

1. Open HACS → menu (drie puntjes rechtsboven) → **Custom repositories**
2. Repository: `https://github.com/TheGinji/ha-dutch-trash-calendar`, type: **Integration** → **Add**
3. Zoek "HA Dutch Trash Calendar" in HACS en kies **Download**
4. Herstart Home Assistant
5. Instellingen → Apparaten & services → Integratie toevoegen → **HA Dutch Trash Calendar**

Handmatig kan ook: kopieer `custom_components/trashapi` naar `/config/custom_components/`.

## Instellingen

Alle parameters van de API zijn instelbaar, bij het toevoegen én later via de knop **Configureren**:

| Veld | API-parameter | Standaard |
|---|---|---|
| Plaats | `Location` | – |
| Postcode | `ZipCode` | – |
| Huisnummer | `HouseNumber` | – |
| Hele jaar tonen | `ShowWholeYear` | aan |
| Cleanprofs-data ophalen | `GetCleanprofsData` | aan |
| Cache negeren | `IgnoreCache` | uit |
| Verversen elke (uren) | – | 6 |

Meerdere adressen? Voeg de integratie gewoon nog een keer toe.

## Entiteiten

- **Per afvalsoort** (Restafval, Gft, Papier, Grofvuil, ...): een sensor met de volgende ophaaldatum.
  Attributen: `days_until`, `upcoming_dates`. Nieuwe soorten die later in de kalender
  verschijnen krijgen automatisch een sensor.
- **Volgende ophaling**: de eerstvolgende datum van alle soorten.
  Attributen: `days_until`, `waste_types`, `waste_types_text`.

De exacte entity_id's staan onder Instellingen → Apparaten & services → Entiteiten.

## Voorbeeld: melding de avond ervoor

```yaml
alias: Afval - morgen ophaling
triggers:
  - trigger: time
    at: "19:00:00"
conditions:
  - condition: template
    value_template: >
      {{ state_attr('sensor.afvalkalender_postcode_huisnumer_volgende_ophaling', 'days_until') == 1 }}
actions:
  - action: notify.notify
    data:
      message: >
        Morgen wordt opgehaald:
        {{ state_attr('sensor.afvalkalender_postcode_huisnummer_volgende_ophaling', 'waste_types_text') }}
```

## Licentie

MIT
