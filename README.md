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
Vereist Home Assistant 2024.11 of nieuwer.

## Instellingen

Bij het toevoegen vul je het adres en de API-instellingen in. Daarna pas je ze apart aan:

- **Adres wijzigen** (bijvoorbeeld na een verhuizing): Instellingen → Apparaten & services →
  HA Dutch Trash Calendar → menu met drie puntjes → **Herconfigureren**.
- **API-instellingen**: de knop **Configureren**.

| Veld | API-parameter | Standaard | Aan te passen via |
|---|---|---|---|
| Plaats | `Location` | – | Herconfigureren |
| Postcode | `ZipCode` | – | Herconfigureren |
| Huisnummer | `HouseNumber` | – | Herconfigureren |
| Hele jaar tonen | `ShowWholeYear` | aan | Configureren |
| Cleanprofs-data ophalen | `GetCleanprofsData` | aan | Configureren |
| Cache negeren | `IgnoreCache` | uit | Configureren |
| Verversen elke (uren) | – | 6 | Configureren |

### Meerdere adressen

Voeg de integratie gewoon nog een keer toe (Instellingen → Apparaten & services → **Dienst
toevoegen**). Elk adres krijgt een eigen apparaat met eigen sensoren en een eigen agenda. Hetzelfde
adres twee keer toevoegen kan niet.

Let op bij het gebruik:

- **De dashboardkaart** laat alle adressen zien, elk onder een eigen kopje (zie hieronder).
- **Automatiseringen** verwijzen naar de entity-ID's van één adres. Voor een tweede adres maak je dus
  een eigen kopie met de entity-ID's van dat adres.
- **Assist "per soort"** (uit `docs/`) zoekt over alle adressen en geeft de laatste treffer. Met twee
  adressen kan het antwoord dus bij het andere adres horen.

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

## Hoe worden de gegevens ververst?

- De integratie vraagt de API om de zoveel uur om de kalender (standaard elke **6 uur**, instelbaar
  van 1 tot 48 uur via **Configureren**). Dat is voldoende, want ophaaldagen veranderen zelden.
- De sensoren, binary sensors en de agenda springen **elke nacht kort na 00:00** vanzelf door naar
  de volgende datum, zonder nieuwe API-aanroep. "Morgen" wordt dus vanzelf "Vandaag".
- Direct verversen kan met de actie `homeassistant.update_entity` op een van de sensoren van de
  integratie. Met de optie **Cache negeren** vraag je de API om haar eigen cache over te slaan.

## Dashboardkaart met containers

De integratie levert zelf een kaart mee. Je hoeft niets te installeren of als resource toe te voegen:
de integratie zet de kaart zelf bij Instellingen → Dashboards → Resources (bij dashboards in
opslagmodus). Kies bij een nieuwe kaart **HA Dutch Trash Calendar** en stel hem in met de
**visuele editor**, of gebruik YAML:

```yaml
type: custom:trash-containers-card
title: Afval
```

Zonder verdere opties toont de kaart alle sensoren van de integratie, de eerstvolgende ophaling
vooraan. De containers zijn grijs met een gekleurde deksel: restafval paars, gft groen, papier blauw
(PMD oranje, glas turquoise, grofvuil bruin). Op de ophaaldag springt de container en heeft hij een
gekleurde rand, de dag ervoor krijgt hij een gekleurde achtergrond. Tik op een container voor de details.
De kaart is zo hoog als zijn inhoud, ook bij meerdere rijen.

Heb je **meer dan één adres**, dan krijgt elk adres een eigen kopje boven zijn containers. In de
visuele editor kun je per adres de **naam** aanpassen (bijvoorbeeld "Thuis" in plaats van
"Afvalkalender 1234AB 12") en het adres **aan of uit zetten**. Met "Kopje per adres tonen" zet je de
kopjes helemaal uit. De visuele editor stelt titel, datum, volgorde, kopjes en adressen in; `entities`
en `colors` stel je in YAML in.

| Optie | Uitleg | Standaard |
|---|---|---|
| `title` | Titel boven de kaart | geen |
| `show_date` | Datum (bijv. "di 3 nov") onder het aantal dagen | `true` |
| `sort` | Eerstvolgende ophaling vooraan | `true` |
| `group_by_address` | Bij meerdere adressen een kopje per adres | `true` |
| `addresses` | Per adres een eigen `name` en `show: false` om het adres te verbergen | alle adressen, met de naam van het apparaat |
| `entities` | Eigen lijst en volgorde van sensoren | alle sensoren |
| `colors` | Deksel-kleur per afvalsoort | zie boven |

Voorbeeld met twee adressen, eigen namen en een verborgen adres:

```yaml
type: custom:trash-containers-card
title: Afval
addresses:
  Afvalkalender 1234AB 12:
    name: Thuis
  Afvalkalender 5678CD 3:
    show: false
```

De sleutel onder `addresses` is de naam van het apparaat, zoals de visuele editor die toont.

Voorbeeld met eigen volgorde, naam en kleur per container:

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

## Toepassingen

- Een dashboard of wandpaneel dat in één oogopslag laat zien welke container als eerste buiten moet.
- Een melding op je telefoon de avond ervoor, met een herinnering als je de container nog niet buiten
  hebt gezet.
- De ophaaldagen in de gedeelde gezinsagenda, door de agenda-entiteit te laten tonen of te
  synchroniseren.
- Vragen aan Assist ("welke bak moet er morgen buiten?").
- Een lamp of display die de avond ervoor een kleur toont, met de sensor "Ophaling morgen" als
  trigger.

## Reparatiemeldingen

Kan de API twee keer achter elkaar niet worden bereikt, dan verschijnt onder Instellingen →
Systeem → Reparaties de melding "TrashAPI is niet bereikbaar". Geeft de API geen ophaaldata meer
voor je adres, dan zie je "Geen ophaaldata gevonden" en blijven de laatst bekende gegevens zichtbaar.
De meldingen verdwijnen vanzelf zodra de API weer werkt.

## Bekende beperkingen

- De integratie is **niet verbonden met een gemeente of afvalinzamelaar** en is afhankelijk van de
  externe TrashAPI. Valt die weg of verandert hij, dan werkt de integratie niet meer. Voor welke
  gemeenten de API gegevens heeft, bepaalt de API.
- Je krijgt alleen wat de API teruggeeft. **Afvalsoorten kunnen verdwijnen of een andere naam krijgen**
  als de bron wordt aangepast. Ophalingen op aanvraag (bijvoorbeeld grofvuil) staan er alleen in als
  de API ze levert.
- Er zijn alleen **datums, geen tijdstippen**. Rond de **jaarwisseling** kan het even duren voordat de
  nieuwe kalender beschikbaar is; de laatst bekende gegevens blijven dan zichtbaar.
- Gegevens worden periodiek opgehaald; er zijn **geen directe updates**.
- De kaart kent kleuren voor veelvoorkomende soorten. Onbekende soorten krijgen een neutrale kleur,
  die je met `colors` kunt aanpassen.
- Vanaf versie 1.5.0 worden de instellingen bij de eerste start automatisch omgezet naar een nieuw
  formaat (adres apart van de API-instellingen). **Terug naar een oudere versie** werkt daarna niet
  meer zonder de integratie opnieuw toe te voegen. Maak een back-up als je dat kunt willen.

## Probleemoplossing

- **Sensoren zijn "niet beschikbaar".** Kijk onder Instellingen → Systeem → Reparaties en in het
  logboek (zoek op `trashapi`). Open de API in je browser om te zien of hij antwoordt:
  `https://trashapi.azurewebsites.net/Trash?Location=PLAATS&ZipCode=1234AB&HouseNumber=12&ShowWholeYear=true&GetCleanprofsData=true&IgnoreCache=false`
- **"Geen ophaaldata gevonden" bij het toevoegen of herconfigureren.** Controleer de postcode (zonder
  spatie), het huisnummer en de plaatsnaam via de link hierboven.
- **Een afvalsoort is weg of "niet beschikbaar".** Verwijder de oude sensor onder Instellingen →
  Entiteiten (zie "Entiteiten").
- **De kaart toont een foutmelding.** Zie de tips bij "Dashboardkaart met containers".
- **Meer details in het logboek.** Zet dit in `configuration.yaml` en herstart:

  ```yaml
  logger:
    default: warning
    logs:
      custom_components.trashapi: debug
  ```

- **Een probleem melden.** Download eerst de diagnostische gegevens: Instellingen → Apparaten &
  services → HA Dutch Trash Calendar → menu met drie puntjes → **Diagnostische gegevens downloaden**.
  Plaats, postcode en huisnummer worden daarin automatisch weggelaten. Voeg het bestand toe aan je
  [melding op GitHub](https://github.com/TheGinji/ha-dutch-trash-calendar/issues).

## Verwijderen

1. Instellingen → Apparaten & services → **HA Dutch Trash Calendar** → menu met drie puntjes naast
   de invoer → **Verwijderen**. De sensoren en de agenda verdwijnen daarmee.
2. Wil je ook de bestanden weghalen? Open HACS → HA Dutch Trash Calendar → menu → **Verwijderen** en
   herstart Home Assistant.
3. Optioneel: de dashboardkaart staat nog als resource onder Instellingen → Dashboards → menu →
   **Resources**. Verwijder `/trashapi_static/trash-containers-card.js` daar zelf als je wilt.
   Eigen automatiseringen en helpers (zoals uit `docs/`) blijven staan en moet je zelf opruimen.

## Kwaliteit

Home Assistant beoordeelt integraties met de
[kwaliteitsschaal](https://www.home-assistant.io/docs/quality_scale/) (Bronze, Silver, Gold en
Platinum). Voor custom integrations zoals deze bestaat daar officieel **geen score** voor, dus dit
project is **niet officieel erkend**. Het is wel gebouwd met de regels van **Bronze, Silver en Gold**
in gedachte en daar zelf tegen getoetst. Regels die niet van toepassing zijn op een online dienst
zonder apparaten (zoals het automatisch ontdekken van apparaten) zijn overgeslagen.

Wat dat in de praktijk oplevert:

- **Bronze, een degelijke basis:** instellen via de interface, het adres wordt gecontroleerd bij het
  toevoegen, eenduidige entiteiten met een uniek ID en duidelijke documentatie.
- **Silver, betrouwbaar in het dagelijks gebruik:** valt de API uit, dan worden de entiteiten netjes
  "niet beschikbaar" en herstelt de integratie zichzelf, en een reparatiemelding laat zien wat er
  aan de hand is. Bij elke wijziging draaien automatische tests (met minstens 95% dekking) en
  de validatie van Home Assistant en HACS.
- **Gold, de beste ervaring:** het adres is te wijzigen via Herconfigureren, de teksten zijn vertaald
  (Nederlands en Engels), er is een diagnostics-download die je adres weglaat, en de documentatie
  bevat voorbeelden, bekende beperkingen en probleemoplossing.

**Platinum is bewust niet nagestreefd.** Van de Platinum-regels ontbreekt alleen strikte typering:
alle code volledig voorzien van type-annotaties en daarop gecontroleerd met `mypy`. Voor deze
integratie levert dat te weinig op om de extra last te rechtvaardigen:

- De code is klein en overzichtelijk, en de automatische tests controleren al het gedrag op de
  plekken waar fouten het vaakst voorkomen.
- De typecontrole draait tegen de nieuwste Home Assistant. Past Home Assistant zijn eigen typen aan,
  dan kan de controle falen zonder dat er hier iets mis is. Dat kost onderhoud zonder dat het de
  gebruiker iets oplevert.
- Voor de gebruiker verandert er niets: strikte typering maakt de integratie niet betrouwbaarder,
  sneller of makkelijker in gebruik. De winst die bij een integratie als deze telt, zit al in de
  niveaus Bronze tot en met Gold.

## Licentie

MIT

## Credits

- **Claude** (Anthropic): AI-assistent die samen met de eigenaar de integratie heeft ontworpen en
  geschreven: code, dashboardkaart, vertalingen, tests en documentatie.
- **OpenCode** met het model **Big Pickle**: AI-codeerassistent in Home Assistant zelf. Gebruikt om de
  code te reviewen en de integratie in een echte installatie te testen.
