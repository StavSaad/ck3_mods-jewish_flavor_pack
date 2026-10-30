# Generates common/court_positions/types/jip_jewish_court_positions.txt, and from the same table the Sabian and Mandaean
# families' positions, common/court_positions/types/jip_gnostic_court_positions.txt (jip_court_flavours.py). Run from the
# mod root.
from jip_court_flavours import FLAVOURS, COMMENTS, flavoured
LEVELS = ['terrible', 'poor', 'average', 'good', 'excellent']


def trait(t, v, desc=None):
    return (f'has_trait = {t}', v, desc or f'court_position_{t.replace("lifestyle_", "")}_trait')


def building(levels, desc):
    # levels: [(building, value)], highest first; checked on the employer's estate
    return ('building', levels, desc)


P = [
    dict(key='jip_rosh_yeshiva',
         comment='Head of the family academy, which trains its scholars and judges. Mishpacha families only; landed Jewish\n# rulers have the vanilla Court Tutor and Court Scholar.',
         order=235, rank='county', skill='learning', who='mishpacha', anim='reading', bg='bp2_university_mena', salary='court_tutor',
         opinion='regular', revoke='minor', skill_max=60,
         apt=[trait('lifestyle_scholar', 15), trait('theologian', 15), trait('erudite', 10), trait('diligent', 10), trait('lazy', -10),
              building([('jip_yeshiva_04', 'jip_yeshiva_rosh_yeshiva_aptitude_2_value'), ('jip_yeshiva_03', 'jip_yeshiva_rosh_yeshiva_aptitude_1_value')], 'court_position_jip_yeshiva')],
         scaling=[{'monthly_learning_lifestyle_xp_gain_mult': 0.04},
                  {'monthly_learning_lifestyle_xp_gain_mult': 0.08, 'monthly_piety_gain_mult': 0.02},
                  {'monthly_learning_lifestyle_xp_gain_mult': 0.12, 'monthly_piety_gain_mult': 0.04},
                  {'monthly_learning_lifestyle_xp_gain_mult': 0.16, 'monthly_piety_gain_mult': 0.06},
                  {'monthly_learning_lifestyle_xp_gain_mult': 0.2, 'monthly_piety_gain_mult': 0.08}],
         modifier={'learning': 1, 'monthly_learning_lifestyle_xp_gain_mult': 0.1},
         ai=['# A family with a Yeshiva wants someone to lead it', 'if = {',
             '\tlimit = { domicile ?= { has_domicile_building_or_higher = jip_yeshiva_03 } }', '\tadd = 50', '}']),
    dict(key='jip_av_beit_din',
         comment='Head of the rabbinic court, the Jewish counterpart of the Chief Qadi. Landed Jewish rulers get it too, since the\n# Chief Qadi is Muslim only.',
         order=236, rank='duchy', skill='learning', who='jewish', anim='personality_zealous', bg='councilchamber', salary='chief_qadi',
         opinion='ceremonial', revoke='major', skill_max=50,
         apt=[trait('just', 15), trait('honest', 10), trait('temperate', 10), trait('theologian', 10), trait('arbitrary', -15),
              trait('deceitful', -10),
              building([('jip_beit_din_04', 'jip_beit_din_av_beit_din_aptitude_2_value'), ('jip_beit_din_03', 'jip_beit_din_av_beit_din_aptitude_1_value')], 'court_position_jip_beit_din')],
         scaling=[{'legitimacy_gain_mult': 0.02},
                  {'legitimacy_gain_mult': 0.04},
                  {'legitimacy_gain_mult': 0.06, 'vassal_opinion': 2},
                  {'legitimacy_gain_mult': 0.08, 'vassal_opinion': 3,
                   'enemy_hostile_scheme_phase_duration_add': 'minor_scheme_phase_duration_malus_value'},
                  {'legitimacy_gain_mult': 0.1, 'vassal_opinion': 5,
                   'enemy_hostile_scheme_phase_duration_add': 'medium_scheme_phase_duration_malus_value'}],
         modifier={'learning': 1, 'monthly_piety_gain_mult': 0.1},
         ai=['if = {', '\tlimit = { ai_zeal >= -25 }', '\tadd = 100', '}']),
    dict(key='jip_paytan',
         comment='Liturgical poet, after Yannai and Eleazar Kalir. Mishpacha families only; landed Jewish rulers have the\n# vanilla Court Poet.',
         order=237, rank='county', skill='diplomacy', who='mishpacha', anim='storyteller', bg='bp1_relaxing_room_mena', salary='court_poet',
         opinion='ceremonial', revoke='minor', skill_max=50,
         apt=[trait('lifestyle_poet', 25), trait('theologian', 10), trait('gregarious', 10), trait('shy', -10)],
         scaling=[{'monthly_prestige_gain_mult': 0.02, 'stress_loss_mult': 0.01},
                  {'monthly_prestige_gain_mult': 0.04, 'stress_loss_mult': 0.025},
                  {'monthly_prestige_gain_mult': 0.06, 'stress_loss_mult': 0.05},
                  {'monthly_prestige_gain_mult': 0.08, 'stress_loss_mult': 0.075},
                  {'monthly_prestige_gain_mult': 0.1, 'stress_loss_mult': 0.1}],
         modifier={'diplomacy': 1},
         ai=[]),
    dict(key='jip_chazan',
         comment="Cantor who leads the family's prayers. Mishpacha families only; landed Jewish rulers have the vanilla Court\n# Musician.",
         order=238, rank='county', skill='learning', who='mishpacha', anim='prayer', bg='ep2_holysite_mena', salary='court_musician',
         opinion='regular', revoke='minor', skill_max=50,
         apt=[trait('zealous', 15), trait('calm', 10), trait('gregarious', 5), trait('cynical', -15, 'court_position_jip_cynical_trait'),
              building([('jip_beit_knesset_06', 'jip_beit_knesset_chazan_aptitude_3_value'), ('jip_beit_knesset_05', 'jip_beit_knesset_chazan_aptitude_2_value'), ('jip_beit_knesset_04', 'jip_beit_knesset_chazan_aptitude_1_value')],
                       'court_position_jip_beit_knesset')],
         scaling=[{'stress_loss_mult': 0.02},
                  {'stress_loss_mult': 0.04, 'monthly_piety': 0.1},
                  {'stress_loss_mult': 0.06, 'monthly_piety': 0.2},
                  {'stress_loss_mult': 0.08, 'monthly_piety': 0.3},
                  {'stress_loss_mult': 0.1, 'monthly_piety': 0.5}],
         modifier={'monthly_piety_gain_mult': 0.1},
         ai=['if = {', '\tlimit = { stress_level >= 1 }', '\tadd = 50', '}']),
    dict(key='jip_gabbai_tzedakah',
         comment='Charity warden who collects and hands out the tzedakah. Mishpacha families only: it plays the part of the vanilla\n# High Almoner, so landed Jewish rulers are left to vanilla.',
         order=239, rank='county', skill='stewardship', who='mishpacha', anim='personality_compassionate', bg='bp1_courtyard_mena',
         salary='high_almoner', salary_mult=1.5, opinion='regular', revoke='minor', skill_max=50,
         apt=[trait('generous', 15), trait('compassionate', 10), trait('just', 10), trait('greedy', -15), trait('callous', -10)],
         scaling=[{'monthly_piety_gain_mult': 0.02},
                  {'monthly_piety_gain_mult': 0.05},
                  {'monthly_piety_gain_mult': 0.1, 'judaism_religion_opinion': 3},
                  {'monthly_piety_gain_mult': 0.15, 'judaism_religion_opinion': 5},
                  {'monthly_piety_gain_mult': 0.2, 'judaism_religion_opinion': 10}],
         modifier={'monthly_piety': 0.1, 'monthly_piety_gain_mult': 0.05},
         ai=['if = {', '\tlimit = { ai_zeal >= 0 }', '\tadd = 50', '}']),
    dict(key='jip_shaliach',
         comment='Emissary who carries letters, funds and news between the Jewish communities. Landed Jewish rulers get it too,\n# since no vanilla position does this.',
         order=240, rank='duchy', skill='diplomacy', who='jewish', anim='throne_room_conversation_1', bg='market_east',
         salary='cultural_emissary', opinion='regular', revoke='minor', skill_max=50, languages=True,
         apt=[trait('diplomat', 15), trait('lifestyle_traveler', 10), trait('gregarious', 10), trait('shy', -10)],
         scaling=[{'diplomatic_range_mult': 0.05, 'judaism_religion_opinion': 2},
                  {'diplomatic_range_mult': 0.1, 'judaism_religion_opinion': 4},
                  {'diplomatic_range_mult': 0.15, 'judaism_religion_opinion': 6},
                  {'diplomatic_range_mult': 0.2, 'judaism_religion_opinion': 8},
                  {'diplomatic_range_mult': 0.25, 'judaism_religion_opinion': 10}],
         modifier={'diplomacy': 1, 'monthly_diplomacy_lifestyle_xp_gain_mult': 0.1},
         ai=['# The diaspora network matters most to a family without land', 'if = {',
             '\tlimit = { jip_can_have_mishpacha_court_positions_trigger = yes }', '\tadd = 50', '}']),
    dict(key='jip_sofer',
         comment="Scribe who keeps the family's letters, contracts, accounts and chronicles: a Seneschal and a Chronicler in one,\n# in place of the council Mishpacha families lack. Each side is a little weaker than its vanilla counterpart. Mishpacha\n# families only; landed Jewish rulers have the council, the vanilla Seneschal and the Chronicler.",
         order=241, rank='county', skill='stewardship', who='mishpacha', anim='writing', bg='fp1_steward_study', salary='seneschal',
         opinion='regular', revoke='minor', skill_max=40, skill_mult=1.5, extra_skill=('diplomacy', 1, 25),
         apt=[trait('administrator', 15), trait('diligent', 10), trait('lifestyle_scholar', 10), trait('lazy', -10), trait('arbitrary', -10)],
         scaling=[{'monthly_stewardship_lifestyle_xp_gain_mult': 0.04, 'legitimacy_loss_mult': -0.05},
                  {'monthly_stewardship_lifestyle_xp_gain_mult': 0.08, 'legitimacy_loss_mult': -0.1},
                  {'monthly_stewardship_lifestyle_xp_gain_mult': 0.12, 'stewardship': 1, 'legitimacy_loss_mult': -0.15,
                   'monthly_dynasty_prestige': 0.02},
                  {'monthly_stewardship_lifestyle_xp_gain_mult': 0.16, 'stewardship': 2, 'legitimacy_loss_mult': -0.2,
                   'monthly_dynasty_prestige': 0.04},
                  {'monthly_stewardship_lifestyle_xp_gain_mult': 0.2, 'stewardship': 3, 'legitimacy_loss_mult': -0.25,
                   'monthly_dynasty_prestige': 0.07}],
         modifier={'stewardship': 1, 'monthly_prestige': 0.25},
         ai=[]),
    dict(key='jip_parnas',
         comment="Lay head of the community where the estate lies, who collects its dues for the family. Mishpacha families only;\n# landed Jewish rulers have the vanilla Seneschal. Kept below the Counting House, the family's main income.",
         order=242, rank='county', skill='stewardship', who='mishpacha', anim='holding_staff', bg='ep3_medi_market', salary='seneschal',
         opinion='regular', revoke='minor', skill_max=50,
         apt=[trait('just', 10), trait('honest', 10), trait('greedy', 5),
              building([('jip_counting_house_04', 'jip_counting_house_parnas_aptitude_2_value'), ('jip_counting_house_02', 'jip_counting_house_parnas_aptitude_1_value')], 'court_position_jip_employer_counting_house')],
         scaling=[{'domicile_monthly_gold_add': 0.05},
                  {'domicile_monthly_gold_add': 0.1},
                  {'domicile_monthly_gold_add': 0.15},
                  {'domicile_monthly_gold_add': 0.2},
                  {'domicile_monthly_gold_add': 0.3}],
         modifier={'stewardship': 1},
         ai=['if = {', '\tlimit = { gold < 0 }', '\tadd = 50', '}']),
]


def block(name, d, n):
    t = '\t' * n
    out = f'{t}{name} = {{\n'
    for k, v in d.items():
        out += f'{t}\t{k} = {v}\n'
    return out + f'{t}}}\n'


def ind(lines, n):
    return ''.join('\t' * n + line + '\n' for line in lines)


def salary_amount(p):
    v = f"{p['salary']}_total_salary_value"
    if p.get('salary_mult'):
        return ['add = {', f'\tvalue = {v}', f"\tmultiply = {p['salary_mult']} # Also pays for the alms", '}']
    return [f'add = {v}']


def gen(p):
    k = p['key']
    pos = f'{k}_court_position'
    shown = ('jip_can_have_mishpacha_court_positions_trigger' if p['who'] == 'mishpacha'
             else 'jip_can_have_jewish_court_positions_trigger')
    o = f"# {p['comment']}\n{pos} = {{\n"
    o += f"\tsort_order = {p['order']}\n\tmax_available_positions = 1\n\tminimum_rank = {p['rank']}\n\tskill = {p['skill']}\n\n"
    o += (f"\tcourt_position_asset = {{\n\t\tanimation = {p['anim']}\n"
          f"\t\tbackground = \"gfx/interface/illustrations/event_scenes/{p['bg']}.dds\"\n\t}}\n\n")
    o += f"\topinion = {{\n\t\tvalue = {p['opinion']}_court_position_opinion\n\t}}\n\n"
    o += "\taptitude_level_breakpoints = { 20 40 60 80 }\n\n"
    o += (f"\t# root = the holder\n\taptitude = {{\n\t\tvalue = 1\n\t\tadd = {{\n\t\t\tvalue = {p['skill']}\n"
          f"\t\t\tmultiply = {p.get('skill_mult', 2.5)}\n"
          f"\t\t\tmax = {p['skill_max']}\n\t\t\tdesc = court_position_skill_{p['skill']}\n\t\t}}\n")
    if p.get('extra_skill'):
        s, mult, cap = p['extra_skill']
        o += (f"\t\tadd = {{\n\t\t\tvalue = {s}\n\t\t\tmultiply = {mult}\n\t\t\tmax = {cap}\n"
              f"\t\t\tdesc = court_position_skill_{s}\n\t\t}}\n")
    if p.get('languages'):
        o += ("\t\tadd = {\n\t\t\tvalue = num_of_known_languages\n\t\t\tsubtract = 1\n\t\t\tmultiply = 5\n\t\t\tmax = 25\n"
              "\t\t\tdesc = court_position_languages\n\t\t}\n")
    for a in p['apt']:
        if a[0] == 'building':
            o += "\t\t# The matching building in the employer's estate (jip_mishpacha_estate_buildings.txt)\n"
            for i, (b, v) in enumerate(a[1]):
                o += (f"\t\t{'if' if i == 0 else 'else_if'} = {{\n\t\t\tlimit = {{\n"
                      f"\t\t\t\temployer ?= {{ domicile ?= {{ has_domicile_building_or_higher = {b} }} }}\n\t\t\t}}\n"
                      f"\t\t\tadd = {{\n\t\t\t\tvalue = {v}\n\t\t\t\tdesc = {a[2]}\n\t\t\t}}\n\t\t}}\n")
        else:
            o += f"\t\tif = {{\n\t\t\tlimit = {{ {a[0]} }}\n\t\t\tadd = {{\n\t\t\t\tvalue = {a[1]}\n\t\t\t\tdesc = {a[2]}\n\t\t\t}}\n\t\t}}\n"
    o += "\t\tadd = court_position_aptitude_low_penalty_value\n\t\tadd = general_aptitude_bonus\n\t}\n\n"
    ai_gate = ("\t\ttrigger_if = {\n\t\t\tlimit = {\n\t\t\t\tis_ai = yes\n\t\t\t\thighest_held_title_tier <= tier_county\n"
               "\t\t\t}\n\t\t\talways = no\n\t\t}\n")
    o += f"\t# root = the court owner\n\tis_shown = {{\n\t\t{shown} = yes\n{ai_gate}\t}}\n\n"
    # minimum_rank is a hard engine gate: a lower-ranked ruler who passed valid_position could pick a holder, but the
    # appointment would silently fail. Landless Mishpacha heads always hold a duchy-tier family title.
    rank_check = '' if p['rank'] == 'county' else f"\t\thighest_held_title_tier >= tier_{p['rank']}\n"
    o += f"\tvalid_position = {{\n\t\t{shown} = yes\n{rank_check}\t}}\n\n"
    o += "\tis_shown_character = {\n\t\tscope:employee = {\n\t\t\tcourt_position_employee_shown_trigger = yes\n\t\t}\n\t}\n\n"
    o += ("\tvalid_character = {\n\t\tscope:employee = {\n"
          f"\t\t\tjip_jewish_court_position_validity_trigger = {{ EMPLOYER = scope:liege POS = {pos} }}\n\t\t}}\n\t}}\n\n")
    o += (f"\trevoke_cost = {{ # root is the liege, no other scopes are passed here!\n\t\tprestige = {{\n"
          f"\t\t\tvalue = {p['revoke']}_court_position_prestige_revoke_cost\n\t\t\tif = {{\n"
          f"\t\t\t\tlimit = {{ free_court_position_revoke_trigger = {{ POS = {k} }} }}\n\t\t\t\tmultiply = 0\n\t\t\t}}\n\t\t}}\n\t}}\n\n")
    amt = salary_amount(p)
    pres = ('' if p['salary'] == 'high_almoner'
            else f"\t\tprestige = {{\n\t\t\tvalue = {p['salary']}_prestige_salary_value\n\t\t}}\n")
    o += ("\tsalary = {\n\t\tgold = {\n\t\t\tvalue = 0\n\t\t\tif = {\n\t\t\t\tlimit = {\n\t\t\t\t\tscope:liege = { has_treasury = no }\n"
          "\t\t\t\t}\n" + ind(amt, 4) + "\t\t\t}\n\t\t}\n")
    o += ("\t\ttreasury = {\n\t\t\tvalue = 0\n\t\t\tif = {\n\t\t\t\tlimit = {\n\t\t\t\t\tscope:liege = { has_treasury = yes }\n"
          "\t\t\t\t}\n" + ind(amt, 4) + "\t\t\t}\n\t\t}\n" + pres + "\t\tround = no\n\t}\n\n")
    o += "\treceived_salary = {\n\t\tgold = {\n\t\t\tvalue = 0\n" + ind(amt, 3) + "\t\t}\n" + pres + "\t\tround = no\n\t}\n\n"
    o += "\tscaling_employer_modifiers = {\n" + ''.join(block(lv, s, 2) for lv, s in zip(LEVELS, p['scaling'])) + "\t}\n\n"
    o += block('modifier', p['modifier'], 1) + '\n'
    o += ("\ton_court_position_received = {\n\t\tbasic_gained_court_position_effect = yes\n\t}\n"
          "\ton_court_position_revoked = {\n\t\tbasic_revoked_court_position_effect = yes\n\t}\n"
          "\ton_court_position_invalidated = {\n\t\tbasic_invalidated_court_position_effect = yes\n\t}\n")
    o += f"\ton_court_position_vacated = {{\n\t\tcourt_position_vacated_event_effect = {{\n\t\t\tCOURT_POSITION_TYPE = {pos}\n\t\t}}\n\t}}\n\n"
    o += "\t# Hires over 0, fires under -50\n\tai_position_score = {\n\t\tvalue = 50\n"
    if p['ai']:
        o += "\t\tscope:liege = {\n" + ind(p['ai'], 3) + "\t\t}\n"
    o += "\t\tadd = court_position_debt_considerations_value\n\t}\n"
    o += ("\tai_candidate_score = {\n\t\tvalue = 50\n\t\tadd = scope:base_value\n\t\tadd = court_position_candidate_score_base_value\n"
          "\t\tadd = court_position_candidate_aptitude_value\n\t}\n}\n")
    return o


head = ('# Jewish court positions. Mishpacha family heads get all of them, since they can appoint almost none of the vanilla\n'
        '# positions and have no council. Landed Jewish rulers only get the ones no vanilla position covers for them\n'
        '# (jip_can_have_jewish_court_positions_trigger). Generated by make_jewish_court_positions.py.\n\n')
out = head + '\n'.join(gen(p) for p in P)
open('common/court_positions/types/jip_jewish_court_positions.txt', 'w', encoding='utf-8-sig', newline='').write(out)
print(len(out.splitlines()), 'lines')

# The Sabian and Mandaean families' positions: the same, under their own names, faith and estate branches
flav = []
for f, d in FLAVOURS.items():
    for p in P:
        new = d['positions'].get(p['key'])
        if new:
            q = dict(p, comment=COMMENTS[new], order=p['order'] + (20 if f == 'sabian' else 40))
            flav.append(flavoured(gen(q), f, p['key'], new))
head = ("# The Sabian and Mandaean Familial families' court positions: copies of the Jewish ones (jip_jewish_court_positions.txt)\n"
        '# under their own names, for heads and holders of their rite (tools/jip_court_flavours.py). Generated by\n'
        '# make_jewish_court_positions.py.\n\n')
out = head + '\n'.join(flav)
leftover = [line for line in ''.join(flav).splitlines() if 'judaism' in line or 'jewish' in line]
assert not leftover, leftover
open('common/court_positions/types/jip_gnostic_court_positions.txt', 'w', encoding='utf-8-sig', newline='').write(out)
print(len(flav), 'Sabian and Mandaean positions')
