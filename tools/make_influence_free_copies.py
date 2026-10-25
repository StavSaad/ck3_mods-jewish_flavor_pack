# Generates influence-free Mishpacha copies of vanilla estate building lines, the overrides hiding the vanilla
# versions, their localization, and the conversion effect. Run from the mod root.
import re

V = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/common/domiciles/buildings/00_estate_buildings.txt'
v = open(V, encoding='utf-8-sig').read().replace('\r\n', '\n')
ANCHOR = '\tallowed_domicile_types = { estate }\n'
POT = '\n\tcan_construct_potential = {\n\t\tjip_can_build_mishpacha_estate_building_trigger = yes\n\t}\n'
# Influence parameters, and the Office's administrative-governor parameters, which do nothing for Mishpacha families
INFLUENCE_PARAM = re.compile(r'^\t\t(influence_gain_from_hof_support_\d|estate_inherit_influence_\w+|trophy_room_victory_influence|estate_torture_grants_influence|estate_local_theme_cost_reduction|estate_unlock_teach_governor_interaction|estate_governor_\w+) = yes\n', re.M)
INFLUENCE_MOD = re.compile(r'^\t\tdomicile_monthly_influence_(add|mult) = [-\d.]+\n', re.M)

def vb(k):
    return re.search(r'^' + k + r' = \{.*?^\}', v, re.M | re.S).group(0)

def read(p):
    return open(p, encoding='utf-8-sig', newline='').read().replace('\r\n', '\n')

def write(p, t, bom=True):
    open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='').write(t.replace('\n', '\r\n'))

# Copied lines: (vanilla key, previous building of the copy or None)
COPIES = [
    ('temple_small_01', None), ('temple_small_02', 'jip_temple_small_01'), ('temple_small_03', 'jip_temple_small_02'),
    ('temple_crypt_04', 'jip_temple_small_03'), ('temple_crypt_05', 'jip_temple_crypt_04'), ('temple_crypt_06', 'jip_temple_crypt_05'),
    ('prison_02', 'prison_01'), ('prison_03', 'jip_prison_02'), ('prison_04', 'jip_prison_03'),
    ('trophy_room_03', 'trophy_room_02'), ('trophy_room_04', 'jip_trophy_room_03'),
    ('office_01', 'estate_main_01'), ('office_02', 'jip_office_01'), ('office_03', 'jip_office_02'), ('office_04', 'jip_office_03'),
    ('silk_01', None), ('silk_02', 'jip_silk_01'), ('silk_03', 'jip_silk_02'), ('silk_04', 'jip_silk_03'), ('silk_05', 'jip_silk_04'), ('silk_06', 'jip_silk_05'),
]

def copy_block(key, prev):
    b = vb(key)
    assert 'can_construct_potential' not in b, key
    b = b.replace(f'{key} = {{', f'jip_{key} = {{', 1)
    if prev:
        b, n = re.subn(r'\tprevious_building = \w+\n', lambda m: f'\tprevious_building = {prev}\n' + POT, b, count=1)
        assert n == 1, key
    else:
        assert 'previous_building' not in b
        b = b.replace(ANCHOR, ANCHOR + POT, 1)
    b = INFLUENCE_PARAM.sub('', b)
    b = INFLUENCE_MOD.sub('', b)
    b = re.sub(r'\n\tparameters = \{\s*\}\n', '\n', b)  # drop emptied parameter blocks
    b = re.sub(r'\n[ \t]+\n', '\n\n', b)
    b = re.sub(r'\n{3,}', '\n\n', b)
    assert 'influence' not in re.sub(r'\tasset = \{.*', '', b, flags=re.S).replace('raid_insight', ''), key
    return b

# 1) Building copies
p = 'common/domiciles/buildings/jip_mishpacha_estate_buildings.txt'
t = read(p)
if '# Influence-free copies' in t:
    t = t[:t.index('\n# Influence-free copies')].rstrip('\n') + '\n'
for old, new in [('temple_small_03', 'jip_temple_small_03'), ('office_02', 'jip_office_02')]:
    t = t.replace(f'\tprevious_building = {old}\n', f'\tprevious_building = {new}\n')
t = t.replace("# Beit Din sub-branch of the office, beside the Clerk's Office",
              "# Beit Din sub-branch of the Mishpacha office, beside the Clerk's Office")
t = t.replace('# Beit Knesset sub-branch of the temple, beside the Crypt, the Church and the Monastery.',
              '# Beit Knesset sub-branch of the Mishpacha temple, beside the Crypt (the Church and Monastery are not copied).')
t += ('\n# Influence-free copies of vanilla estate lines, for Mishpacha families, who have no influence or governorships.\n'
      '# Identical to vanilla except for the removed influence and governor modifiers and parameters; names and icons are vanilla.\n'
      '# The vanilla versions are hidden from Mishpacha families in jip_vanilla_estate_overrides.txt.\n')
for key, prev in COPIES:
    t += copy_block(key, prev) + '\n'
write(p, t)

# 2) Overrides hiding the vanilla versions
HIDDEN = [
    ('market_01', 'Mishpacha families build the Counting House instead (jip_mishpacha_estate_buildings.txt)'),
    ('guest_room_01', 'Mishpacha families build an influence-free copy instead (jip_hachnasat_orchim_01)'),
    ('wine_cellar_01', 'Its only use is influence at feasts, which Mishpacha families do not have'),
    ('temple_small_01', 'Mishpacha families build an influence-free copy instead (jip_temple_small_01)'),
    ('prison_02', 'Mishpacha families build an influence-free copy instead (jip_prison_02)'),
    ('trophy_room_03', 'Mishpacha families build an influence-free copy instead (jip_trophy_room_03)'),
    ('office_01', 'Mishpacha families build a copy without the governor bonuses instead (jip_office_01)'),
    ('silk_01', 'Mishpacha families build an influence-free copy instead (jip_silk_01)'),
]
out = ('# Overrides of vanilla estate buildings from 00_estate_buildings.txt, unchanged except for can_construct_potential,\n'
       '# which hides them from Mishpacha families. Hiding a line\'s first tier (or the tier where a copy branches off)\n'
       '# hides the rest of it. Keep in sync with vanilla when the game updates.\n')
for key, c in HIDDEN:
    b = vb(key)
    assert b.count(ANCHOR) == 1 and 'can_construct_potential' not in b, key
    b = b.replace(ANCHOR, ANCHOR + f'\n\t# {c}\n\tcan_construct_potential = {{\n\t\tNOT = {{ jip_can_build_mishpacha_estate_building_trigger = yes }}\n\t}}\n')
    out += '\n' + b + '\n'
write('common/domiciles/buildings/jip_vanilla_estate_overrides.txt', out)

# 3) Localization: vanilla names
p = 'localization/english/jip_estate_buildings_l_english.yml'
t = read(p)
if ' # Influence-free copies' in t:
    t = t[:t.index('\n # Influence-free copies')].rstrip('\n') + '\n'
t = t.rstrip('\n') + '\n\n # Influence-free copies of vanilla lines keep the vanilla names\n'
for key, _ in COPIES:
    t += f' jip_{key}_domicile_building: "${key}_domicile_building$"\n'
write(p, t)

# 4) Conversion: vanilla building -> list of buildings to add, in order
REPLACE = {}
for n in range(1, 7):
    REPLACE[f'market_0{n}'] = [f'jip_counting_house_0{i}' for i in range(1, n + 1)]
    REPLACE[f'guest_room_0{n}'] = [f'jip_hachnasat_orchim_0{i}' for i in range(1, n + 1)]
    REPLACE[f'silk_0{n}'] = [f'jip_silk_0{i}' for i in range(1, n + 1)]
for n in range(1, 5):
    REPLACE[f'office_0{n}'] = [f'jip_office_0{i}' for i in range(1, n + 1)]
for n in range(1, 4):
    REPLACE[f'wine_cellar_0{n}'] = []
    REPLACE[f'temple_small_0{n}'] = [f'jip_temple_small_0{i}' for i in range(1, n + 1)]
temple_base = ['jip_temple_small_01', 'jip_temple_small_02', 'jip_temple_small_03']
for n in range(4, 7):
    REPLACE[f'temple_crypt_0{n}'] = temple_base + [f'jip_temple_crypt_0{i}' for i in range(4, n + 1)]
    # The Church and Monastery have no Mishpacha copy; the Beit Knesset takes their place
    REPLACE[f'temple_large_0{n}'] = temple_base + [f'jip_beit_knesset_0{i}' for i in range(4, n + 1)]
    REPLACE[f'temple_monastery_0{n}'] = temple_base + [f'jip_beit_knesset_0{i}' for i in range(4, n + 1)]
for n in range(2, 5):
    REPLACE[f'prison_0{n}'] = ['prison_01'] + [f'jip_prison_0{i}' for i in range(2, n + 1)]
for n in range(3, 5):
    REPLACE[f'trophy_room_0{n}'] = ['trophy_room_01', 'trophy_room_02'] + [f'jip_trophy_room_0{i}' for i in range(3, n + 1)]

eff = ('\n# Swaps the vanilla estate buildings hidden from Mishpacha families (jip_vanilla_estate_overrides.txt) for their\n'
       '# replacements of the same tier: influence-free copies, the Counting House for the market, and the Beit Knesset for\n'
       '# the Church and Monastery. The Wine Cellar, which only gives influence, is removed.\n'
       '# Vanilla seeds estates with some of these at game start. Generated by make_influence_free_copies.py.\n'
       '# root = the family head\n'
       'jip_mishpacha_replace_estate_buildings_effect = {\n\tdomicile ?= {\n')
for old, new in REPLACE.items():
    eff += f'\t\tif = {{\n\t\t\tlimit = {{ has_domicile_building = {old} }}\n\t\t\tremove_domicile_building = {old}\n'
    for nb in new:
        eff += f'\t\t\tadd_domicile_building = {nb}\n'
    eff += '\t\t}\n'
eff += '\t}\n}\n'
p = 'common/scripted_effects/01_jip_utility_effects.txt'
t = read(p)
i = t.index('\n# Swaps the vanilla estate buildings hidden from Mishpacha families')
t = t[:i].rstrip('\n') + '\n' + eff
write(p, t)

# 5) Trigger for the on_action: any vanilla building that needs swapping
trig = ('\n# Domicile scope: has a vanilla estate building that is hidden from Mishpacha families and must be swapped\n'
        '# (see jip_mishpacha_replace_estate_buildings_effect). Generated by make_influence_free_copies.py.\n'
        'jip_domicile_has_vanilla_influence_building_trigger = {\n\tOR = {\n')
for old in REPLACE:
    trig += f'\t\thas_domicile_building = {old}\n'
trig += '\t}\n}\n'
p = 'common/scripted_triggers/jip_mishpacha_triggers.txt'
t = read(p)
if 'jip_domicile_has_vanilla_influence_building_trigger' in t:
    t = t[:t.index('\n# Domicile scope: has a vanilla estate building that is hidden')].rstrip('\n') + '\n'
write(p, t.rstrip('\n') + '\n' + trig)

p = 'common/on_action/jip_mishpacha_on_actions.txt'
t = read(p)
old = '''		domicile ?= {
			OR = {
				has_domicile_building_or_higher = market_01
				has_domicile_building_or_higher = guest_room_01
				has_domicile_building_or_higher = wine_cellar_01
			}
		}
'''
if old in t:
    t = t.replace(old, '\t\tdomicile ?= { jip_domicile_has_vanilla_influence_building_trigger = yes }\n')
write(p, t)
print('copies', len(COPIES), 'hidden', len(HIDDEN), 'conversions', len(REPLACE))
