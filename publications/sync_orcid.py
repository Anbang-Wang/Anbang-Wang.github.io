"""
Sync publications from ORCID + CrossRef.

Usage:
    python publications/sync_orcid.py

What it does:
  1. Fetches your works list from ORCID (public API, no auth needed)
  2. For each work with a DOI, fetches full metadata from CrossRef
  3. For NEW papers  → creates a .js stub (fill in thumb/titleZh/venueZh manually)
  4. For EXISTING papers → updates title, authors, venue, year from CrossRef
                           preserves: cite, thumb, titleZh, venueZh, category

Limitations:
  - Chinese translations (titleZh, venueZh) must be added manually
  - Cover image (thumb.img) must be added manually
  - Papers not yet on ORCID won't appear — go to orcid.org and claim them
"""

import os, re, json, urllib.request, urllib.parse, time

ORCID      = '0009-0005-4685-5690'
PUB_DIR    = os.path.dirname(os.path.abspath(__file__))
MAILTO     = 'w.anbang25@imperial.ac.uk'   # polite header for CrossRef

# ── Helpers ──────────────────────────────────────────────────────────────────

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())

def orcid_works():
    data = get(f'https://pub.orcid.org/v3.0/{ORCID}/works',
               {'Accept': 'application/json'})
    works = []
    for g in data.get('group', []):
        ws  = g.get('work-summary', [{}])[0]
        doi = next((e['external-id-value'] for e in
                    (ws.get('external-ids') or {}).get('external-id', [])
                    if e['external-id-type'] == 'doi'), None)
        if doi:
            works.append(doi.lower())
    return works

def crossref(doi):
    url = f'https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}'
    return get(url)['message']

def semantic_scholar_abstract(doi):
    """Fetch abstract from Semantic Scholar (returns None if unavailable)."""
    try:
        url = f'https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields=abstract'
        data = get(url, {'User-Agent': 'sync_orcid/1.0'})
        return data.get('abstract')
    except Exception:
        return None

def arxiv(doi):
    """Fetch metadata from arXiv API for DOIs like 10.48550/arxiv.XXXX.XXXXX"""
    arxiv_id = doi.split('arxiv.')[-1]
    url = f'https://export.arxiv.org/api/query?id_list={arxiv_id}'
    import xml.etree.ElementTree as ET
    req = urllib.request.Request(url, headers={'User-Agent': 'sync_orcid/1.0'})
    with urllib.request.urlopen(req, timeout=12) as r:
        tree = ET.parse(r)
    ns = {'atom': 'http://www.w3.org/2005/Atom',
          'arxiv': 'http://arxiv.org/schemas/atom'}
    entry = tree.find('.//atom:entry', ns)
    if entry is None:
        return None
    title    = (entry.findtext('atom:title', '', ns) or '').strip().replace('\n', ' ')
    abstract = (entry.findtext('atom:summary', '', ns) or '').strip().replace('\n', ' ')
    year     = (entry.findtext('atom:published', '', ns) or '')[:4]
    authors  = [a.findtext('atom:name', '', ns)
                for a in entry.findall('atom:author', ns)]
    return {'title': title, 'abstract': abstract, 'authors_raw': authors,
            'year': year, 'arxiv_id': arxiv_id, 'doi': doi}

def is_arxiv(doi):
    return '10.48550/arxiv' in doi.lower()

def fmt_authors(msg, highlight='Wang, Anbang'):
    """Format author list; bold the highlighted author."""
    authors = msg.get('author', [])
    parts = []
    for a in authors:
        given  = a.get('given', '')
        family = a.get('family', '')
        name   = f'{family}, {given}'
        initials = '. '.join(w[0] for w in given.split() if w) + '.'
        short    = f'{initials} {family}'
        if highlight.lower() in name.lower():
            parts.append(f'<strong>{short}</strong>')
        else:
            parts.append(short)
    if len(parts) > 4:
        # keep highlight author even if beyond position 3
        highlighted = [p for p in parts if '<strong>' in p]
        if highlighted and highlighted[0] not in parts[:3]:
            parts = parts[:2] + highlighted[:1] + ['et al.']
        else:
            parts = parts[:3] + ['et al.']
    return ', '.join(parts)

def fmt_venue(msg):
    """Build venue string from CrossRef metadata."""
    journal = (msg.get('container-title') or [''])[0]
    volume  = msg.get('volume', '')
    issue   = msg.get('issue', '')
    page    = msg.get('page', '')
    year    = (msg.get('published-print') or msg.get('published') or
               msg.get('published-online') or {})
    year    = ((year.get('date-parts') or [['']])[0][0])

    loc = ''
    if volume:
        loc += f', {volume}'
        if issue: loc += f'({issue})'
    if page:
        loc += f': {page}'
    return f'<em>{journal}</em>{loc}, {year}.'

def doi_to_cite_key(doi, msg):
    """Generate a cite key like wang2025pinn from CrossRef metadata."""
    authors = msg.get('author', [])
    family  = authors[0].get('family', 'unknown').lower() if authors else 'unknown'
    family  = re.sub(r'[^a-z]', '', family)
    year    = (msg.get('published') or msg.get('published-print') or
               msg.get('published-online') or {})
    year    = str((year.get('date-parts') or [['']])[0][0])
    return f'{family}{year}'

def existing_files():
    """Return dict of {doi: filepath} for existing pub JS files."""
    result = {}
    for fname in os.listdir(PUB_DIR):
        if fname in ('index.js', 'journal_metrics.js', 'sync_orcid.py', 'update_metrics.py') \
           or not fname.endswith('.js'):
            continue
        path = os.path.join(PUB_DIR, fname)
        content = open(path, encoding='utf-8').read()
        m = re.search(r"doi['\"]?\s*:\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
        if m:
            result[m.group(1).lower()] = path
    return result

def read_field(content, field):
    """Extract a JS string field value from file content."""
    m = re.search(rf"{field}\s*:\s*'((?:[^'\\]|\\.)*)'", content)
    return m.group(1) if m else None

def update_existing(path, msg):
    """Update title, authors, venue in an existing JS file from CrossRef data."""
    content = open(path, encoding='utf-8').read()

    new_title   = msg.get('title', [''])[0]
    new_authors = fmt_authors(msg)
    new_venue   = fmt_venue(msg)

    def replace_field(c, field, value):
        return re.sub(
            rf"({field}\s*:\s*')((?:[^'\\]|\\.)*)'",
            lambda m: m.group(1) + value.replace("'", "\\'") + "'",
            c, count=1
        )

    content = replace_field(content, 'title',   new_title)
    content = replace_field(content, 'authors', new_authors)
    content = replace_field(content, 'venue',   new_venue)

    # fetch and update abstract if not already present
    if 'abstract:' not in content:
        if is_arxiv(doi):
            abstract = msg.get('abstract') if isinstance(msg, dict) else None
        else:
            abstract = semantic_scholar_abstract(doi)
        if abstract:
            abstract_escaped = abstract.replace("'", "\\'")
            content = content.replace(
                "  venueZh:",
                f"  abstract: '{abstract_escaped}',\n  venueZh:"
            )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_stub(doi, msg, cite_key, category='published'):
    """Write a new JS stub for a paper not yet in the repo."""
    if is_arxiv(doi):
        title   = msg['title']
        authors = fmt_authors_raw(msg['authors_raw'])
        year    = msg['year']
        venue   = f'<em>arXiv</em>:{msg["arxiv_id"]}, {year}.'
        label   = f'arXiv\\n{year}'
        bg      = 'linear-gradient(135deg,#1c1c1c,#b91c1c)'
        color   = '#fca5a5'
    else:
        title   = msg.get('title', [''])[0]
        authors = fmt_authors(msg)
        venue   = fmt_venue(msg)
        journal = (msg.get('container-title') or [''])[0]
        year    = (msg.get('published-print') or msg.get('published') or
                   msg.get('published-online') or {})
        year    = str((year.get('date-parts') or [['']])[0][0])
        label   = f'{journal[:4].upper()}\\n{year}'
        bg      = 'linear-gradient(135deg,#1e3a5f,#1e4d8c)'
        color   = '#93c5fd'

    abstract = semantic_scholar_abstract(doi) if not is_arxiv(doi) else None
    abstract_line = f"  abstract: '{abstract.replace(chr(39), chr(92)+chr(39))}',\n" if abstract else ''

    stub = f"""window._PUBS = window._PUBS || [];
window._PUBS.push({{
  cite: '{cite_key}',
  doi:  '{doi}',
  category: '{category}',
  thumb: {{ label: '{label}', bg: '{bg}', color: '{color}' }},
  title:   '{title.replace(chr(39), chr(92)+chr(39))}',
  titleZh: '/* TODO: 中文标题 */',
  authors: '{authors}',
  venue:   '{venue.replace(chr(39), chr(92)+chr(39))}',
  venueZh: '/* TODO: 中文 venue */',
{abstract_line}}});
"""
    fname = os.path.join(PUB_DIR, f'{cite_key}.js')
    if os.path.exists(fname):
        fname = os.path.join(PUB_DIR, f'{cite_key}_{doi.split("/")[-1][:8]}.js')
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(stub)
    return fname

def fmt_authors_raw(names, highlight='Wang, Anbang'):
    """Format a plain list of 'Given Family' strings."""
    parts = []
    for name in names:
        bits = name.strip().split()
        if not bits:
            continue
        family   = bits[-1]
        given    = ' '.join(bits[:-1])
        initials = '. '.join(w[0] for w in given.split() if w) + '.'
        short    = f'{initials} {family}'
        full     = f'{family}, {given}'
        if highlight.lower() in full.lower():
            parts.append(f'<strong>{short}</strong>')
        else:
            parts.append(short)
    if len(parts) > 4:
        highlighted = [p for p in parts if '<strong>' in p]
        if highlighted and highlighted[0] not in parts[:3]:
            parts = parts[:2] + highlighted[:1] + ['et al.']
        else:
            parts = parts[:3] + ['et al.']
    return ', '.join(parts)

def inject_script_tag(js_filename):
    """Add <script src="publications/X.js"> to index.html if not already present."""
    index_path = os.path.join(os.path.dirname(PUB_DIR), 'index.html')
    if not os.path.exists(index_path):
        return
    content = open(index_path, encoding='utf-8').read()
    tag = f'  <script src="publications/{js_filename}"></script>'
    if tag in content:
        return
    content = content.replace(
        '  <script src="publications/index.js"></script>',
        f'{tag}\n  <script src="publications/index.js"></script>'
    )
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

# ── Main ─────────────────────────────────────────────────────────────────────

print(f'Fetching ORCID works for {ORCID}...')
dois = orcid_works()
print(f'Found {len(dois)} works with DOI\n')

known = existing_files()

for doi in dois:
    print(f'  DOI: {doi}')
    try:
        if is_arxiv(doi):
            msg      = arxiv(doi)
            category = 'preprints'
        else:
            msg      = crossref(doi)
            category = 'published'
    except Exception as e:
        print(f'    [fetch error] {e}')
        continue

    if msg is None:
        print(f'    [no data]')
        continue

    if doi in known:
        if not is_arxiv(doi):
            update_existing(known[doi], msg)
        else:
            # arXiv: only backfill abstract if missing
            path    = known[doi]
            content = open(path, encoding='utf-8').read()
            if 'abstract:' not in content and msg.get('abstract'):
                esc = msg['abstract'].replace("'", "\\'")
                content = content.replace(
                    "  venueZh:",
                    f"  abstract: '{esc}',\n  venueZh:"
                )
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
        print(f'    → updated  {os.path.basename(known[doi])}')
    else:
        cite_key = (f'arxiv{msg["arxiv_id"].replace(".", "_")}'
                    if is_arxiv(doi) else doi_to_cite_key(doi, msg))
        fname    = create_stub(doi, msg, cite_key, category)
        inject_script_tag(os.path.basename(fname))
        print(f'    → created  {os.path.basename(fname)}  ← add thumb/titleZh/venueZh')

    time.sleep(0.3)

print('\nDone.')
