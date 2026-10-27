# HA Dutch Trash Calendar

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheGinji&repository=ha-dutch-trash-calendar&category=integration)

Home Assistant integration voor de afvalkalender-API op
<https://trashapi.azurewebsites.net>. Je vult plaats, postcode en huisnummer in en
krijgt per afvalsoort een sensor met de volgende ophaaldatum, een agenda, sensoren voor
"ophaling vandaag/morgen" en een dashboardkaart met containers.

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

- **Per afvalsoort** (Restafval, Gft, Papier, ...): een sensor met de volgende ophaaldatum.
  Attributen: `waste_type`, `days_until`, `days_text`, `upcoming_dates`. Nieuwe soorten die later in
  de kalender verschijnen krijgen automatisch een sensor.
- **Volgende ophaling**: de eerstvolgende datum van alle soorten.
  Attributen: `days_until`, `days_text`, `waste_types`, `waste_types_text`.
- **Ophaling vandaag** en **Ophaling morgen** (binary sensors): aan als er vandaag/morgen iets wordt
  opgehaald. Attributen: `waste_types`, `waste_types_text`. Handig voor automatiseringen en badges.
- **Ophaaldagen** (agenda): alle ophaaldagen als hele-dag-afspraken, zichtbaar in de Home
  Assistant-agenda en bruikbaar als trigger voor automatiseringen.

`days_text` is een leesbare tekst: `Vandaag`, `Morgen` of `Over 4 dagen` (Engels als Home Assistant
niet op Nederlands staat: `Today`, `Tomorrow`, `In 4 days`).

De exacte entity_id's staan onder Instellingen → Apparaten & services → Entiteiten.

Verdwijnt een afvalsoort uit de API (bijvoorbeeld omdat de bron een foutieve regel corrigeert), dan
blijft de bijbehorende sensor als "niet beschikbaar" achter. Verwijder hem dan onder Instellingen →
Entiteiten. Komt de soort terug, dan wordt de sensor vanzelf opnieuw aangemaakt.

## Dashboardkaart met containers

De integratie levert zelf een kaart mee. Je hoeft niets te installeren of als resource toe te voegen:
de integratie zet de kaart zelf bij Instellingen → Dashboards → Resources (bij dashboards in
opslagmodus). Kies bij een nieuwe kaart **HA Dutch Trash Calendar**, of gebruik YAML:

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

Zie je "Custom element doesn't exist"? Herstart Home Assistant en ververs de pagina hard
(Ctrl/Cmd+Shift+R), of reset de frontend-cache in de app. Gebruik je een YAML-dashboard (`mode: yaml`),
voeg dan zelf deze resource toe:

```yaml
resources:
  - url: /trashapi_static/trash-containers-card.js
    type: module
```

## Voorbeeld: badge met "Over 4 dagen"

```yaml
type: entity
entity: sensor.afvalkalender_postcode_huisnummer_restafval
state_content: days_text
```

## Automatiseringen: meldingen en Assist

Kant-en-klare voorbeelden staan in [docs/afval-automatiseringen.md](docs/afval-automatiseringen.md):

- **Pushmelding de avond ervoor** met de knop "Container buiten gezet".
- **Herinneringen** om 21:30 en 06:45, zolang je de container niet als buiten gezet hebt gemarkeerd.
- **Assist**: vraag "welke bak moet er morgen buiten?" of "wanneer wordt restafval opgehaald?".

Het document legt ook uit hoe je ze toevoegt en welke namen (entity-ID's en telefoons) je moet aanpassen.

## Reparatiemeldingen

Kan de API twee keer achter elkaar niet worden bereikt, dan verschijnt onder Instellingen →
Systeem → Reparaties de melding "TrashAPI is niet bereikbaar". Geeft de API geen ophaaldata meer
voor je adres, dan zie je "Geen ophaaldata gevonden" en blijven de laatst bekende gegevens zichtbaar.
De meldingen verdwijnen vanzelf zodra de API weer werkt.

## Licentie

MIT
