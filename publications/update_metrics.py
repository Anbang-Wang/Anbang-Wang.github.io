"""
Run this script periodically to refresh journal IF from OpenAlex (free, no API key).
  python publications/update_metrics.py

OpenAlex 2yr_mean_citedness is a close approximation of the 2-year impact factor.
JCR official IF / Q rankings are not publicly available (Clarivate paywall).
"""

import os, re, json, urllib.request, urllib.parse, time

PUB_DIR = os.path.dirname(os.path.abspath(__file__))

# --- OpenAlex source IDs for known journals (faster than search) ---
JOURNAL_IDS = {
    'Expert Systems with Applications':              'S13144211',
    'IEEE Transactions on Biomedical Engineering':   'S5240358',
    'Medical Image Analysis':                        'S116571295',
    'IEEE Transactions on Medical Imaging':          'S58069681',
    'Computers in Biology and Medicine':             'S44278595',
    'Journal of Cardiovascular Computed Tomography': 'S331060',
}

# NOTE: OpenAlex 2yr_mean_citedness uses a different methodology than Clarivate JCR.
# Values are typically lower than official IF (e.g., JCCT: OpenAlex ~0.9 vs JCR ~4.4).
# For accurate JCR IF/Q rankings, manually override the badge field in each .js file.

def fetch_by_id(source_id):
    url = f'https://api.openalex.org/sources/{source_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'update_metrics/1.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def fetch_by_name(journal_name):
    q = urllib.parse.quote(journal_name)
    url = f'https://api.openalex.org/sources?search={q}&per_page=3'
    req = urllib.request.Request(url, headers={'User-Agent': 'update_metrics/1.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    results = data.get('results', [])
    match = next(
        (x for x in results if journal_name.lower() in x['display_name'].lower()),
        results[0] if results else None
    )
    return match

def get_if(journal_name):
    sid = JOURNAL_IDS.get(journal_name)
    try:
        if sid:
            data = fetch_by_id(sid)
            if2yr = (data.get('summary_stats') or {}).get('2yr_mean_citedness')
        else:
            data = fetch_by_name(journal_name)
            if2yr = (data or {}).get('2yr_mean_citedness') or \
                    ((data or {}).get('summary_stats') or {}).get('2yr_mean_citedness')
        return round(if2yr, 1) if if2yr else None
    except Exception as e:
        print(f'  [warn] {journal_name}: {e}')
        return None

def extract_journal(content):
    """Extract journal name from the <em>…</em> in the venue field."""
    m = re.search(r"venue:\s*['\"].*?<em>(.*?)</em>", content)
    return m.group(1) if m else None

def update_badge(content, if2yr):
    """Replace IF number in badge field, or append if not present."""
    # Match:  badge: 'SCI Q1 Top · IF 9.8',   or  badge: 'SCI Q1 Top',
    def replacer(m):
        text = m.group(1)
        if re.search(r'IF\s*[\d.]+', text):
            text = re.sub(r'IF\s*[\d.]+', f'IF {if2yr}', text)
        else:
            text = text.rstrip() + f' · IF {if2yr}'
        return m.group(0).replace(m.group(1), text)

    return re.sub(r"badge:\s*'([^']+)'", replacer, content)

# --- Main ---
files = [f for f in os.listdir(PUB_DIR)
         if f.endswith('.js') and f not in ('index.js', 'metrics.js')]

for fname in sorted(files):
    path = os.path.join(PUB_DIR, fname)
    content = open(path, encoding='utf-8').read()

    journal = extract_journal(content)
    if not journal:
        print(f'{fname}: no venue/journal found, skipping')
        continue

    print(f'{fname}  →  {journal}', end='', flush=True)
    if2yr = get_if(journal)

    if if2yr is None:
        print('  [not found]')
        continue

    new_content = update_badge(content, if2yr)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'  →  IF {if2yr}  [updated]')
    else:
        print(f'  →  IF {if2yr}  [no change]')

    time.sleep(0.3)   # be polite to OpenAlex

print('\nDone. Reload index.html to see updated badges.')
