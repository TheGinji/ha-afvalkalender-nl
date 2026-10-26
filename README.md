# HA Dutch Trash Calendar

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheGinji&repository=ha-dutch-trash-calendar&category=integration)

Home Assistant integration voor de afvalkalender-API op
<https://trashapi.azurewebsites.net>. Je vult plaats, postcode en huisnummer in en
krijgt per afvalsoort een sensor met de volgende ophaaldatum, plus een dashboardkaart met
containers.

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
  Attributen: `waste_type`, `days_until`, `days_text`, `upcoming_dates`. Nieuwe soorten die later in
  de kalender verschijnen krijgen automatisch een sensor.
- **Volgende ophaling**: de eerstvolgende datum van alle soorten.
  Attributen: `days_until`, `days_text`, `waste_types`, `waste_types_text`.

`days_text` is een leesbare tekst: `Vandaag`, `Morgen` of `Over 4 dagen` (Engels als Home Assistant
niet op Nederlands staat: `Today`, `Tomorrow`, `In 4 days`).

De exacte entity_id's staan onder Instellingen → Apparaten & services → Entiteiten.

## Dashboardkaart met containers

De integratie levert zelf een kaart mee. Je hoeft niets te installeren of als resource toe te voegen.
Kies bij een nieuwe kaart **HA Dutch Trash Calendar**, of gebruik YAML:

```yaml
type: custom:trash-containers-card
title: Afval
```

Zonder verdere opties toont de kaart alle sensoren van de integratie, de eerstvolgende ophaling
vooraan. De containers zijn grijs met een gekleurde deksel: restafval paars, gft groen, papier blauw
(PMD oranje, glas turquoise, grofvuil bruin). Op de ophaaldag springt de container en heeft hij een
gekleurde rand, de dag ervoor krijgt hij een gekleurde achtergrond. Tik op een container voor de details.

| Optie | Uitleg | Standaard |
|---|---|---|
| `title` | Titel boven de kaart | geen |
| `show_date` | Datum (bijv. "di 3 nov") onder het aantal dagen | `true` |
| `sort` | Eerstvolgende ophaling vooraan | `true` |
| `entities` | Eigen lijst en volgorde van sensoren | alle sensoren |
| `colors` | Deksel-kleur per afvalsoort | zie boven |

Voorbeeld met eigen volgorde, naam en kleur:

```yaml
type: custom:trash-containers-card
title: Afval
show_date: false
entities:
  - sensor.afvalkalender_1234ab_12_restafval
  - entity: sensor.afvalkalender_1234ab_12_gft
    name: Groen
    color: "#2e9e4f"
  - sensor.afvalkalender_1234ab_12_papier
colors:
  restafval: "#8e44ad"
```

Zie je de kaart niet na een update? Herstart Home Assistant en ververs de pagina hard
(Ctrl/Cmd+Shift+R), of reset de frontend-cache in de app.

## Voorbeeld: badge met "Over 4 dagen"

```yaml
type: entity
entity: sensor.afvalkalender_postcode_huisnummer_restafval
state_content: days_text
```

## Voorbeeld: melding de avond ervoor

```yaml
alias: Afval - morgen ophaling
triggers:
  - trigger: time
    at: "19:00:00"
conditions:
  - condition: template
    value_template: >
      {{ state_attr('sensor.afvalkalender_postcode_huisnummer_volgende_ophaling', 'days_until') == 1 }}
actions:
  - action: notify.notify
    data:
      message: >
        Morgen wordt opgehaald:
        {{ state_attr('sensor.afvalkalender_postcode_huisnummer_volgende_ophaling', 'waste_types_text') }}
```

### De automatisering toevoegen

1. Ga naar Instellingen → Automatiseringen en scènes → **Automatisering maken** → **Nieuwe automatisering maken**.
2. Tik rechtsboven op het menu met drie puntjes en kies **Bewerken in YAML**.
3. Wis wat er staat, plak je YAML en tik op **Opslaan**.

Pas eerst twee dingen aan, anders doet hij niets:

- **Entity-ID:** `sensor.afvalkalender_postcode_huisnummer_volgende_ophaling` is een voorbeeld.
  Zoek de echte op onder Instellingen → Entiteiten (zoek op "volgende ophaling"). Die heet iets als
  `sensor.afvalkalender_1234ab_12_volgende_ophaling`. Vervang hem op twee plekken.
- **Notify:** `notify.notify` bestaat vaak niet. Zoek je telefoon onder Ontwikkelhulpmiddelen → Acties
  (zoek op "notify"). Die heet iets als `notify.mobile_app_jouw_telefoon`.

Met **Uitvoeren** in het menu van de automatisering kun je de melding direct testen.

## Licentie

MIT
