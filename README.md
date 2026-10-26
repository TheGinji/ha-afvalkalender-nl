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

## Voorbeeld: melding de avond ervoor

```yaml
alias: Afval - morgen ophaling
triggers:
  - trigger: time
    at: "19:00:00"
conditions:
  - condition: state
    entity_id: binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen
    state: "on"
actions:
  - action: notify.notify
    data:
      message: >
        Morgen wordt opgehaald:
        {{ state_attr('binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen', 'waste_types_text') }}
```

### De automatisering toevoegen

1. Ga naar Instellingen → Automatiseringen en scènes → **Automatisering maken** → **Nieuwe automatisering maken**.
2. Tik rechtsboven op het menu met drie puntjes en kies **Bewerken in YAML**.
3. Wis wat er staat, plak je YAML en tik op **Opslaan**.

Pas eerst twee dingen aan, anders doet hij niets:

- **Entity-ID:** de namen met `postcode_huisnummer` zijn een voorbeeld. Zoek de echte op onder
  Instellingen → Entiteiten (zoek op "ophaling morgen"). Die heet iets als
  `binary_sensor.afvalkalender_1234ab_12_ophaling_morgen`. Vervang hem overal in de YAML.
- **Notify:** `notify.notify` bestaat vaak niet. Zoek je telefoon onder Ontwikkelhulpmiddelen → Acties
  (zoek op "notify"). Die heet iets als `notify.mobile_app_jouw_telefoon`.

Met **Uitvoeren** in het menu van de automatisering kun je de melding direct testen.

## Melding met bevestiging ("Container buiten gezet")

Een melding op je telefoon met een knop. Druk je erop, dan stopt de herinnering. Doe je het niet,
dan krijg je 's avonds laat en 's ochtends nog een herinnering.

Maak eerst een helper: Instellingen → Apparaten & services → Helpers → **Helper maken** →
**Schakelaar**, naam `Afval buiten gezet` (wordt `input_boolean.afval_buiten_gezet`).
Maak daarna drie automatiseringen zoals hierboven beschreven. Vervang de entity-ID's en de notify-naam.

**1. Avondmelding met knop**

```yaml
alias: Afval - avondmelding
triggers:
  - trigger: time
    at: "19:00:00"
conditions:
  - condition: state
    entity_id: binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen
    state: "on"
actions:
  - action: input_boolean.turn_off
    target:
      entity_id: input_boolean.afval_buiten_gezet
  - action: notify.mobile_app_jouw_telefoon
    data:
      title: Container buiten zetten
      message: >
        Morgen wordt opgehaald:
        {{ state_attr('binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen', 'waste_types_text') }}
      data:
        tag: afval
        actions:
          - action: AFVAL_BUITEN
            title: Container buiten gezet
```

**2. Bevestiging**

```yaml
alias: Afval - bevestiging
triggers:
  - trigger: event
    event_type: mobile_app_notification_action
    event_data:
      action: AFVAL_BUITEN
actions:
  - action: input_boolean.turn_on
    target:
      entity_id: input_boolean.afval_buiten_gezet
  - action: notify.mobile_app_jouw_telefoon
    data:
      message: clear_notification
      data:
        tag: afval
```

**3. Herinnering (21:30 en 06:45)**

```yaml
alias: Afval - herinnering
triggers:
  - trigger: time
    at: "21:30:00"
  - trigger: time
    at: "06:45:00"
conditions:
  - condition: state
    entity_id: input_boolean.afval_buiten_gezet
    state: "off"
  - condition: or
    conditions:
      - condition: state
        entity_id: binary_sensor.afvalkalender_postcode_huisnummer_ophaling_vandaag
        state: "on"
      - condition: state
        entity_id: binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen
        state: "on"
actions:
  - action: notify.mobile_app_jouw_telefoon
    data:
      title: Container nog niet buiten
      message: >
        {% if is_state('binary_sensor.afvalkalender_postcode_huisnummer_ophaling_vandaag', 'on') -%}
        Vandaag wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_postcode_huisnummer_ophaling_vandaag', 'waste_types_text') }}. Staat de container al buiten?
        {%- else -%}
        Morgen wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen', 'waste_types_text') }}. Heb je de container al buiten gezet?
        {%- endif %}
      data:
        tag: afval
        actions:
          - action: AFVAL_BUITEN
            title: Container buiten gezet
```

## Assist: "Welke bak moet er morgen buiten?"

Twee automatiseringen met een Assist-zin als trigger. Je kunt de vraag typen of inspreken
(Assist moet op Nederlands staan). Vervang de entity-ID's.

**Wat moet er morgen buiten?**

```yaml
alias: Afval - Assist morgen
triggers:
  - trigger: conversation
    command:
      - "welke (bak|container) moet er morgen buiten"
      - "wat wordt er morgen opgehaald"
      - "wanneer wordt het afval opgehaald"
actions:
  - set_conversation_response: >-
      {% set morgen = 'binary_sensor.afvalkalender_postcode_huisnummer_ophaling_morgen' %}
      {% set volgende = 'sensor.afvalkalender_postcode_huisnummer_volgende_ophaling' %}
      {% if is_state(morgen, 'on') -%}
      Zet morgen {{ state_attr(morgen, 'waste_types_text') }} buiten.
      {%- else -%}
      Morgen wordt er niets opgehaald. De volgende ophaling is {{ state_attr(volgende, 'days_text') | lower }}: {{ state_attr(volgende, 'waste_types_text') }}.
      {%- endif %}
```

**Wanneer wordt een bepaalde soort opgehaald?** (bijvoorbeeld "wanneer wordt restafval opgehaald")

```yaml
alias: Afval - Assist per soort
triggers:
  - trigger: conversation
    command:
      - "wanneer wordt {afvalsoort} opgehaald"
actions:
  - set_conversation_response: >-
      {% set soort = (trigger.slots.afvalsoort | default('')) | lower | trim %}
      {% set ns = namespace(sensor=none) %}
      {% for s in states.sensor if s.attributes.waste_type is defined and s.attributes.waste_type | lower == soort %}
      {% set ns.sensor = s %}
      {% endfor %}
      {%- if ns.sensor is none -%}
      Die afvalsoort ken ik niet.
      {%- elif ns.sensor.attributes.days_text is none -%}
      Voor {{ ns.sensor.attributes.waste_type }} is nu geen ophaaldatum bekend.
      {%- else -%}
      {{ ns.sensor.attributes.waste_type }} wordt {{ ns.sensor.attributes.days_text | lower }} opgehaald.
      {%- endif %}
```

## Reparatiemeldingen

Kan de API twee keer achter elkaar niet worden bereikt, dan verschijnt onder Instellingen →
Systeem → Reparaties de melding "TrashAPI is niet bereikbaar". Geeft de API geen ophaaldata meer
voor je adres, dan zie je "Geen ophaaldata gevonden" en blijven de laatst bekende gegevens zichtbaar.
De meldingen verdwijnen vanzelf zodra de API weer werkt.

## Licentie

MIT
