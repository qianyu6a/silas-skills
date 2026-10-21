# -*- coding: utf-8 -*-
"""Five-track candidate cross-batch full verifier (One Lamp pipeline).

Usage: python verify_candidates.py <workspace path>
e.g.:  python verify_candidates.py <workspace>

Does four things:
1. For every entry's "source excerpt" in the five candidate files (framework / principle / case /
   counterexample / glossary term), compare it word for word against its block
   -- normalize both sides the same way (strip page markers + strip all whitespace); normalizing
      only one side errs in both directions
   -- when the strict match fails, give "cross-page excerpts" a second chance: strip OCR page-header
      noise lines line by line (page marker lines, lines that are a bare 1-3 digit page number,
      lines starting with an N.M subsection header) and retry;
      full-width/half-width and glyph differences do not take this path (they are still real
      differences -- fix the excerpt)
2. Three-level fallback extraction of the excerpt: code fence -> > blockquote -> same line
   (stripping the outer quotation marks)
3. "source location" accepts "Block N", "blocks N-M", and the legacy Chinese forms
4. An empty excerpt always fails -- the empty string is a substring of any text, so a missed
   check would make a whole track falsely all-green

Prints the ok/bad count and the failure details for each track; TOTAL BAD: 0 means everything passed.
Directory compatibility: blocks/ or 原文/; cand/ or 候选/.
File names: English (framework.md, ...) or the legacy Chinese names (框架.md, ...). Heading
patterns accept both languages, so this script verifies both editions of the skill.
"""
import io
import os
import re
import sys
import glob

BASE = sys.argv[1] if len(sys.argv) > 1 else '.'
BLOCKS_DIR = next((d for d in (os.path.join(BASE, 'blocks'), os.path.join(BASE, '原文'))
                   if os.path.isdir(d)), os.path.join(BASE, 'blocks'))
CAND_DIR = next((d for d in (os.path.join(BASE, 'cand'), os.path.join(BASE, '候选'))
                 if os.path.isdir(d)), os.path.join(BASE, 'cand'))

# "[page 12]", "[p. 12]" and "[第12页]" are the same marker
PAGE_MARK = re.compile(r'\[\s*(?:p(?:age|\.)?\s*\d+|第\s*\d+\s*页)\s*\]', re.I)
EXCERPT_LABEL = r'- (?:Source excerpt|原文摘录)[^：:\n]*[：:]'


def norm(s):
    return re.sub(r'\s+', '', PAGE_MARK.sub('', s))


def clean_block(t):
    """Strip OCR page-header noise lines line by line (page marker lines, lines that are a bare
    1-3 digit page number, lines starting with an N.M subsection header), for the second-pass match
    of cross-page excerpts -- used only after the strict match fails; full-width/half-width and glyph
    differences do not take this path."""
    out = []
    for ln in t.split('\n'):
        s = ln.strip()
        if PAGE_MARK.fullmatch(s):
            continue
        if re.match(r'^\d{1,3}$', s):
            continue
        if re.match(r'^\d+\.\d+\S', s):
            continue
        out.append(ln)
    return '\n'.join(out)


blocks = {}
for p in sorted(glob.glob(os.path.join(BLOCKS_DIR, 'block*.txt'))):
    m = re.search(r'block(\d+)', os.path.basename(p))
    if m:
        blocks[int(m.group(1))] = io.open(p, encoding='utf-8').read().replace('\r\n', '\n')
print('blocks loaded:', len(blocks))
blocks_clean = {k: clean_block(v) for k, v in blocks.items()}


def extract_excerpt(p):
    """Three-level fallback extraction of the excerpt; returns None or a string (possibly the empty
    string, so the caller must check for emptiness)"""
    m = re.search(EXCERPT_LABEL + r'\s*\n```(?:text)?\n(.*?)\n```', p, re.S)
    if m:
        return m.group(1)
    m = re.search(EXCERPT_LABEL + r'\s*\n\s*((?:[ \t]*>.*\n?)+)', p)
    if m:
        lines = [ln.strip().lstrip('>').strip() for ln in m.group(1).strip().split('\n')]
        return '\n'.join(l for l in lines if l)
    m = re.search(EXCERPT_LABEL + r'(.*)', p)
    if m:
        s = m.group(1).strip()
        if len(s) >= 2 and s[0] in '“"「《' and s[-1] in '”"」》':
            s = s[1:-1]
        return s
    return None


def check(names, title_patterns):
    path = None
    for name in names:
        candidate = os.path.join(CAND_DIR, name + '.md')
        if os.path.exists(candidate):
            path = candidate
            break
    if path is None:
        print('[%s] file not found, skipped' % names[0])
        return 0
    t = io.open(path, encoding='utf-8').read()
    # the per-block receipt tail is not an entry list -- cut it before splitting
    t = re.split(r'(?m)^## .*(?:receipt|回执).*$', t)[0]
    pat = '|'.join('(?:%s)' % tp for tp in title_patterns)
    parts = re.split(r'(?m)^(?=%s)' % pat, t)
    ok = bad = 0
    fails = []
    for p in parts[1:]:
        title = p.split('\n')[0].strip()
        ex = extract_excerpt(p)
        m_loc = re.search(r'- (?:Source location|原文位置)[：:](.+)', p)
        if ex is None or not ex.strip() or not m_loc:
            bad += 1
            fails.append((title[:45], 'excerpt empty/unparsed or location missing'))
            continue
        ex = ex.strip()
        if PAGE_MARK.search(ex):
            bad += 1
            fails.append((title[:45], 'PAGE-MARK: ' + ex[:40]))
            continue
        decl = []
        loc = m_loc.group(1)
        for a, b in re.findall(r'blocks?\s*(\d+)(?:\s*[-–]\s*(\d+))?', loc, re.I):
            decl.append(int(a))
            if b:
                decl.append(int(b))
        for a, b in re.findall(r'第\s*(\d+)(?:[-–](\d+))?\s*块', loc):
            decl.append(int(a))
            if b:
                decl.append(int(b))
        for a in re.findall(r'块\s*(\d+)', loc):
            decl.append(int(a))
        hit = any(
            bn in blocks and (norm(ex) in norm(blocks[bn])
                              or norm(ex) in norm(blocks_clean[bn]))
            for bn in decl)
        if hit:
            ok += 1
        else:
            bad += 1
            fails.append((title[:45], ex[:55]))
    print('[%s] ok=%d bad=%d' % (names[0], ok, bad))
    for t_, e_ in fails[:10]:
        print('   FAIL:', t_, '|', repr(e_))
    return bad


TRACKS = [
    (('framework', '框架'), [r'## \d+\. ', r'## 框架']),
    (('principle', '原则'), [r'## Principle[：:]', r'## 原则[：:]']),
    (('case', '案例'), [r'## Case[：:]', r'## 案例[：:]']),
    (('counterexample', '反例'), [r'## Counterexample\s*\d+[：:]', r'## 反例\s*\d+[：:]']),
    (('glossary', '术语'), [r'## Glossary term[：:]', r'## 术语[：:]']),
]

total = 0
for names, patterns in TRACKS:
    total += check(names, patterns)
print('TOTAL BAD:', total)
sys.exit(1 if total else 0)
