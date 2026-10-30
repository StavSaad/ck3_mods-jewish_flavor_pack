# Generates gui/shared/coat_of_arms.gui: a full copy of the realm CoA GUI with the Familial government's decoration.
# A Familial head's realm CoA has no tier crown. A Jewish head's (jip_coa_is_jewish) shows a kippah
# (jip_mishpacha_topframe_<size>.dds), or the Keter Shem Tov for an Exilarch
# (jip_exilarch_topframe_<size>.dds, jip_coa_is_exilarch in common/scripted_guis), instead of the tier crown; the tier bar
# stays, as for adventurers (the shield shape itself comes from gfx/interface/icons/realm_frames/familial_government_*,
# picked by the engine from the government's name).
#
# Built on Aligned Realm Banners' copy of the file when that mod is installed (workshop 3823433423), so Rising Lion can load
# after it and keep both: ARB's fix that draws top decorations as an overlay instead of pushing the banner down, and its
# march/palatinate/castellan decorations. The result must also work without ARB, so its references to ARB are guarded: its
# scripted GUIs are swapped for our copies (common/scripted_guis/jip_arb_compat_scripted_guis.txt) shown only when ARB is
# installed (ARB_PRESENT: its localization resolves), and its textures are picked with Select_CString, falling back to a
# vanilla texture, so nothing missing is ever looked up. Without ARB at generation time it is built on vanilla's file.
# Rerun after every vanilla or ARB update.
import os
import re

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/gui/shared/coat_of_arms.gui'
ARB = r'C:/Program Files (x86)/Steam/steamapps/workshop/content/1158310/3823433423/gui/shared/coat_of_arms.gui'
OUT = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/gui/shared/coat_of_arms.gui'
GOV = "'familial_government'"
HIDE_TIER_BAR = False
EXILARCH = "GetScriptedGui('jip_coa_is_exilarch').IsShown( GuiScope.SetRoot( Character.MakeScope ).End )"
JEWISH = "GetScriptedGui('jip_coa_is_jewish').IsShown( GuiScope.SetRoot( Character.MakeScope ).End )"
# Other faiths' families: the Sabians' crescent of Sin and the Mandaeans' klila (jip_<kind>_topframe_<size>.dds, made by
# make_mishpacha_crown.py), each drawn once its textures exist; checked by the jip_coa_is_<kind> scripted GUIs. The save
# game and bookmark have no faith to check, so they keep the kippah.
FAITH_DECOR = [(k, f"GetScriptedGui('jip_coa_is_{k}').IsShown( GuiScope.SetRoot( Character.MakeScope ).End )")
               for k in ['sabian', 'mandaean']
               if os.path.exists(os.path.dirname(OUT) + f'/../../gfx/interface/coat_of_arms/jip_{k}_topframe_28.dds')]
# A bookmark character is no real character, so titles can't be looked up: the bookmark entries of the Exilarchs at their
# start dates (common/bookmarks/bookmarks/jip_bookmarks.txt) are matched by name instead
EXILARCH_BOOKMARKS = ['bookmark_jip_exilarch_chisdai_ii', 'bookmark_jip_exilarch_karaite_boaz']
BOOKMARK_EXILARCH = 'Or( ' + ', '.join(f"EqualTo_string( BookmarkCharacter.GetName, Localize('{k}') )" for k in EXILARCH_BOOKMARKS) + ' )'

ARB_PRESENT = "Not( EqualTo_string( Localize('setting_arb_contract_decor_on'), 'setting_arb_contract_decor_on' ) )"

use_arb = os.path.exists(ARB)
src = open(ARB if use_arb else VANILLA, encoding='utf-8-sig').read()
parts = re.split(r'(?m)^(?=\ttype )', src)
count = {'crown': 0, 'decor': 0, 'topframe': 0}


def hide_topframes(block, gov_expr):
    if not HIDE_TIER_BAR:
        return block
    def sub(m):
        count['topframe'] += 1
        return f'{m.group(1)}{m.group(2)}visible = "[Not({gov_expr}.IsType({GOV}))]"\n{m.group(2)}'
    return re.sub(r'(coa_realm_topframe\s*=\s*\{\n)(\t+)', sub, block)


def decor_icon(indent, visible, size, w, h, kind='mishpacha', position=None):
    t = indent
    count['decor'] += 1
    pos = f'{t}\tposition = {{ {position} }}\n' if position else ''
    return (f'\n{t}icon = {{\n'
            f'{t}\tname = "jip_{kind}_top_decor"\n'
            f'{t}\tvisible = "{visible}"\n'
            f'{t}\tparentanchor = hcenter\n'
            f'{t}\tsize = {{ {w} {h} }}\n'
            f'{pos}'
            f'{t}\ttexture = "gfx/interface/coat_of_arms/jip_{kind}_topframe_{size}.dds"\n'
            f'{t}}}\n')


def add_decor_after_adventurer(p, name):
    """The kippah, or the Exilarch's Keter Shem Tov, after every adventurer helmet: in the layout (vanilla, and ARB's _crown
    variants) or as ARB's overlay above the banner, at the same position as the helmet"""
    out, pos, found = [], 0, 0
    for mm in re.finditer(r'(\t+)icon = \{\n\t+name = "adventurer_top_decor"\n(?:.*\n)*?\1\}\n', p):
        blk = mm.group(0)
        size = re.search(r'landless_adventurer_topframe_(\d+)\.dds', blk).group(1)
        w, h = re.search(r'size = \{ (\d+) (\d+) \}', blk).groups()
        position = re.search(r'position = \{ (-?\d+ -?\d+) \}', blk)
        vis = re.search(r'visible = "\[(.*)\]"', blk).group(1).replace("'landless_adventurer_government'", GOV)
        out.append(p[pos:mm.end()])
        out.append(decor_icon(mm.group(1), f'[And( And( {vis}, {JEWISH} ), Not({EXILARCH}) )]', size, w, h, position=position and position.group(1)))
        out.append(decor_icon(mm.group(1), f'[And( {vis}, {EXILARCH} )]', size, w, h, 'exilarch', position and position.group(1)))
        for kind, shown in FAITH_DECOR:
            out.append(decor_icon(mm.group(1), f'[And( {vis}, {shown} )]', size, w, h, kind, position and position.group(1)))
        pos = mm.end()
        found += 1
    assert found, name
    out.append(p[pos:])
    return ''.join(out)


out = []
for p in parts:
    m = re.match(r'\ttype (\w+)', p)
    name = m.group(1) if m else ''
    if re.fullmatch(r'coa_realm_(tiny|small|medium|big|huge)_crown', name):
        # the tier crown is hidden for Mishpacha heads, as for adventurers and theocracies
        p, n = re.subn(r'(blockoverride "crown"\s*\{\s*)visible = "\[(.*)\]"',
                       lambda mm: f'{mm.group(1)}visible = "[And( {mm.group(2)}, Not(Character.GetGovernment.IsType({GOV})) )]"', p)
        assert n == 1, name
        count['crown'] += 1
        if use_arb:
            p = add_decor_after_adventurer(p, name)
    elif re.fullmatch(r'coa_realm_(tiny|small|medium|big|huge)', name):
        p = add_decor_after_adventurer(p, name)
        p = hide_topframes(p, 'GovernmentType')
    # a save game has no character to look titles or faith up on, so it always shows the kippah
    elif name == 'coa_savegame':
        p, n = re.subn(r'visible = "\[SaveGameItem\.HasCoatOfArms\]"(\n\t+parentanchor = hcenter\n\t+texture = "gfx/interface/coat_of_arms/crown_strip_44\.dds")',
                       lambda mm: f'visible = "[And( SaveGameItem.HasCoatOfArms, Not(SaveGameItem.GetPlayerGovernment.IsType({GOV})) )]"{mm.group(1)}', p)
        assert n == 1, name
        count['crown'] += 1
        mm = re.search(r'(\t+)icon = \{\n\t+name = "crown"\n(?:.*\n)*?\1\}\n', p)
        p = p[:mm.end()] + decor_icon(mm.group(1), f'[And( SaveGameItem.HasCoatOfArms, SaveGameItem.GetPlayerGovernment.IsType({GOV}) )]', 44, 52, 32) + p[mm.end():]
        p = hide_topframes(p, 'SaveGameItem.GetPlayerGovernment')
    elif name == 'coa_realm_bookmark':
        p, n = re.subn(r'(framesize = \{ 64 40 \}\n\t+)visible = "\[Not\(BookmarkCharacter\.GetGovernmentType\.IsType\(\'ecclesiastical_government\'\)\)\]"',
                       lambda mm: f'{mm.group(1)}visible = "[And( Not(BookmarkCharacter.GetGovernmentType.IsType(\'ecclesiastical_government\')), Not(BookmarkCharacter.GetGovernmentType.IsType({GOV})) )]"', p)
        assert n == 1, name
        count['crown'] += 1
        mm = re.search(r'(\t+)icon = \{\n\t+name = "crown"\n(?:.*\n)*?\1\}\n', p)
        bm_gov = f'BookmarkCharacter.GetGovernmentType.IsType({GOV})'
        p = (p[:mm.end()]
             + decor_icon(mm.group(1), f'[And( {bm_gov}, Not({BOOKMARK_EXILARCH}) )]', 62, 64, 40)
             + decor_icon(mm.group(1), f'[And( {bm_gov}, {BOOKMARK_EXILARCH} )]', 62, 64, 40, 'exilarch')
             + p[mm.end():])
        p = hide_topframes(p, 'BookmarkCharacter.GetGovernmentType')
    elif name == 'coa_dynasty_bookmark':
        p = hide_topframes(p, 'BookmarkCharacter.GetGovernmentType')
    out.append(p)

text = ''.join(out)
if use_arb:
    # guard ARB's references so the file also works without ARB
    text, n_gui = re.subn(r"GetScriptedGui\( 'arb_(\w+)' \)\.IsShown\( GuiScope\.SetRoot\( Character\.MakeScope \)\.End \)",
                          lambda mm: f"And( {ARB_PRESENT}, GetScriptedGui( 'jip_arb_{mm.group(1)}' ).IsShown( GuiScope.SetRoot( Character.MakeScope ).End ) )", text)
    text, n_tex = re.subn(r'texture = "gfx/interface/coat_of_arms/arb_(\w+)_topframe_(\d+)\.dds"',
                          lambda mm: f"texture = \"[Select_CString( {ARB_PRESENT}, 'gfx/interface/coat_of_arms/arb_{mm.group(1)}_topframe_{mm.group(2)}.dds', 'gfx/interface/coat_of_arms/landless_adventurer_topframe_{mm.group(2)}.dds' )]\"", text)
    unguarded = [u for u in re.findall(r"GetScriptedGui\( *'arb_|texture *= *\"gfx/interface/coat_of_arms/arb_", text)]
    assert not unguarded, 'unguarded ARB reference'
    print('guarded', n_gui, 'scripted GUI calls and', n_tex, 'textures')
# realm types: a pair per helmet (vanilla: 5 in the flow; ARB: 5 in the _crown flows + 5 overlays); save game 1; bookmark 2
expected_decor = (10 if use_arb else 5) * (2 + len(FAITH_DECOR)) + 1 + 2
assert count == {'crown': 7, 'decor': expected_decor, 'topframe': 9 if HIDE_TIER_BAR else 0}, count
if use_arb:
    base = ("Aligned Realm Banners' copy (workshop 3823433423; its changes are marked \"arb\", and its references are guarded\n"
            "# so the file also works without it)")
    # drop the source's own header comment, which describes that file, not this one
    text = re.sub(r'\A(#[^\n]*\n)+', '', text)
else:
    base = 'vanilla 1.20'
header = (f'# Generated by make_coa_gui_override.py from {base}: a full copy of gui/shared/coat_of_arms.gui with the\n'
          "# Familial government's realm CoA decoration (no tier crown; for Jews a kippah, or the Keter Shem Tov for an Exilarch).\n"
          '# With Aligned Realm Banners, Rising Lion must load after it. Rerun after every vanilla or ARB update.\n')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(b'\xef\xbb\xbf' + (header + text).encode('utf-8'))
print('base:', 'ARB' if use_arb else 'vanilla', count)
