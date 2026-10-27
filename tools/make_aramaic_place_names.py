# Writes the Aramean, Assyrian and Nabati cultural names (name_list_aramean, name_list_assyrian, name_list_nabati) in
# common/landed_titles/jip_landed_titles.txt from the table below, the one place to change them. Rerunnable: it
# replaces those three lists' entries in every cultural_names block, removes them from titles not in the table,
# and adds a cultural_names block where a title needs one. The other lists (Canaanite, Jewish) are left alone.
#
# Naming rule (0.15 plan, section 1):
# - Aramean: Iron-Age Aramaic where attested, otherwise Classical Syriac
# - Assyrian: Neo-Assyrian (Akkadian) where attested, otherwise Classical Syriac
# - Nabati: the Aramean name, except its own names in the Sawad (NABATI below)
# None leaves the list without a name there (the title's default name shows).
import re

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
PATH = MOD + 'common/landed_titles/jip_landed_titles.txt'

# title: (assyrian, aramean), as cn_ keys without the prefix
NAMES = {
    # Syria
    'k_syria': ('eber_nari', 'aram'),                 # Ebir-nari, "Across the River"; Aram
    'd_aleppo': ('bit_agusi', 'arpad'),               # the Aramean kingdom of Aleppo: Bit Agusi / Arpad (Sefire)
    'c_aleppo': ('halab', 'halab'),
    'b_azaz': ('hazazu', 'hazaz'),
    'b_tall_afrin': ('arpaddu', 'arpad'),             # the city of Arpad, Tell Rifaat
    'b_manbij': ('nappigu', 'mabbug'),
    'c_syrrusafa': ('rasappa', 'resafa'),             # Rasappa / Rezeph, Syriac Rsafa (Sergiopolis)
    'b_ar-rusafa': ('rasappa', 'resafa'),
    'c_qinnasrin': ('qennesrin', 'qennesrin'),
    'b_qinnasrin': ('qennesrin', 'qennesrin'),
    'd_edessa': ('carchemish', 'osroene'),
    'c_edessa': ('adme', 'urhay'),                    # Adma in Assyrian texts; Syriac Urhay
    'b_edessa': ('adme', 'urhay'),
    'b_al-bira': (None, 'birtha'),                    # Birecik, Syriac Birtha
    'c_samosata': ('kummuh', 'shmishat'),             # Kummuh, Commagene
    'b_samosata': ('kummuh', 'shmishat'),
    'c_marash': ('marqasi', None),                    # Marqas(i), capital of Gurgum
    'b_marash': ('marqasi', None),
    'c_aintab': ('carchemish', 'carchemish'),
    'b_jarabulus': ('carchemish', 'carchemish'),       # the site of Carchemish (not Aintab)
    'd_homs': ('subat', 'zobah'),                     # Subat, the Assyrian province of Zobah (location debated)
    'c_homs': ('subat', 'hems'),
    'b_hims': ('subat', 'hems'),
    'c_shayzar': ('sezer', 'sezer'),
    'b_shayzar': ('sezer', 'sezer'),
    'b_masyaf': ('mansuate', 'mansuate'),
    'c_hama': ('hamath', 'hamath'),
    'b_hama': ('hamath', 'hamath'),
    'b_salamiya': ('luhuti', 'luash'),                # Lu'ash of the Zakkur stele, Luhuti to the Assyrians
    'b_kafartab': ('kfartav', 'kfartav'),
    'b_latakia': ('ramitha', 'ramitha'),
    'd_antioch': ('unqi', 'umq'),                     # the kingdom of the Amuq plain (Patina), 'mq on the Zakkur stele
    'b_antartus': ('arwada', 'arwad'),                # Antaradus, facing the island of Arwad
    'd_lebanon': ('labnanu', 'lebnan'),
    'b_saida': ('sidunu', None),                      # Sidon in Sennacherib's annals
    'd_damascus': ('sha_imerishu', None),             # Sha-imerishu, the Assyrian name of the kingdom of Damascus
    'c_damascus': ('dimashqa', 'darmsuq'),
    'b_damascus': ('dimashqa', 'darmsuq'),
    'b_nawa': ('neve', 'neve'),
    'b_zurra': ('geshur', 'geshur'),
    'c_hauran': ('hauranu', None),                    # Mount Hauran of Shalmaneser III
    'b_anjar': ('iturea', 'iturea'),
    'b_sarkhad': ('salcah', 'salcah'),
    'b_as-suwaida-hauran': ('canatha', 'canatha'),
    'd_palmyra': ('tadmar', 'tadmur'),                # Tadmar of Tiglath-pileser I; Palmyrene Tadmor
    'c_palmyra': ('tadmar', 'tadmur'),
    'b_tadmur': ('tadmar', 'tadmur'),
    'c_qaryatan': ('qiryatain', 'qiryatain'),
    'b_al-qaryatan': ('qiryatain', 'qiryatain'),
    # Jazira
    'k_jazira': ('ashur', 'ashur'),                   # Ashur in the Aramaic inscriptions; Aram Naharaim (Hebrew) is the Jewish lists'
    'd_diyarrabia': ('hanigalbat', 'beth_arbaye'),
    'c_mosul': ('athor', 'athor'),                    # the Church of the East's see of Athor
    'b_mosul': ('athor', 'athor'),
    'b_ain_al-qayyara': ('ashur', 'ashur'),           # the city of Ashur, Qal'at Sherqat
    'b_juhaina': ('kalhu', None),                     # Kalhu, Nimrud
    'b_al-hadr': ('hatra', 'hatra'),
    'c_ninive': ('ninua', 'ninwe'),
    'b_ninawa': ('ninua', 'ninwe'),
    'b_bartulla': (None, 'bartelli'),
    'c_sinjar': ('shingar', 'shingar'),
    'b_sinjar': ('shingar', 'shingar'),
    'c_nasibin': ('nasibina', 'nisibin'),
    'b_nasibin': ('nasibina', 'nisibin'),
    'b_gazirat_ibn_umar': ('gazarta', 'gazarta'),
    'c_khabur': ('habor', 'habor'),
    'b_araban': ('shadikanni', None),                 # Tell Ajaja
    'c_upper_khabur': ('bit_bahiani', 'upperhabor'),  # the Aramean kingdom of Guzana
    'b_ras_al-ain': ('guzana', 'gozan'),
    'b_mardin': ('merde', 'merde'),
    'b_kafartutha': ('kfartut', 'kfartut'),
    'b_tall_mauzan': (None, 'tella'),                 # Tella d-Mawzlat, Viransehir
    'd_diyarmudar': ('balihu', 'padanaram'),          # the Balikh towns of Shalmaneser III; Paddan Aram (Peshitta)
    'c_harran': ('harranu', None),
    'b_harran': ('harranu', None),
    'b_saruj': ('sarugi', 'serugh'),
    'c_raqqa': ('tuttul', 'qalliniqos'),              # Raqqa is Tuttul (Tell Bi'a), Callinicum; Mari is downstream
    'b_raqqa': ('tuttul', 'qalliniqos'),
    'c_dausar': ('bit_adini', 'bethadini'),
    'b_tall_ammar': ('kar_shalmaneser', 'til_barsip'),  # Tell Ahmar, capital of Bit Adini
    'd_diyarbakr': ('bit_zamani', 'beth_zamani'),     # the Aramean kingdom of Amida
    'c_amida': ('amedi', 'amid'),
    'b_amid': ('amedi', 'amid'),
    'b_hisn_kaifa': ('hesna_d_kifa', 'hesna_d_kifa'),
    'c_tall_basma': ('kashiyari', 'tur_abdin'),       # the Tur Abdin plateau (Midyat, Hasankeyf)
    'b_baqirda': (None, 'qardu'),                     # Bet Qardu, Gordyene
    'b_saird': (None, 'seert'),
    'c_mayyafariqin': (None, 'maipherqat'),           # Martyropolis
    'b_mayyafariqin': (None, 'maipherqat'),
    'b_arzan': (None, 'arzon'),
    'd_euphrates': ('suhu', None),                    # the land of Suhu on the middle Euphrates
    'c_rahba': ('laqe', None),                        # the Aramean land of Laqe, above Suhu
    'b_ad-daliya': ('mari', 'mari'),                  # Mari, Tell Hariri by Abu Kamal
    'c_hadithat-ana': ('anat', 'anat'),
    'b_hadithat-ana': ('anat', 'anat'),
    'd_kurdistan': ('hadyab', 'hadyab'),              # Adiabene
    'c_irbil': ('arbail', 'arbel'),
    'b_irbil': ('arbail', 'arbel'),
    'b_al-haditha': (None, 'hdatta'),                 # the Church of the East's see of Hdatta
    'b_as-sinn': (None, 'shenna'),                    # Shenna d-Beth Ramman
    'c_shahrazur': ('mazamua', None),                 # the Assyrian province of the Shahrizor plain
    'b_shahrazur': ('mazamua', None),
    # Mesopotamia
    'k_mesopotamia': ('karduniash', 'beth_aramaye'),
    'd_samarra': ('beth_garmai', 'beth_garmai'),
    'c_hulwan': ('khalmanu', None),
    'b_hulwan': ('khalmanu', None),
    'c_kirkuk': ('arrapha', 'karka_d_beth_slokh'),
    'b_kirkuk': ('arrapha', 'karka_d_beth_slokh'),
    'c_takrit': ('takritain', 'tagrit'),
    'b_takrit': ('takritain', 'tagrit'),
    'd_wasit': ('kashkar', 'kashkar'),
    'c_wasit': ('kashkar', 'kashkar'),
    'b_kaskar': ('kashkar', 'kashkar'),
    'd_kufa': ('hirta', 'hirta'),
    'c_kufa': ('hirta', 'hirta'),
    'b_al-hila': ('babili', 'babel'),                 # the ruins of Babylon by Hilla
    'b_niffar': ('nibru', 'nippur'),
    'c_akhadid': ('uruk', None),                      # Uruk and Ur
    'b_al-akhadid': ('uruk', None),
    'd_baghdad': ('akkad', None),
    'c_anbar': ('piroz_shabur', 'piroz_shabur'),      # Pumbedita stays on the Jewish lists
    'b_al-anbar': ('piroz_shabur', 'piroz_shabur'),
    'c_badaraya': ('der', 'bethdaraye'),              # Der (Tell Aqar by Badra); Beth Daraye keeps its name
    'b_badaraya': ('der', 'bethdaraye'),
    'b_hit': ('id', None),                            # Id, the bitumen town
    'd_basra': ('bit_yakin', 'maishan'),              # Bit Yakin of the Sealand; Mesene
    'c_ubulla': ('perat_d_maishan', 'perat_d_maishan'),
    'b_al-ubulla': ('perat_d_maishan', 'perat_d_maishan'),
    # Khuzestan (k_persia, d_khuzestan only)
    'd_khuzestan': ('elam', 'beth_huzaye'),
    'c_ahvaz': ('hormizd_ardashir', 'hormizd_ardashir'),  # the Church of the East's see of Hormizd-Ardashir
    'b_ahvaz': ('hormizd_ardashir', 'hormizd_ardashir'),
    'c_tustar': ('shushtar', 'shushtar'),
    'b_tustar': ('shushtar', 'shushtar'),
    'b_gondishapur': ('beth_lapat', 'beth_lapat'),    # the Church of the East's metropolis of Beth Lapat
    'b_as-sus': ('shushan', 'shush'),                 # Susa
    # Egypt
    'e_kemet': ('musri', 'mesrin'),
}

# Nabati names that differ from the Aramean ones
NABATI = {}

LISTS = ('name_list_assyrian', 'name_list_aramean', 'name_list_nabati')


def wanted(title):
    if title not in NAMES:
        return []
    assyrian, aramean = NAMES[title]
    nabati = NABATI.get(title, aramean)
    return [(l, v) for l, v in zip(LISTS, (assyrian, aramean, nabati)) if v]


raw = open(PATH, encoding='utf-8-sig').read()
crlf = '\r\n' in raw
lines = raw.replace('\r\n', '\n').split('\n')

# Index every title's opening line, its depth, and the line of its own cultural_names block
stack = []          # (title or None, start line)
titles = {}         # title: [start, indent, cultural_names start, cultural_names end, end]
for i, line in enumerate(lines):
    code = line.split('#')[0]
    for tok in re.finditer(r'([ekdcb]_[\w-]+|cultural_names|[\w-]+) = \{|\{|\}', code):
        if tok.group(0) == '}':
            name, start = stack.pop()
            if name in titles and titles[name][0] == start:
                titles[name][4] = i
            if name == 'cultural_names':
                owner = next(t for t, _ in reversed(stack) if t and t != 'cultural_names' and re.match(r'[ekdcb]_', t))
                titles[owner][2:4] = [start, i]
            continue
        name = tok.group(1)
        if name and re.match(r'[ekdcb]_[\w-]+$', name):
            assert name not in titles, f'{name} defined twice'
            titles[name] = [i, re.match(r'\t*', line).group(0), None, None, None]
            stack.append((name, i))
        else:
            stack.append((name, i))
    # One-line blocks such as color = { 1 2 3 } open and close on the same line
assert not stack

missing = [t for t in NAMES if t not in titles]
assert not missing, f'not in the mod file: {missing}'

# Work bottom-up so line numbers above stay valid
edits = []
for title, (start, indent, cn_start, cn_end, end) in titles.items():
    want = wanted(title)
    if cn_start is None:
        if want:
            edits.append((start, 'add', title, indent, end, None, want))
        continue
    body = lines[cn_start + 1:cn_end]
    has = any(re.match(r'\s*(%s) = ' % '|'.join(LISTS), l) for l in body)
    if has or want:
        edits.append((cn_start, 'replace', title, indent, cn_start, cn_end, want))

changed = 0
for pos, kind, title, indent, cn_start, cn_end, want in sorted(edits, key=lambda e: -e[0]):
    inner = indent + '\t\t'
    if kind == 'replace':
        body = [l for l in lines[cn_start + 1:cn_end] if not re.match(r'\s*(%s) = ' % '|'.join(LISTS), l)]
        body += [f'{inner}{l} = cn_{v}' for l, v in want]
        if any(l.strip() for l in body):
            new = [lines[cn_start]] + body + [lines[cn_end]]
            lines[cn_start:cn_end + 1] = new
        else:
            # Nothing left: drop the block and the blank line before it
            drop_from = cn_start - 1 if not lines[cn_start - 1].strip() else cn_start
            del lines[drop_from:cn_end + 1]
    else:
        # After the title's own color line, as the mod's other blocks are, else right after its opening line.
        # pos is the title's opening line and cn_start its end line for additions
        at = next((j for j in range(pos + 1, cn_start) if lines[j].startswith(indent + '\tcolor')), pos)
        block = ['', f'{indent}\tcultural_names = {{'] + [f'{inner}{l} = cn_{v}' for l, v in want] + [f'{indent}\t}}']
        lines[at + 1:at + 1] = block
    changed += 1

out = '\n'.join(lines)
open(PATH, 'w', encoding='utf-8-sig', newline='\r\n' if crlf else '\n').write(out)
keys = sorted({v for t in NAMES for v in NAMES[t] if v} | {v for v in NABATI.values() if v})
print(f'{changed} titles written; {len(keys)} cn_ keys used')
print(' '.join(keys))
