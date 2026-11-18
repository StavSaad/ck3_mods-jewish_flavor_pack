# Generates common/struggle/struggles/persian_struggle_script.txt: a full copy of vanilla's Persian Struggle (a struggle
# can't be patched by key) with Rising Lion's peoples added as involved cultures and faiths: the Assyrians and the Bavlim
# (the Jews of Babylonia), vanilla's Mandaean culture (which replaced our Nabati in 1.21), Rabbinism and Karaism,
# and the Mandaean faith (Mandaeans and Sabians). Rerun after every vanilla update.
import os

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/common/struggle/struggles/persian_struggle_script.txt'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'common', 'struggle', 'struggles', 'persian_struggle_script.txt')

t = open(VANILLA, encoding='utf-8-sig').read()
PATCHES = [
    ('\t\tkhwarezmian\n',
     '\t\tkhwarezmian\n'
     '\t\t# Rising Lion: the Assyrians, the Jews of Babylonia, and the Mandaeans of the marshes\n'
     '\t\tassyrian\n\t\tbavlim\n\t\tmandaean\n'),
    ('\t\t# Christian\n\t\tnestorian\n',
     '\t\t# Christian\n\t\tnestorian\n\n'
     '\t\t# Rising Lion: Jewish, and the Mandaeans and Sabians\n'
     '\t\trabbinic_faith\n\t\tkaraism\n\t\tmandaean_faith\n'),
]
for old, new in PATCHES:
    assert t.count(old) == 1, 'vanilla changed, update the patch: ' + old[:50]
    t = t.replace(old, new)
open(OUT, 'wb').write(b'\xef\xbb\xbf' + t.encode('utf-8'))
print('ok')
