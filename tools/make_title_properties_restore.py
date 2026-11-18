# Restores, in common/landed_titles/jip_landed_titles.txt, what our redefinitions of vanilla titles would drop. A title
# defined twice takes all its properties from the last definition, so a duchy we redefine for its Hebrew name loses
# vanilla's market_capital (1.21: a duchy's market sits at that barony, and roads end there) and a title loses every
# vanilla cultural name our cultural_names block doesn't repeat. For each title of ours that vanilla also defines:
# - market_capital: vanilla's is added after our capital line when we have none
# - cultural_names: vanilla's entries for name lists we don't name are added to our block (ours win where both name one)
# Our own names (Hebrew, Aramaic, Canaanite...) are untouched. Idempotent; rerun after every vanilla update and after
# make_aramaic_place_names.py.
import glob
import os
import re

V = r'C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game/common/landed_titles/'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'landed_titles', 'jip_landed_titles.txt')
TITLE = re.compile(r'^[ekdcbh]_[\w-]+$')


def index(lines):
    """title: dict(start, end, indent, cn=(start, end) or None, market=its own market_capital or False, capital=line or None,
    entries={list: name})"""
    stack, out = [], {}
    for i, line in enumerate(lines):
        code = line.split('#')[0]
        for tok in re.finditer(r'([\w-]+) = \{|\{|\}|([\w-]+) = ([\w-]+)', code):
            if tok.group(0) == '}':
                name, start = stack.pop()
                if name in out and out[name]['start'] == start:
                    out[name]['end'] = i
                if name == 'cultural_names':
                    owner = next(t for t, _ in reversed(stack) if t and TITLE.match(t))
                    out[owner]['cn'] = (start, i)
                continue
            if tok.group(2):  # key = value
                owner = next((t for t, _ in reversed(stack) if t and TITLE.match(t)), None)
                in_cn = stack and stack[-1][0] == 'cultural_names'
                if owner and in_cn:
                    out[owner]['entries'][tok.group(2)] = tok.group(3)
                elif owner and stack and stack[-1][0] == owner:
                    if tok.group(2) == 'market_capital':
                        out[owner]['market'] = tok.group(3)
                    if tok.group(2) == 'capital':
                        out[owner]['capital'] = i
                continue
            name = tok.group(1)
            if name and TITLE.match(name):
                out[name] = dict(start=i, end=None, indent=re.match(r'\t*', line).group(0), cn=None, market=False,
                                 capital=None, entries={})
            stack.append((name, i))
    assert not stack
    return out


van = {}
for f in sorted(glob.glob(V + '*.txt')):
    vl = open(f, encoding='utf-8-sig').read().replace('\r\n', '\n').split('\n')
    for t, d in index(vl).items():
        # the title's own market_capital only, never a child's
        van[t] = dict(entries=d['entries'], market=d['market'] or None)

raw = open(OUT, 'rb').read()
crlf = b'\r\n' in raw
lines = raw.decode('utf-8-sig').replace('\r\n', '\n').split('\n')
ours = index(lines)
inserts = []  # (line index to insert before, [lines])
n_market = n_names = 0
for t, d in ours.items():
    if t not in van:
        continue
    ind = d['indent'] + '\t'
    if van[t]['market'] and not d['market']:
        at = (d['capital'] + 1) if d['capital'] is not None else d['start'] + 1
        inserts.append((at, [f'{ind}market_capital = {van[t]["market"]} # vanilla\'s (tools/make_title_properties_restore.py)']))
        n_market += 1
    missing = [(k, v) for k, v in van[t]['entries'].items() if k not in d['entries']]
    if missing:
        n_names += len(missing)
        body = [f'{ind}\t{k} = {v}' for k, v in missing]
        if d['cn']:
            inserts.append((d['cn'][1], body))
        else:
            inserts.append((d['start'] + 1, [f'{ind}cultural_names = {{ # vanilla\'s (tools/make_title_properties_restore.py)'] + body + [f'{ind}}}']))
for at, block in sorted(inserts, key=lambda x: -x[0]):
    lines[at:at] = block
text = '\n'.join(lines)
open(OUT, 'wb').write(b'\xef\xbb\xbf' + (text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))
print(f'market capitals restored: {n_market}; vanilla cultural names restored: {n_names}')
