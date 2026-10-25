# Gives each Jewish (Israelite heritage) culture, and the Nabati, the innovation history of the culture it lived among, by copying that
# culture's vanilla history file (its own file if it has one, else its heritage's) into history/cultures/<jewish>.txt.
# A culture's own file overrides the heritage file (see vanilla history/cultures/_culture.info). Rerun after a vanilla
# update changes the source files.
import os
import re

V = r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game\history\cultures'
os.chdir(r'C:\Users\stavs\OneDrive\Documents\Paradox Interactive\Crusader Kings III\mod\jewitup')

# jewish culture: (neighbour shown in the comment, vanilla source file, extra lines kept before the copy)
MAP = {
    'ashkenazi': ('the Rhineland Germans (central Germanic heritage)', 'heritage_central_germanic.txt', ''),
    'sephardi': ('the Castilians (Iberian heritage)', 'heritage_iberian.txt', ''),
    'bavlim': ('the Mashriqi Arabs of Iraq (levantine)', 'levantine.txt', ''),
    'radhanite': ('the Mashriqi Arabs of Baghdad, home of the Radhanite merchants (levantine)', 'levantine.txt', ''),
    'kochinim': ('the Tamils of Kerala (Dravidian heritage)', 'heritage_dravidian.txt', ''),
    'hebrew': ('the Mashriqi Arabs of the Levant (levantine)', 'levantine.txt', ''),
    'edomite': ('the Bedouin of Edom (Arabic heritage)', 'heritage_arabic.txt',
                '# Desert warfare from antiquity\n1.1.1 = {\n\tdiscover_innovation = innovation_war_camels\n}\n\n'),
    # Not Jewish: the Aramaic peasants of the Sawad (0.15)
    'nabati': ('the Mashriqi Arabs of Iraq (levantine)', 'levantine.txt', ''),
}

for culture, (who, src, extra) in MAP.items():
    body = open(os.path.join(V, src), encoding='utf-8-sig').read().replace('\r\n', '\n')
    # Drop the source's own leading comment lines; ours says where it comes from
    body = re.sub(r'\A(\s*#[^\n]*\n)+', '', body).lstrip('\n')
    # Innovations the extra lines already give can't be discovered again later
    for inno in re.findall(r'discover_innovation = (\w+)', extra):
        body = re.sub(rf'[ \t]*discover_innovation = {inno}[ \t]*\n', '', body)
    text = (f'# {culture.capitalize()} culture: the same innovations as {who} at every start date.\n'
            f'# Copied from vanilla history/cultures/{src} by make_jewish_culture_history.py; rerun it after vanilla updates.\n\n'
            + extra + body.rstrip('\n') + '\n')
    open(f'history/cultures/{culture}.txt', 'wb').write(b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode('utf-8'))
    print(culture, '<-', src, len(re.findall(r'discover_innovation', body)), 'innovations')
