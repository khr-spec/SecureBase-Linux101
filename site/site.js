/* Progressive enhancement: navigation and source links work without JavaScript. */
(() => {
  'use strict';
  const root = document.body.dataset.root || './';
  const menu = document.querySelector('[data-menu]');
  const topnav = document.querySelector('.top-links');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open)); topnav.classList.toggle('open', open);
  });
  const theme = document.querySelector('[data-theme-toggle]');
  try { const saved = localStorage.getItem('securebase-theme'); if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved; } catch (_) {}
  theme?.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('securebase-theme', next); } catch (_) {}
  });
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const code = button.closest('.code-block').querySelector('code');
    try { await navigator.clipboard.writeText(code.textContent); button.textContent = 'Kopieret'; }
    catch (_) { const selection = getSelection(); const range = document.createRange(); range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range); button.textContent = 'Markering klar · Ctrl+C'; }
    setTimeout(() => button.textContent = 'Kopiér', 2500);
  }));
  const lightbox = document.querySelector('#lightbox');
  let current = null;
  const image = lightbox?.querySelector('img');
  const caption = lightbox?.querySelector('.lightbox-caption');
  function visibleImages() { return [...document.querySelectorAll('a[data-zoom]')].filter(a => !a.closest('[hidden]')); }
  function showImage(link) {
    current = link; image.src = link.href; image.alt = link.dataset.caption || link.querySelector('img')?.alt || 'Dokumentationsbillede';
    caption.textContent = image.alt;
    const download = lightbox.querySelector('[data-image-download]'); download.href = link.href;
    download.download = decodeURIComponent(link.href.split('/').pop());
    if (!lightbox.open) lightbox.showModal();
  }
  document.querySelectorAll('a[data-zoom]').forEach(a => a.addEventListener('click', e => { if (!lightbox?.showModal || e.ctrlKey || e.metaKey) return; e.preventDefault(); showImage(a); }));
  function nextImage(offset) { const links = visibleImages(); const index = links.indexOf(current); if (links.length) showImage(links[(index + offset + links.length) % links.length]); }
  lightbox?.querySelector('[data-previous]')?.addEventListener('click', () => nextImage(-1));
  lightbox?.querySelector('[data-next]')?.addEventListener('click', () => nextImage(1));
  lightbox?.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') nextImage(-1); if (e.key === 'ArrowRight') nextImage(1); });
  document.querySelectorAll('dialog').forEach(d => { d.querySelector('[data-close]')?.addEventListener('click', () => d.close()); d.addEventListener('click', e => { if (e.target === d) { const r = d.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) d.close(); } }); });
  document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.filter; let count = 0;
    document.querySelectorAll('.gallery-card').forEach(card => { card.hidden = !(value === 'all' || card.dataset.module === value || (value === 'v12' && card.dataset.series === 'v12')); if (!card.hidden) count++; });
    document.querySelectorAll('[data-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    const counter = document.querySelector('[data-gallery-count]'); if (counter) counter.textContent = count + ' billeder vist';
  }));
  const search = document.querySelector('#search-dialog');
  const input = search?.querySelector('input');
  const results = search?.querySelector('.search-results');
  const status = search?.querySelector('.search-status');
  let index = null;
  async function openSearch() {
    if (!search?.showModal) return; search.showModal(); input.focus();
    if (index === null) {
      status.textContent = 'Indlæser dokumentationsindeks…';
      try { const response = await fetch(root + 'assets/search.json'); if (!response.ok) throw new Error('HTTP'); index = await response.json(); status.textContent = 'Søg i moduler, vejledninger og kildekode.'; renderResults(); }
      catch (_) { status.textContent = 'Søgning kræver HTTP/HTTPS. Åbn websitet, eller brug navigationsmenuen i den lokale forhåndsvisning.'; }
    }
  }
  function renderResults() {
    if (!index) return; const query = input.value.trim().toLocaleLowerCase('da'); results.replaceChildren();
    if (!query) { status.textContent = 'Søg fx efter SSH, sudo, logrotation eller Netplan.'; return; }
    const words = query.split(/\s+/); const matches = index.map(item => ({ item, hay: (item.title + ' ' + item.text).toLocaleLowerCase('da') })).filter(v => words.every(w => v.hay.includes(w))).sort((a,b) => Number(b.item.title.toLocaleLowerCase('da').includes(query)) - Number(a.item.title.toLocaleLowerCase('da').includes(query))).slice(0,12);
    status.textContent = matches.length ? matches.length + ' resultater vist' : 'Ingen resultater. Prøv et andet ord.';
    matches.forEach(({item}) => { const a = document.createElement('a'); a.href = root + item.url; const title = document.createElement('strong'); title.textContent = item.title; const snippet = document.createElement('span'); const lower = item.text.toLocaleLowerCase('da'); const pos = Math.max(0, lower.indexOf(words[0]) - 65); snippet.textContent = (pos ? '…' : '') + item.text.slice(pos, pos + 180) + '…'; a.append(title,snippet); results.append(a); });
  }
  document.querySelectorAll('[data-search]').forEach(b => b.addEventListener('click', openSearch));
  input?.addEventListener('input', renderResults);
  document.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openSearch(); } });
  const progress = document.querySelector('.reading-progress');
  const updateProgress = () => { const available = document.documentElement.scrollHeight - innerHeight; if (progress) progress.style.width = (available > 0 ? Math.min(100, scrollY / available * 100) : 0) + '%'; };
  addEventListener('scroll', updateProgress, {passive:true}); updateProgress();
  const tocLinks = [...document.querySelectorAll('.toc a')];
  if ('IntersectionObserver' in window && tocLinks.length) { const observer = new IntersectionObserver(entries => { entries.forEach(entry => { if (entry.isIntersecting) { tocLinks.forEach(a => a.classList.toggle('active', decodeURIComponent(a.hash.slice(1)) === entry.target.id)); } }); }, {rootMargin:'-100px 0px -65% 0px'}); document.querySelectorAll('.prose h2,.prose h3').forEach(h => observer.observe(h)); }
})();
