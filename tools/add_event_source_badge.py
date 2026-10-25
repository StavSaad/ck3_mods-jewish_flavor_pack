# Adds the mod's source banner (gui/event_window_widgets/jip_event_source_badge.gui) to every visible event of the mod that
# opens a normal event window. Idempotent. The contract events get it from make_contract_events.py.
import glob
import re

MOD = r'C:/Users/stavs/OneDrive/Documents/Paradox Interactive/Crusader Kings III/mod/jewitup/'
BADGE = ('\twidgets = {\n\t\twidget = {\n\t\t\tgui = "jip_event_source_badge"\n'
         '\t\t\tcontainer = "foreground_shader_vfx_container"\n\t\t}\n\t}\n')
total = 0
for path in glob.glob(MOD + 'events/**/*.txt', recursive=True):
    if path.endswith('jip_mishpacha_contract_events.txt'):
        continue
    raw = open(path, 'rb').read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig')
    crlf = '\r\n' in text
    text = text.replace('\r\n', '\n')
    n = 0

    def add(m):
        global n
        block = m.group(0)
        if ('hidden = yes' in block or 'window = ' in block or 'jip_event_source_badge' in block
                or not re.search(r'^\ttype = \w+_event', block, re.M)):
            return block
        assert '\twidgets = {' not in block and '\twidget = {' not in block, m.group(1)
        anchor = re.search(r'^\ttheme = .*\n', block, re.M) or re.search(r'^\ttype = .*\n', block, re.M)
        n += 1
        return block[:anchor.end()] + BADGE + block[anchor.end():]

    new = re.sub(r'(?ms)^([\w.]+\.\d+) = \{\n.*?^\}', add, text)
    if n:
        if crlf:
            new = new.replace('\n', '\r\n')
        open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + new.encode('utf-8'))
    print(path.split('jewitup/')[1], n)
    total += n
print('total', total)
