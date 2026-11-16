"""A small reader and writer for Paradox script (CK3), enough for the generators that merge game files.

parse(text) -> list of items. An item is (key, op, value) for `key = value`, or (None, None, value) for a bare
value in a list block. A value is a string token (quotes kept) or a Block. A `key = hsv { ... }` form is kept as
(key, op, Tagged('hsv', Block)). Comments are dropped.
"""
import re

TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}]|[<>!?]=|==|[=<>]|[^\s{}=<>!?#"]+|[!?]', re.S)
OPS = {'=', '<', '>', '<=', '>=', '!=', '?=', '=='}


class Block(list):
    pass


class Tagged:
    def __init__(self, tag, block):
        self.tag, self.block = tag, block


def strip_comments(text):
    out = []
    for line in text.splitlines():
        res, q = [], False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == '#' and not q:
                break
            res.append(ch)
        out.append(''.join(res))
    return '\n'.join(out)


def tokenize(text):
    return TOKEN.findall(strip_comments(text.lstrip('﻿')))


def parse(text):
    toks = tokenize(text)
    pos = 0

    def block():
        nonlocal pos
        items = Block()
        while pos < len(toks):
            t = toks[pos]
            if t == '}':
                pos += 1
                return items
            if t == '{':
                pos += 1
                items.append((None, None, block()))
                continue
            if pos + 1 < len(toks) and toks[pos + 1] in OPS:
                key, op = t, toks[pos + 1]
                pos += 2
                items.append((key, op, value()))
            else:
                pos += 1
                items.append((None, None, t))
        return items

    def value():
        nonlocal pos
        t = toks[pos]
        if t == '{':
            pos += 1
            return block()
        pos += 1
        # `hsv { ... }`, `rgb { ... }`, `hsv360 { ... }`
        if pos < len(toks) and toks[pos] == '{' and re.fullmatch(r'[a-z0-9_]+', t) and t in ('hsv', 'rgb', 'hsv360'):
            pos += 1
            return Tagged(t, block())
        return t

    return block()


def fmt_value(v, ind):
    if isinstance(v, Tagged):
        return v.tag + ' ' + fmt_value(v.block, ind)
    if isinstance(v, Block):
        if all(k is None and not isinstance(x, (Block, Tagged)) for k, _, x in v):
            return '{ ' + ' '.join(x for _, _, x in v) + ' }' if v else '{ }'
        return '{\n' + write(v, ind + 1) + '\t' * ind + '}'
    return v


def write(items, ind=0):
    out = []
    for k, op, v in items:
        if k is None:
            out.append('\t' * ind + fmt_value(v, ind) + '\n')
        else:
            out.append('\t' * ind + '%s %s %s\n' % (k, op, fmt_value(v, ind)))
    return ''.join(out)


def same(a, b):
    """Structural equality of two values."""
    if isinstance(a, Tagged) or isinstance(b, Tagged):
        return isinstance(a, Tagged) and isinstance(b, Tagged) and a.tag == b.tag and same(a.block, b.block)
    if isinstance(a, Block) or isinstance(b, Block):
        if not (isinstance(a, Block) and isinstance(b, Block)) or len(a) != len(b):
            return False
        return all(x[0] == y[0] and x[1] == y[1] and same(x[2], y[2]) for x, y in zip(a, b))
    return a == b
