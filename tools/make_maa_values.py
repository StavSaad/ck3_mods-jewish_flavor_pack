# Refreshes the base cost constants in common/script_values/jip_men_at_arms_values.txt from vanilla's
# common/script_values/00_men_at_arms_values.txt. Men-at-arms costs must be load-time constants (@[ ]), and @ values are
# local to a file, so vanilla's base costs are repeated there; our units' costs are multiples of them, like vanilla's
# cultural units. Rerun after every vanilla update.
import os
import re

VANILLA = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/common/script_values/00_men_at_arms_values.txt'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'script_values', 'jip_men_at_arms_values.txt')

van = dict(re.findall(r'(?m)^(@\w+) = ([^\r\n#]+?)\s*$', open(VANILLA, encoding='utf-8-sig').read()))
raw = open(OUT, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8-sig').replace('\r\n', '\n')
changed = []


def sub(m):
    key, old = m.group(1), m.group(2)
    assert key in van, f'{key} is gone from vanilla: update our costs'
    if van[key] != old:
        changed.append(f'{key}: {old} -> {van[key]}')
    return f'{key} = {van[key]}'


t = re.sub(r'(?m)^(@\w+) = ([^\n#]+?)[ \t]*$', sub, t)
open(OUT, 'wb').write(b'\xef\xbb\xbf' + (t.replace('\n', '\r\n') if crlf else t).encode('utf-8'))
print('\n'.join(changed) or 'unchanged')
