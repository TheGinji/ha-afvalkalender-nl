# Afvalkalender NL

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Home Assistant 2024.11+](https://img.shields.io/badge/Home%20Assistant-2024.11%2B-41BDF5.svg)](https://www.home-assistant.io)
[![Release](https://img.shields.io/github/v/release/TheGinji/ha-afvalkalender-nl)](https://github.com/TheGinji/ha-afvalkalender-nl/releases)
[![Tests](https://github.com/TheGinji/ha-afvalkalender-nl/actions/workflows/tests.yaml/badge.svg)](https://github.com/TheGinji/ha-afvalkalender-nl/actions/workflows/tests.yaml)
[![Validate](https://github.com/TheGinji/ha-afvalkalender-nl/actions/workflows/validate.yaml/badge.svg)](https://github.com/TheGinji/ha-afvalkalender-nl/actions/workflows/validate.yaml)
[![Licentie: MIT](https://img.shields.io/github/license/TheGinji/ha-afvalkalender-nl)](LICENSE)
[![Sterren](https://img.shields.io/github/stars/TheGinji/ha-afvalkalender-nl?style=flat)](https://github.com/TheGinji/ha-afvalkalender-nl/stargazers)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=TheGinji&repository=ha-afvalkalender-nl&category=integration)

**De afvalkalender voor Home Assistant.** Zie in één oogopslag welke container er als eerste buiten
moet: restafval, gft, papier, pmd en meer, als sensoren, agenda en een dashboardkaart met containers.
Je vult alleen je plaats, postcode en huisnummer in. De gegevens komen van de
[TrashAPI](https://trashapi.azurewebsites.net).

*English: Afvalkalender NL is a Home Assistant custom integration (HACS) for Dutch waste collection
calendars. It gives you sensors per waste type, a calendar, "pickup today/tomorrow" sensors, a dashboard
card with a visual editor, a refresh button and support for several addresses. Netherlands only.*

## Wat krijg je?

- **Een sensor per afvalsoort** met de volgende ophaaldatum, het aantal dagen en een leesbare tekst
  ("Morgen", "Over 4 dagen").
- **Een agenda** met alle ophaaldagen, **sensoren "Ophaling vandaag" en "Ophaling morgen"** voor
  automatiseringen, en een **knop "Nu verversen"**.
- **Een dashboardkaart met containers** in gekleurde deksels, met een visuele editor. Op de
  ophaaldag springt de container.
- **Meerdere adressen**, elk met eigen sensoren, een eigen kopje op de kaart en eigen keuzes welke
  afvalsoorten je ziet.
- **Meldingen en Assist**: een pushmelding de avond ervoor met de knop "Container buiten gezet" en
  vragen als "welke bak moet er morgen buiten?" (kant-en-klare voorbeelden).
- **Reparatiemeldingen en diagnostics** als de API niet werkt, in het Nederlands en Engels.

## Is dit de juiste integratie voor jou?

Er zijn meer afvalintegraties voor Home Assistant, met een andere aanpak. Afvalbeheer ondersteunt veel
Nederlandse en Belgische afvalinzamelaars waaruit je kiest, Afvalwijzer haalt gegevens van
mijnafvalwijzer.nl en afvalstoffendienstkalender.nl, en de Waste Collection Schedule is een raamwerk
voor veel landen en inzamelaars. Zoek ze in HACS als je daar meer aan hebt.

**Afvalkalender NL werkt met één bron, de TrashAPI.** Je hoeft geen inzamelaar te kiezen en geeft
alleen plaats, postcode en huisnummer in. Of jouw adres wordt ondersteund, bepaalt de API. Test dat
eerst door de link onder "Probleemoplossing" met jouw adres in je browser te openen. Krijg je daar
ophaaldata terug, dan werkt deze integratie ook. De integratie is gemaakt voor Nederlandse adressen;
België is niet getest.

## Installeren via HACS

1. Open HACS → menu (drie puntjes rechtsboven) → **Custom repositories**
2. Repository: `https://github.com/TheGinji/ha-afvalkalender-nl`, type: **Integration** → **Add**
3. Zoek "Afvalkalender NL" in HACS en kies **Download**
4. Herstart Home Assistant
5. Instellingen → Apparaten & services → Integratie toevoegen → **Afvalkalender NL**

Handmatig kan ook: kopieer `custom_components/trashapi` naar `/config/custom_components/`.
Vereist Home Assistant 2024.11 of nieuwer.

*Eerder geïnstalleerd als "HA Dutch Trash Calendar"? Dat is dezelfde integratie met een nieuwe naam en
repository. Je instellingen en entiteiten blijven bestaan. Verschijnt de update niet in HACS, voeg dan
de nieuwe repository hierboven toe.*

## Instellen

Bij het toevoegen vul je het adres en de API-instellingen in. Daarna pas je ze apart aan:

- **Adres wijzigen** (bijvoorbeeld na een verhuizing): Instellingen → Apparaten & services →
  Afvalkalender NL → menu met drie puntjes → **Herconfigureren**.
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
- **Nu verversen** (knop): haalt de kalender direct opnieuw op en slaat daarbij de cache van de API
  over. De knop blijft bruikbaar als de API even niet bereikbaar was.
- **Laatst bijgewerkt** (sensor, diagnostisch): het tijdstip van de laatste geslaagde update. Deze
  sensor staat **standaard uit**; zet hem aan onder Instellingen → Apparaten & services → Entiteiten
  als je hem wilt zien. Na een mislukte update blijft hij het laatste succes tonen.

`days_text` is een leesbare tekst: `Vandaag`, `Morgen` of `Over 4 dagen` (Engels als Home Assistant
niet op Nederlands staat: `Today`, `Tomorrow`, `In 4 days`).

De exacte entity_id's staan onder Instellingen → Apparaten & services → Entiteiten.

Verdwijnt een afvalsoort uit de API (bijvoorbeeld omdat de bron een foutieve regel corrigeert), dan
blijft de bijbehorende sensor als "niet beschikbaar" achter. Verwijder hem dan onder Instellingen →
Entiteiten. Komt de soort terug, dan wordt de sensor vanzelf opnieuw aangemaakt.

### Hoe worden de gegevens ververst?

- De integratie vraagt de API om de zoveel uur om de kalender (standaard elke **6 uur**, instelbaar
  van 1 tot 48 uur via **Configureren**). Dat is voldoende, want ophaaldagen veranderen zelden.
- De sensoren, binary sensors en de agenda springen **elke nacht kort na 00:00** vanzelf door naar
  de volgende datum, zonder nieuwe API-aanroep. "Morgen" wordt dus vanzelf "Vandaag".
- Direct verversen kan met de knop **Nu verversen**. Die vraagt de API om haar eigen cache over te
  slaan, ook als je de optie **Cache negeren** uit hebt staan. Voor automatiseringen kan ook de actie
  `button.press` op die knop, of `homeassistant.update_entity` op een van de sensoren.

## Dashboardkaart met containers

De integratie levert zelf een kaart mee. Je hoeft niets te installeren of als resource toe te voegen:
de integratie zet de kaart zelf bij Instellingen → Dashboards → Resources (bij dashboards in
opslagmodus). Kies bij een nieuwe kaart **Afvalkalender NL** en stel hem in met de **visuele editor**,
of gebruik YAML:

```yaml
type: custom:trash-containers-card
title: Afval
```

Zonder verdere opties toont de kaart alle sensoren van de integratie, de eerstvolgende ophaling
vooraan. De containers zijn grijs met een gekleurde deksel; de kleuren stel je zelf in per afvalsoort
(zie "Kleuren van de deksel"). Op de ophaaldag springt de container en heeft hij een gekleurde rand, de
dag ervoor krijgt hij een gekleurde achtergrond. Tik op een container voor de details. De kaart is zo
hoog als zijn inhoud, ook bij meerdere rijen.

Heb je **meer dan één adres**, dan krijgt elk adres een eigen kopje boven zijn containers. In de
visuele editor heeft elk adres een eigen blok waarin je:
- de **naam** van het kopje aanpast (bijvoorbeeld "Thuis" in plaats van "Afvalkalender 1234AB 12");
- het **hele adres** aan of uit zet;
- per **afvalsoort** aan of uit zet wat dat adres laat zien. Heb je bij een adres geen gft, of alleen
  papier, dan zet je de rest uit.

Met "Kopje per adres tonen" zet je de kopjes helemaal uit. De visuele editor stelt titel, datum,
volgorde, kopjes, adressen, afvalsoorten per adres en deksel-kleuren in; `entities` stel je in YAML in.

| Optie | Uitleg | Standaard |
|---|---|---|
| `title` | Titel boven de kaart | geen |
| `show_date` | Datum (bijv. "di 3 nov") onder het aantal dagen | `true` |
| `sort` | Eerstvolgende ophaling vooraan | `true` |
| `group_by_address` | Bij meerdere adressen een kopje per adres | `true` |
| `addresses` | Per adres: eigen `name`, `show: false` om het adres te verbergen en `hide: [gft]` om afvalsoorten alleen bij dat adres te verbergen | alle adressen en soorten, met de naam van het apparaat |
| `entities` | Eigen lijst en volgorde van sensoren | alle sensoren |
| `colors` | Deksel-kleur per afvalsoort | zie "Kleuren van de deksel" |

Voorbeeld met twee adressen: het eerste krijgt een eigen naam en geen gft, het tweede laat alleen
papier zien:

```yaml
type: custom:trash-containers-card
title: Afval
addresses:
  Afvalkalender 1234AB 12:
    name: Thuis
    hide: [gft]
  Afvalkalender 5678CD 3:
    name: Voortuin
    hide: [restafval, gft]
```

De sleutel onder `addresses` is de naam van het apparaat, zoals de visuele editor die toont. Bij `hide`
gebruik je de naam van de afvalsoort in kleine letters. Zet je alles van alle adressen uit, dan zegt de
kaart dat er geen afvalsensoren zijn.

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

### Kleuren van de deksel

De kleuren van afvalcontainers verschillen **per gemeente**. Er is geen landelijke standaard, en de
TrashAPI geeft geen kleuren door. De kaart begint daarom met een standaard die je aanpast aan jouw
gemeente:

| Soort | Standaard |
|---|---|
| Gft | groen |
| Papier | blauw |
| PMD en plastic | oranje |
| Restafval | paars (bijvoorbeeld in veel Friese gemeenten; elders is restafval vaak grijs of zwart) |
| Glas, textiel, grofvuil, kerstbomen | een eigen keuze zonder standaard: turquoise, geel, bruin en groen |
| Andere soorten | grijsblauw |

**Aanpassen in de visuele editor:** open het blok **Kleur van de deksel** en kies per afvalsoort een
kleur uit de lijst, of "Standaard". De kleur geldt voor alle adressen.

**Aanpassen in YAML:** gebruik `colors:` met de naam van de soort in kleine letters. Elke hex-kleur kan:

```yaml
colors:
  restafval: "#6f767d"   # grijs
  papier: "#1e78d6"
```

Wil je maar één container een andere kleur geven, gebruik dan `entities:` met `color:` (zie het
voorbeeld hierboven).

Zie je "Custom element doesn't exist"? Herstart Home Assistant en ververs de pagina hard
(Ctrl/Cmd+Shift+R), of reset de frontend-cache in de app. Gebruik je een YAML-dashboard (`mode: yaml`),
voeg dan zelf deze resource toe:

```yaml
resources:
  - url: /trashapi_static/trash-containers-card.js
    type: module
```

Voorbeeld van een badge met "Over 4 dagen":

```yaml
type: entity
entity: sensor.afvalkalender_postcode_huisnummer_restafval
state_content: days_text
```

## Meldingen en Assist

Kant-en-klare voorbeelden staan in [docs/afval-automatiseringen.md](docs/afval-automatiseringen.md):

- **Pushmelding de avond ervoor** met de knop "Container buiten gezet".
- **Herinneringen** om 21:30 en 06:45, zolang je de container niet als buiten gezet hebt gemarkeerd.
- **Assist**: vraag "welke bak moet er morgen buiten?" of "wanneer wordt restafval opgehaald?".

Het document legt ook uit hoe je ze toevoegt en welke namen (entity-ID's en telefoons) je moet aanpassen.
Andere ideeën: een lamp of display die de avond ervoor een kleur toont, met de sensor "Ophaling morgen"
als trigger, of de ophaaldagen in de gezinsagenda.

## Probleemoplossing

- **Reparatiemeldingen.** Kan de API twee keer achter elkaar niet worden bereikt, dan verschijnt onder
  Instellingen → Systeem → Reparaties "TrashAPI is niet bereikbaar". Geeft de API geen ophaaldata meer
  voor je adres, dan zie je "Geen ophaaldata gevonden" en blijven de laatst bekende gegevens zichtbaar.
  De meldingen verdwijnen vanzelf zodra de API weer werkt.
- **Sensoren zijn "niet beschikbaar".** Kijk onder Instellingen → Systeem → Reparaties en in het
  logboek (zoek op `trashapi`). Open de API in je browser om te zien of hij antwoordt (vervang plaats,
  postcode en huisnummer):
  `https://trashapi.azurewebsites.net/Trash?Location=PLAATS&ZipCode=1234AB&HouseNumber=12&ShowWholeYear=true&GetCleanprofsData=true&IgnoreCache=false`
  Antwoordt de API weer, druk dan op **Nu verversen**; dan hoef je niet op de volgende automatische
  update te wachten.
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
  services → Afvalkalender NL → menu met drie puntjes → **Diagnostische gegevens downloaden**.
  Plaats, postcode en huisnummer worden daarin automatisch weggelaten. Voeg het bestand toe aan je
  [melding op GitHub](https://github.com/TheGinji/ha-afvalkalender-nl/issues).

## Bekende beperkingen

- De integratie is **niet verbonden met een gemeente of afvalinzamelaar** en is afhankelijk van de
  externe TrashAPI. Valt die weg of verandert hij, dan werkt de integratie niet meer. Voor welke
  gemeenten de API gegevens heeft, bepaalt de API.
- Je krijgt alleen wat de API teruggeeft. **Afvalsoorten kunnen verdwijnen of een andere naam krijgen**
  als de bron wordt aangepast. Ophalingen op aanvraag (bijvoorbeeld grofvuil) staan er alleen in als
  de API ze levert.
- Er zijn alleen **datums, geen tijdstippen**. Rond de **jaarwisseling** kan het even duren voordat de
  nieuwe kalender beschikbaar is; de laatst bekende gegevens blijven dan zichtbaar.
- Gegevens worden periodiek opgehaald; er zijn **geen directe updates**. Met de knop **Nu verversen**
  haal je ze op wanneer je wilt.
- De **deksel-kleuren** van de kaart zijn een standaard en kloppen niet voor elke gemeente. Pas ze aan
  (zie "Kleuren van de deksel"). Soorten die de kaart niet kent krijgen een neutrale kleur.
- Afvalsoorten die je op de kaart uitzet (`hide`) blijven als sensor bestaan; alleen de kaart laat ze
  niet zien. Voor de sensoren zelf geldt: verwijder ze onder Entiteiten als je ze niet wilt.
- Vanaf versie 1.5.0 worden de instellingen bij de eerste start automatisch omgezet naar een nieuw
  formaat (adres apart van de API-instellingen). **Terug naar een oudere versie** werkt daarna niet
  meer zonder de integratie opnieuw toe te voegen. Maak een back-up als je dat kunt willen.

## Verwijderen

1. Instellingen → Apparaten & services → **Afvalkalender NL** → menu met drie puntjes naast
   de invoer → **Verwijderen**. De sensoren en de agenda verdwijnen daarmee.
2. Wil je ook de bestanden weghalen? Open HACS → Afvalkalender NL → menu → **Verwijderen** en
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
