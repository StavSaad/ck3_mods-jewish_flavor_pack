# The Sabian and Mandaean families' court positions: copies of the Jewish ones under their own names, read by
# make_jewish_court_positions.py (the positions) and make_jewish_court_position_tasks.py (their tasks).
# Each flavour maps a Jewish position to its own key (None: no counterpart), and SUBS turns the copied text into theirs:
# their estate branches (make_gnostic_estate_buildings.py), their faith and their triggers.
FLAVOURS = {
    'sabian': dict(
        positions={
            'jip_rosh_yeshiva': 'jip_muallim',
            'jip_av_beit_din': 'jip_rais_al_kahana',
            'jip_paytan': 'jip_shair',
            'jip_chazan': 'jip_kahin',
            'jip_gabbai_tzedakah': 'jip_sabian_almoner',
            'jip_shaliach': 'jip_rasul',
            'jip_sofer': 'jip_katib',
            'jip_parnas': 'jip_sabian_wakil',
        },
        # The library branch is vanilla's Observatory
        subs=[('jip_yeshiva_0', 'library_observatory_0'), ('court_position_jip_yeshiva', 'court_position_jip_observatory'),
              ('jip_beit_din_0', 'jip_diwan_0'), ('court_position_jip_beit_din', 'court_position_jip_diwan'),
              ('jip_beit_knesset_0', 'jip_haykal_0'), ('court_position_jip_beit_knesset', 'court_position_jip_haykal')],
        rite='sabianism'),
    'mandaean': dict(
        positions={
            'jip_rosh_yeshiva': 'jip_ganzibra',
            'jip_av_beit_din': None,
            'jip_paytan': None,
            'jip_chazan': 'jip_tarmida',
            'jip_gabbai_tzedakah': 'jip_shganda',
            'jip_shaliach': 'jip_izgadda',
            'jip_sofer': 'jip_sapra',
            'jip_parnas': 'jip_mandaean_wakil',
        },
        subs=[('jip_yeshiva_0', 'jip_scriptorium_0'), ('court_position_jip_yeshiva', 'court_position_jip_scriptorium'),
              ('jip_beit_knesset_0', 'jip_mandi_0'), ('court_position_jip_beit_knesset', 'court_position_jip_mandi')],
        rite='mandeaism'),
}

COMMENTS = {
    'jip_muallim': "Teacher of the family's school, after Thabit ibn Qurra and his pupils. The Rosh Yeshiva's counterpart; the\n# Observatory raises the aptitude.",
    'jip_rais_al_kahana': "Chief of the priests, who judged the Harranians by their own law. The Av Beit Din's counterpart.",
    'jip_shair': "Poet of the house, as the Sabian secretaries of Baghdad were. The Paytan's counterpart.",
    'jip_kahin': "Priest of the planets who keeps the family's rites. The Chazan's counterpart.",
    'jip_sabian_almoner': "Almoner of the family's alms. The Gabbai Tzedakah's counterpart.",
    'jip_rasul': "Envoy between the Sabians of Harran and of Baghdad. The Shaliach's counterpart.",
    'jip_katib': "Secretary of the family, as the al-Sabi were the caliphs'. The Sofer's counterpart.",
    'jip_sabian_wakil': "Agent who collects the community's dues for the family. The Parnas' counterpart.",
    'jip_ganzibra': "The ganzibra, the senior priest who trains and ordains the priests. The Rosh Yeshiva's counterpart; the\n# Scriptorium raises the aptitude.",
    'jip_tarmida': "The tarmida, the priest who baptises in living water. The Chazan's counterpart.",
    'jip_shganda': "The shganda, the deacon who serves the priests and the poor. The Gabbai Tzedakah's counterpart.",
    'jip_izgadda': "The izgadda, the messenger between the villages of the marshes. The Shaliach's counterpart.",
    'jip_sapra': "The sapra, the scribe who copies the books. The Sofer's counterpart.",
    'jip_mandaean_wakil': "Agent who collects the community's dues for the family. The Parnas' counterpart.",
}


def flavour_subs(f):
    """Text replacements that turn a generated Jewish position or task into flavour f's"""
    d = FLAVOURS[f]
    return d['subs'] + [
        ('jip_ransomable_captive_trigger', f'jip_ransomable_{f}_captive_trigger'),
        ('has_religion = religion:judaism_religion', f"rite = rite:{d['rite']}"),
        ('judaism_religion_opinion', 'dualism_religion_opinion'),
        ('jip_can_have_mishpacha_court_positions_trigger', f'jip_can_have_{f}_court_positions_trigger'),
        ('jip_can_have_jewish_court_positions_trigger', f'jip_can_have_{f}_court_positions_trigger'),
        ('jip_jewish_court_position_validity_trigger', f'jip_{f}_court_position_validity_trigger'),
    ]


def flavoured(text, f, old, new):
    """text with the Jewish position old renamed to new and turned into flavour f's"""
    import re
    text = re.sub(f'\\b{old}(?![a-z0-9])', new, text)
    for a, b in flavour_subs(f):
        text = text.replace(a, b)
    return text


def counterparts(key):
    """The flavour positions of a Jewish position key"""
    return [d['positions'][key] for d in FLAVOURS.values() if d['positions'].get(key)]
