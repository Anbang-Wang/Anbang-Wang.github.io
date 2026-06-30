// Render publications from window._PUBS (populated by each paper's script tag)

const TAB_META = [
  { key: 'published',  labelEn: 'Published',    labelZh: '已发表' },
  { key: 'review',     labelEn: 'Under Review',  labelZh: '审稿中' },
  { key: 'preprints',  labelEn: 'Preprints',     labelZh: '预印本' },
];

function resolveBadge(pub) {
  const journalMatch = pub.venue.match(/<em>(.*?)<\/em>/);
  const journal = journalMatch ? journalMatch[1] : null;
  const m = journal && (window._JOURNAL_METRICS || {})[journal];
  if (m) {
    const label = `SCI ${m.q}${m.top ? ' Top' : ''} · IF ${m.if}`;
    const cls   = m.top ? 'top' : 'conf';
    return `<span class="venue-badge ${cls}">${label}</span>`;
  }
  return pub.badge
    ? `<span class="venue-badge ${pub.badgeClass || ''}">${pub.badge}</span>`
    : '';
}

function pubThumbFallback(img, bg, color, label) {
  const d = document.createElement('div');
  d.className = 'pub-thumb';
  d.style.background = bg;
  d.style.color = color;
  d.innerHTML = label.replace(/\\n/g, '<br>');
  img.parentNode.replaceChild(d, img);
}

function buildPubRow(pub) {
  const title = pub.title;
  const venue = pub.venue;
  const badge = resolveBadge(pub);

  const imgSrc    = pub.thumb.img || `publications/pics/${pub.cite}.jpg`;
  const bg        = pub.thumb.bg.replace(/'/g, "\\'");
  const color     = pub.thumb.color;
  const label     = pub.thumb.label;
  const thumbHtml = `<img src="${imgSrc}" alt=""
      style="width:100%;height:76px;object-fit:cover;border-radius:10px;"
      onerror="pubThumbFallback(this,'${bg}','${color}','${label}')">`;

  const hasDetail = pub.abstract || pub.doi;
  const links = pub.doi
    ? `<a class="pub-link" href="https://doi.org/${pub.doi}" target="_blank" onclick="event.stopPropagation()">DOI ↗</a>`
    : '';
  const abstract = pub.abstract
    ? `<p class="pub-abstract">${pub.abstract}</p>`
    : '';
  const detailHtml = hasDetail ? `
    <div class="pub-detail">
      <div class="pub-detail-inner">
        ${abstract}
        <div class="pub-links">${links}</div>
      </div>
    </div>` : '';

  const toggle = hasDetail ? `<span class="pub-toggle">▼</span>` : '';

  return `
    <div class="pub-row" ${hasDetail ? 'onclick="this.classList.toggle(\'expanded\')"' : ''}>
      <div class="pub-main">
        <div class="pub-left">${thumbHtml}</div>
        <div class="pub-right">
          <div class="title pub-title">${toggle}${title}</div>
          <div class="meta">${pub.authors} &middot; ${venue} ${badge}</div>
        </div>
      </div>
      ${detailHtml}
    </div>`;
}

function renderPublications(lang) {
  const section = document.getElementById('publications');
  if (!section) return;

  const year = p => parseInt((p.venue.match(/(20\d\d)/) || [])[1] || 0);
  const all = (window._PUBS || []).slice().sort((a, b) => year(b) - year(a));
  const PUBLICATIONS = { published: [], review: [], preprints: [] };
  all.forEach(p => PUBLICATIONS[p.category].push(p));

  const activeTabs = TAB_META.filter(t => PUBLICATIONS[t.key].length > 0);
  if (activeTabs.length === 0) return;

  let tabBarHtml = '<div class="pub-tabs" role="tablist">';
  activeTabs.forEach((t, i) => {
    const active = i === 0 ? 'active' : '';
    tabBarHtml += `
      <button class="pub-tab ${active}"
              onclick="window._switchPubTab('${t.key}', this)"
              role="tab">
        <span class="tab-label" data-en="${t.labelEn}" data-zh="${t.labelZh}">${t.labelEn}</span>
        <span class="count">${PUBLICATIONS[t.key].length}</span>
      </button>`;
  });
  tabBarHtml += '</div>';

  let panelsHtml = '';
  activeTabs.forEach((t, i) => {
    const active = i === 0 ? 'active' : '';
    const rows   = PUBLICATIONS[t.key].map(p => buildPubRow(p)).join('');
    panelsHtml  += `<div class="pub-panel ${active}" id="pub-${t.key}">${rows}</div>`;
  });

  const old = document.getElementById('pub-container');
  if (old) old.remove();

  const container = document.createElement('div');
  container.id = 'pub-container';
  container.innerHTML = tabBarHtml + panelsHtml;
  section.querySelector('h2').after(container);
}

function refreshPubLang(lang) {
  const container = document.getElementById('pub-container');
  if (!container) return;
  container.querySelectorAll('.tab-label[data-en]').forEach(el => {
    el.textContent = lang === 'zh' ? el.dataset.zh : el.dataset.en;
  });
}

function _switchPubTab(key, btn) {
  document.querySelectorAll('.pub-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.pub-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('pub-' + key).classList.add('active');
}

window._switchPubTab  = _switchPubTab;
window.refreshPubLang = refreshPubLang;

document.addEventListener('DOMContentLoaded', () => renderPublications('en'));
