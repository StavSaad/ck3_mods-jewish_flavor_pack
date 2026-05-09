# Rising Lion — Canaanite Flavor Pack: Mod Analysis

**Version:** 0.13.0  
**Game:** Crusader Kings 3 (supported version 1.19.*)  
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

## Government Type: Mishpacha (jewish_admin_family_government)

A custom administrative government type modeled on the historical Nasi. Key rules:
- Landless playable
- Administrative mechanic (city holdings as primary)
- Supports noble families, house aspirations, legitimacy
- Reduced levy/MaA capacity, increased diplomatic range
- Primary heritage: Israelite

Title flavorizations include: Emperor, King, Duke (landless), Exilarch, Kohen Gadol, Kohen (chaplain position).

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
| 0.13.0 | Masada 3-tier building; Kemet/Crescent/Beth Nahrain nickname grants; Mishpacha desc expansion; Jewish-flavored Exilarchate election tooltips |