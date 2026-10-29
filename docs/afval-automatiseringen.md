# Afval: meldingen met bevestiging + Assist-vragen

Voorbeeldconfiguratie voor **Afvalkalender NL**. Bestaat uit één helper en vijf
automatiseringen: drie voor pushmeldingen met de knop "Container buiten gezet" en twee
voor vragen aan Assist.

> **Let op:** pas de namen aan voor jouw installatie.
> - Vervang `1234ab_12` door de slug van je eigen postcode en huisnummer.
> - Vervang `notify.mobile_app_telefoon_1` en `notify.mobile_app_telefoon_2` door je eigen
>   telefoons. Zoek ze onder Ontwikkelhulpmiddelen → Acties (zoek op "notify").
> - Heb je maar één telefoon? Verwijder dan in elke automatisering het blok van
>   `telefoon_2`.

## Vereisten

- Home Assistant 2024.11 of nieuwer.
- De Home Assistant Companion-app op elke telefoon die meldingen moet ontvangen.
- De integratie levert deze entiteiten (de namen hieronder gelden als Home Assistant op
  Nederlands staat; in het Engels heten ze bijvoorbeeld `..._pickup_tomorrow`):
  - `binary_sensor.<slug>_ophaling_vandaag`
  - `binary_sensor.<slug>_ophaling_morgen`
  - `sensor.<slug>_volgende_ophaling`
  - per afvalsoort een sensor met de attributen `waste_type`, `days_until`, `days_text`

## 1. Helper (verplicht)

Via de interface: Instellingen → Apparaten & services → Helpers → **Helper maken** →
**Schakelaar**, naam `Afval buiten gezet`. Of in `configuration.yaml`:

```yaml
input_boolean:
  afval_buiten_gezet:
    name: Afval buiten gezet
    icon: mdi:trash-can-outline
```

## 2. Automatiseringen

Deze lijst heeft het formaat van `automations.yaml`. Je kunt hem daar onderaan plakken
(en daarna de configuratie herladen), of elke automatisering los toevoegen: nieuwe
automatisering → menu met drie puntjes → **Bewerken in YAML** → plak één blok zonder de
`- ` voorop (en laat de regel `id:` weg).

```yaml
- id: '1793054101000'
  alias: Afval - avondmelding
  description: Melding met de knop "Container buiten gezet" als er morgen iets wordt opgehaald.
  triggers:
  - trigger: time
    at: '19:00:00'
  conditions:
  - condition: state
    entity_id: binary_sensor.afvalkalender_1234ab_12_ophaling_morgen
    state: 'on'
  actions:
  - action: input_boolean.turn_off
    target:
      entity_id: input_boolean.afval_buiten_gezet
  - action: notify.mobile_app_telefoon_1
    data:
      title: Container buiten zetten
      message: >-
        Morgen wordt opgehaald:
        {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_morgen', 'waste_types_text') }}.
        Houd de melding ingedrukt en kies "Container buiten gezet".
      data:
        tag: afval
        actions:
        - action: AFVAL_BUITEN
          title: Container buiten gezet
  - action: notify.mobile_app_telefoon_2
    data:
      title: Container buiten zetten
      message: >-
        Morgen wordt opgehaald:
        {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_morgen', 'waste_types_text') }}.
        Houd de melding ingedrukt en kies "Container buiten gezet".
      data:
        tag: afval
        actions:
        - action: AFVAL_BUITEN
          title: Container buiten gezet
  mode: single
- id: '1793054102000'
  alias: Afval - bevestiging
  description: Zet de helper aan en wist de melding als op "Container buiten gezet" is gedrukt.
  triggers:
  - trigger: event
    event_type: mobile_app_notification_action
    event_data:
      action: AFVAL_BUITEN
  conditions: []
  actions:
  - action: input_boolean.turn_on
    target:
      entity_id: input_boolean.afval_buiten_gezet
  - action: notify.mobile_app_telefoon_1
    data:
      message: clear_notification
      data:
        tag: afval
  - action: notify.mobile_app_telefoon_2
    data:
      message: clear_notification
      data:
        tag: afval
  mode: single
- id: '1793054103000'
  alias: Afval - herinnering
  description: >-
    Herinnert om 21:30 (als er morgen iets wordt opgehaald) en om 06:45 (als er vandaag iets
    wordt opgehaald), zolang de container nog niet als buiten gezet is gemarkeerd.
  triggers:
  - trigger: time
    at: '21:30:00'
    id: avond
  - trigger: time
    at: '06:45:00'
    id: ochtend
  conditions:
  - condition: state
    entity_id: input_boolean.afval_buiten_gezet
    state: 'off'
  - condition: or
    conditions:
    - condition: and
      conditions:
      - condition: trigger
        id: avond
      - condition: state
        entity_id: binary_sensor.afvalkalender_1234ab_12_ophaling_morgen
        state: 'on'
    - condition: and
      conditions:
      - condition: trigger
        id: ochtend
      - condition: state
        entity_id: binary_sensor.afvalkalender_1234ab_12_ophaling_vandaag
        state: 'on'
  actions:
  - action: notify.mobile_app_telefoon_1
    data:
      title: Container nog niet buiten
      message: >-
        {% if trigger.id == 'ochtend' -%}
        Vandaag wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_vandaag', 'waste_types_text') }}. Houd de melding ingedrukt en kies "Container buiten gezet".
        {%- else -%}
        Morgen wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_morgen', 'waste_types_text') }}. Houd de melding ingedrukt en kies "Container buiten gezet".
        {%- endif %}
      data:
        tag: afval
        actions:
        - action: AFVAL_BUITEN
          title: Container buiten gezet
  - action: notify.mobile_app_telefoon_2
    data:
      title: Container nog niet buiten
      message: >-
        {% if trigger.id == 'ochtend' -%}
        Vandaag wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_vandaag', 'waste_types_text') }}. Houd de melding ingedrukt en kies "Container buiten gezet".
        {%- else -%}
        Morgen wordt opgehaald: {{ state_attr('binary_sensor.afvalkalender_1234ab_12_ophaling_morgen', 'waste_types_text') }}. Houd de melding ingedrukt en kies "Container buiten gezet".
        {%- endif %}
      data:
        tag: afval
        actions:
        - action: AFVAL_BUITEN
          title: Container buiten gezet
  mode: single
- id: '1793054104000'
  alias: Afval - Assist morgen
  description: Beantwoordt de vraag wat er morgen buiten moet.
  triggers:
  - trigger: conversation
    command:
    - wanneer [moet] [de] [volgende] (bak|container|afvalcontainer)
    - wanneer [moet] [de] [volgende] (bak|container|afvalcontainer) aan de weg
    - wanneer [moet] [de] [volgende] (bak|container|afvalcontainer) buiten
    - welke (bak|container|afvalcontainer) moet er [morgen] buiten
    - welke (bak|container|afvalcontainer) moet er [morgen] aan de weg
    - welke (bak|container|afvalcontainer) is [de] volgende
    - wat wordt er [morgen] opgehaald
    - "[wat|wanneer] is de volgende ophaling"
    - wanneer wordt het afval opgehaald
  conditions: []
  actions:
  - set_conversation_response: >-
      {% set morgen = 'binary_sensor.afvalkalender_1234ab_12_ophaling_morgen' %}
      {% set volgende = 'sensor.afvalkalender_1234ab_12_volgende_ophaling' %}
      {% if is_state(morgen, 'on') -%}
      Zet morgen {{ state_attr(morgen, 'waste_types_text') }} buiten.
      {%- elif state_attr(volgende, 'days_text') is none -%}
      Ik weet op dit moment niet wanneer de volgende ophaling is.
      {%- else -%}
      Morgen wordt er niets opgehaald. De volgende ophaling is {{ state_attr(volgende, 'days_text') | lower }}: {{ state_attr(volgende, 'waste_types_text') }}.
      {%- endif %}
  mode: single
- id: '1793054105000'
  alias: Afval - Assist per soort
  description: Beantwoordt de vraag wanneer een bepaalde afvalsoort wordt opgehaald.
  triggers:
  - trigger: conversation
    command:
    - wanneer wordt {afvalsoort} opgehaald
    - wanneer is {afvalsoort} aan de beurt
    - "[over] hoeveel dagen wordt {afvalsoort} opgehaald"
    - over hoeveel dagen is {afvalsoort} aan de beurt
    - hoeveel dagen (tot|voordat) {afvalsoort} wordt opgehaald
    - hoeveel dagen tot {afvalsoort}
    - "[over] hoeveel dagen {afvalsoort}"
    - wanneer {afvalsoort}
  conditions: []
  actions:
  - set_conversation_response: >-
      {% set ruw = (trigger.get('slots', {}).get('afvalsoort', '')) | lower | trim %}
      {% set algemeen = ['afval', 'alles', 'container', 'bak'] %}
      {% set volgende = 'sensor.afvalkalender_1234ab_12_volgende_ophaling' %}
      {% set ns = namespace(sensor=none, algemeen=false) %}
      {% for s in states.sensor if s.attributes.waste_type is defined and s.attributes.upcoming_dates is defined and s.attributes.waste_type | lower in ruw %}
      {% set ns.sensor = s %}
      {% endfor %}
      {% for w in algemeen if w in ruw %}
      {% set ns.algemeen = true %}
      {% endfor %}
      {%- if not ruw -%}
      Noem een afvalsoort, bijvoorbeeld: wanneer wordt restafval opgehaald.
      {%- elif ns.sensor is not none and ns.sensor.attributes.days_text is none -%}
      Voor {{ ns.sensor.attributes.waste_type }} is nu geen ophaaldatum bekend.
      {%- elif ns.sensor is not none -%}
      {{ ns.sensor.attributes.waste_type }} wordt {{ ns.sensor.attributes.days_text | lower }} opgehaald.
      {%- elif ns.algemeen and state_attr(volgende, 'days_text') is none -%}
      Ik weet op dit moment niet wanneer de volgende ophaling is.
      {%- elif ns.algemeen -%}
      De volgende ophaling is {{ state_attr(volgende, 'days_text') | lower }}: {{ state_attr(volgende, 'waste_types_text') }}.
      {%- else -%}
      Die afvalsoort ken ik niet.
      {%- endif %}
  mode: single
```

## Wat elke automatisering doet

| Automatisering | Wat het doet |
|---|---|
| **Afval - avondmelding** | Om 19:00, alleen als er morgen iets wordt opgehaald: zet de helper uit en stuurt een pushmelding met de afvalsoort(en) en de knop **Container buiten gezet**. |
| **Afval - bevestiging** | Vangt de knopdruk op (`mobile_app_notification_action` met `AFVAL_BUITEN`): zet de helper aan en wist de melding op alle telefoons via dezelfde `tag: afval`. |
| **Afval - herinnering** | Zolang de helper uit staat: om 21:30 een herinnering als er morgen iets wordt opgehaald, en om 06:45 als er vandaag iets wordt opgehaald. De tekst kiest zelf "Vandaag" of "Morgen". |
| **Afval - Assist morgen** | Beantwoordt "wat moet er morgen buiten" en "wanneer is de volgende ophaling". Geeft de soorten van morgen, of anders de volgende ophaling met het aantal dagen. |
| **Afval - Assist per soort** | Beantwoordt "wanneer gft", "over hoeveel dagen restafval", "wanneer wordt papier opgehaald". Zoekt de afvalsoort in de zin op en leest `days_text` van de bijbehorende sensor. Algemene woorden (afval, bak, container) verwijzen naar de volgende ophaling. |

## Samenhang van de meldingen

1. 19:00: als er morgen iets wordt opgehaald: melding met knop, helper op `off`.
2. 21:30 (morgen is ophaaldag) en 06:45 (vandaag is ophaaldag), alleen als de helper nog `off` is: herinnering.
3. Jij drukt op de knop: helper `on`, meldingen verdwijnen.
4. De volgende keer dat er de dag erna wordt opgehaald, zet 19:00 de helper weer terug naar `off`.

## Aandachtspunten

- **Waarom `notify.mobile_app_<device>` en niet `notify.send_message`:** alleen de
  device-service kan `tag` en `actions` meegeven; `send_message` ondersteunt die velden
  niet, en dan werkt de knop niet.
- **iOS en Android:** op iOS verschijnen actieknoppen pas na lang indrukken van de melding.
  Dat kan niet worden afgedwongen, vandaar de instructie in de berichttekst. Op Android
  zie je de knop direct; haal de zin "Houd de melding ingedrukt en kies ..." dan gerust weg.
- **Eén helper voor alle telefoons.** Drukt iemand op zijn eigen telefoon, dan stopt de
  herinnering voor iedereen en verdwijnen alle meldingen. Wil je dat per persoon, dan is
  er één helper per persoon nodig en een aparte automatisering per device.
- **Assist-patronen:** `[...]` is een optioneel woord, `(a|b)` een keuze en
  `{afvalsoort}` vrije tekst. Zinnen die met `[` beginnen moeten tussen quotes, anders
  leest YAML ze als lijst.
- **Volgorde in de zinnenlijst:** specifieke zinnen eerst, de kale
  `[over] hoeveel dagen {afvalsoort}` en `wanneer {afvalsoort}` als laatste. Anders
  slokt de vrije tekst de rest van de zin op en antwoordt Assist "Die afvalsoort ken ik
  niet".
- **Assist is patroongebaseerd, geen taalbegrip.** Vrije formuleringen vallen buiten de
  boot; breid de zinnenlijst uit als je merkt dat een vraag niet aankomt. Een LLM-agent
  is alleen nodig als je echt vrij wilt kunnen praten.
