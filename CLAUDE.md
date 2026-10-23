# Rising Lion — Canaanite Flavor Pack: Mod Analysis

**Version:** 0.13.1 (0.14.0 in development)  
**Game:** Crusader Kings 3 (supported version 1.20.*)  
**Workshop ID:** 3501948259  
**Tags:** Religion, Culture, Decisions, Flavor

---

## Overview

Rising Lion is a CK3 mod focused on bringing deep historical and cultural flavor to the Levant, Near East, and surrounding regions. It centers on Jewish/Israelite heritage and the ancient civilizations of the area, adding new cultures, faiths, playable dynasties, decisions, buildings, and government types.

---

## Cultures

New or expanded cultures, each with their own heritage, innovations, and traditions:
- Hebrew, Edomite, Canaanite, Phoenician, Radhanite, Bavlim, Aramean, Copt

Players can reform or restore cultures through major decisions.

---

## Religions & Faiths

Judaism is the central religious focus, with two distinct faiths:

- **Rabbinism** — Decentralized, no head of faith. Holy sites: Jerusalem, Safed, Sinai, Alexandria, Babylon. Doctrines: communal identity, legalism, religious legal pronouncements.
- **Karaism** — A rival Jewish faith with its own Exilarchate line.
- **Kohanism** — Introduces the Kohen Gadol (High Priest) title with its own flavorization and council position.

---

## Playable Dynasties & Characters

Historically grounded Jewish dynasties, all playable:
- Davidite, Bostanite, Ananite, Kalonymos, Shealtiel, Benveniste, Makhirite, Maimon, Nathanite

Landless play is supported. Maimonides is playable. The 867 bookmark includes several new starts:
- Radhanite merchant (tribal, Tmutarakan)
- Rabbinic Exilarch Hasdai II (Bostanite dynasty)
- Karaite Exilarch Boaz I (Ananite dynasty)
- Pinchas ben Abdimi (Nathanite dynasty)
- A Khazar ruler
- An Ethiopian character (hard difficulty)

---

## Government Type: Mishpacha (mishpacha_government)

A custom government for landless Jewish families, modeled on the historical Nasi. Key rules:
- Landless playable; families hold a duchy-tier noble family title (`d_jip_*` in `common/landed_titles/jip_landless_titles.txt`) and an estate
- City holdings only; a family that gains land adopts its liege's government (or feudal)
- `mechanic_type = mishpacha`, not administrative: landless heads fail vanilla's `is_landed_or_landless_administrative_or_theocratic`, so most vanilla court positions, events and admin perks are closed to them. Gate Mishpacha content with `government_has_flag = government_is_mishpacha`
- No council and no influence (the influence flag is off); legitimacy and noble families are on
- Reduced levies and MaA, cheaper mercenaries, doubled diplomatic range, +15% income, +10% learning XP
- Primary heritage: Israelite

### Realm and migration
- Families are vassals of the realm their estate lies in, under the "Charter of Privileges" contract (communal taxes, religious rights, Beit Din and trade rights); Muslim lieges may levy jizya
- Moving the estate to another realm switches liege; AI families migrate to more welcoming realms on their own
- A head who leaves Judaism steps down for the nearest Jewish man of the house; Mishpacha Succession covers family titles and Exilarchs

### Titles
- Family heads are **Mar/Geveret** and their spouses Geveret/Mar, whatever the liege (`top_liege = no`, priority 302); estates are "the X Household"
- Family titles use the `duchy_mishpacha` tier name ("Mishpacha"); without it the landless titles log "Failed to find any valid flavorization"
- Exilarch and Kohen Gadol (priority 310) outrank Mar
- Title flavorization `flag` checks did not work for a Davidic "Nasi" variant; it was dropped

### Estate buildings (`common/domiciles/buildings/jip_mishpacha_estate_buildings.txt`)
- New branches with custom icons: **Yeshiva** (library), **Beit Din** (office), **Beit Knesset** (temple; slows migration, discourages expulsion)
- **Counting House** replaces the market line; **Hachnasat Orchim** replaces the Guest Room (piety instead of influence); both keep vanilla names/icons
- Influence-free copies replace vanilla Temple/Crypt/Prison/Trophy Room/Silk/Office lines; the vanilla versions are hidden in `jip_vanilla_estate_overrides.txt`, and existing estates are swapped by `jip_mishpacha_replace_estate_buildings_effect`
- The Villa's influence becomes prestige (`jip_mishpacha_villa_1..5` modifiers)

### Court positions (`common/court_positions/types/jip_jewish_court_positions.txt`, generated)
- Mishpacha heads can appoint all eight: **Rosh Yeshiva, Av Beit Din, Paytan, Chazan, Gabbai Tzedakah, Shaliach, Sofer, Parnas**
- Landed Jewish rulers (duke and above) only get **Av Beit Din** and **Shaliach**, which no vanilla position covers for them; the rest duplicate vanilla positions they already have
- Holders must be adult Jews; the Yeshiva, Beit Din, Beit Knesset and Counting House raise the matching position's aptitude, shown as building parameters
- `minimum_rank` is a hard engine gate: positions above county also check `highest_held_title_tier` in `valid_position`, or appointments silently fail
- Tasks: positions with a vanilla counterpart share its tasks through `common/court_positions/tasks/jip_vanilla_task_overrides.txt` (exact vanilla copies with our positions added to `court_position_types` and the vanilla position's DLC added to `is_shown`; keep in sync with vanilla). New tasks are in `jip_jewish_court_position_tasks.txt`. Both files are generated
- Vanilla tasks that look up their own position by name (Educate Children, Organize Court) can't be shared: they would show but do nothing
- All eight and the Court Financier are full-time jobs (`jip_jewish_court_position_validity_trigger`): one per character, and not alongside a vanilla full-time position. Vanilla positions don't check ours, so a landed ruler's Av Beit Din or Shaliach could still take a vanilla job
- The Sofer combines the Seneschal and Chronicler (stewardship and diplomacy aptitude; the Chronicler's legend tasks plus Keep the Estate's Affairs)

Title flavorizations also include: Emperor, King, Duke (Israelite heritage), Exilarch, Kohen Gadol, Kohen (chaplain position).

---

## Jews in Gentile Realms

- **Expel the Jews / Readmit the Jews** decisions for Christian and Muslim rulers, with AI weighting from traits and tenets; expelled lords may resist in one shared war and become Mishpacha families if they lose
- **Court Financier** court position for non-Jewish dukes and above: domain taxes and Jewish opinion, angers zealots, debt-collection events
---

## The Exilarchate

A central political mechanic of the mod. Two rival figurehead titles:
- **d_exilarchate** — Rabbinic Exilarchate, held by the Davidite/Bostanite/Nathanite lines
- **d_karaite_exilarchate** — Karaite Exilarchate, held by the Ananite line

Both use **Exilarchate Elective** succession: dynasty members and claimants of the same faith vote. Players can use the **Claim Exilarchate** decision to start a scheme, gain a claim, become an elector, and campaign for the title. The Exilarchate has deep history files going back to -596.1.1 (the Babylonian exile).

---

## The Davidic Line Trait

**Type:** Fame trait, inheritable  
**Inheritance:** Male line only, 100% chance, does not inherit from real father (illegitimate children excluded)  
**Shown in ruler designer:** No — bloodline only

### Stat Effects
- +5 zealot opinion
- +10 same-faith opinion
- +0.2 monthly prestige
- Initial legitimacy boost flag

### Interaction with the Exilarchate
In Exilarchate elections, candidates with `davidic_line` receive a bonus to elector votes, scaled by each elector's zeal. Devout electors weight Davidic descent heavily, making the trait a major political asset when campaigning for the Exilarch title.

### Davidic Line Legacy Track
Unlocked when the dynasty dynast carries the `davidic_line` trait (or has already purchased into the track). Five perks, thematically mirroring David's legacy:

| Perk | Name | Effects |
|------|------|---------|
| 1 | Traditional Slingers | Skirmisher MaA: +2 size, +20 damage, +20 pursuit, toughness/screen multipliers |
| 2 | David's Virility | +1 seduction scheme slot, +25% fertility, +5 years of fertility |
| 3 | Shepherd Kings | +2 Diplomacy, +0.5 monthly piety, +10 vassal opinion |
| 4 | Solomon's Wisdom | +3 Learning, +1 language-learning scheme slot |
| 5 | Clever Administrators | +50% development growth, +1 domain limit, +20% tax income |

---

## Major Decisions

### Culture Decisions
- **Form Hebrew Culture** — Requires Israelite heritage, Jewish faith, control of Palestine/Transjordan, Jerusalem of same faith
- **Form Edomite Culture** — Requires Israelite/Phoenician heritage, capital in Edom region
- **Form Canaanite Culture** — Requires Phoenician heritage or Israelite capital in Phoenicia region

### Title Formation Decisions
- Kingdom of Judea, Kingdom of Edom, Kingdoms of Upper/Lower Egypt
- Phoenicia (Tyre, Sidon, Byblos)
- **Empire of Canaan** — De jure empire of the Levant
- **Empire of Kemet** — Egypt, Nubia, Blemmyia
- **Hegemony of the Fertile Crescent** — Large Near Eastern hegemony
- **Beth Nahrain** — Available to Israelites and Canaanites

### Jewish-Specific Decisions
- **Claim Exilarchate** — Start a scheme to gain a claim and become an elector
- **Reestablish Canaanite City** — Create a Phoenician trade republic vassal in a historic city (Tyre, Sidon, Beirut, Tripoli, Famagusta, Nicosia, Latakia)

---

## Unique Buildings

- **Masada** (3 tiers) — Special building at b_zughar, capital of c_negev. Tiers: Ruins of Old Masada (150g, +200 garrison, +1 fort) → Restored Masadan Fortifications (400g, +500 garrison, +2 fort, +5% levy) → Grand Fortifications of Masada (1000g, +1000 garrison, +4 fort, +10% levy, +5 defender bonus)
- **Temple in Jerusalem** — Special building slot on Temple Mount; rebuilding it causes major diplomatic fallout with Muslim rulers (-100 opinion, -15 Islamic fervor)

---

## Compatibility

- Compatible with **Cultures Expanded** mod (v0.10.1+)
- Integrates with the base game's **Persian Struggle** (Rabbinism and Karaism listed as involved faiths)
- Integrates with base game tributary setup system

---

## Changelog Summary

| Version | Key Additions |
|---------|--------------|
| 0.9.0 | Kalonymos, Shealtiel, Benveniste, Makhirite dynasties; Mishpacha government; Exilarchate elective; Maimonides playable |
| 0.10.0 | Kingdom of Edom; Edomite culture; Empire of Canaan rework; Beth Nahrain |
| 0.10.1 | Cultures Expanded compatibility |
| 0.11.0 | Empire of Kemet; Upper/Lower Egypt kingdoms; Copt culture; Aramean/Phoenician tradition changes |
| 0.12.0 | Hegemony of the Fertile Crescent; performance improvements; Kemet region rework |
| 0.13.0 | Masada 3-tier building; Kemet/Crescent nickname grants; Mishpacha desc expansion; Jewish-flavored Exilarchate election tooltips |
| 0.14.0 (in development) | CK3 1.20 update; Mishpacha charter, migration, succession, estate buildings, Mar/Geveret titles and court positions; Expel/Readmit the Jews; Court Financier; Kehunah tenet for Kohenism |