/* BAVARIA — progressive enhancement only. The site works without JavaScript. */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  /* Mobile navigation */
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav__toggle');
  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Κλείσιμο μενού' : 'Άνοιγμα μενού');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { toggle.click(); toggle.focus(); }
    });
  }

  /* Reveal on scroll */
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* Product filters (+ ?cap= preselect) */
  var filterBar = document.querySelector('[data-filters]');
  if (filterBar) {
    var cards = document.querySelectorAll('[data-cap]');
    filterBar.addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      var f = btn.getAttribute('data-filter');
      filterBar.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      var shown = 0;
      cards.forEach(function (c) { var ok = f === 'all' || c.getAttribute('data-cap') === f; c.hidden = !ok; if (ok) shown++; });
      var live = document.getElementById('filter-status');
      if (live) live.textContent = shown + ' μοντέλα';
    });
    var m = /[?&]cap=(\d+)/.exec(location.search);
    if (m) { var pre = filterBar.querySelector('button[data-filter="' + m[1] + '"]'); if (pre) pre.click(); }
  }

  /* Selection guide: recommends an exact model from the product data */
  var guide = document.querySelector('[data-guide]');
  if (guide) {
    var products = JSON.parse(guide.getAttribute('data-products'));
    var $ = function (k) { return guide.querySelector('[data-out="' + k + '"]'); };
    var fmt = function (a) { return String(a).replace('.', ','); };
    var update = function () {
      var people = parseInt((guide.querySelector('input[name="people"]:checked') || {}).value || '3', 10);
      var high = (guide.querySelector('input[name="use"]:checked') || {}).value === 'high';
      var boiler = (guide.querySelector('input[name="boiler"]:checked') || {}).value === 'yes';
      var cap = people <= 2 ? 130 : people <= 4 ? 150 : 220;
      var energy = boiler ? 3 : 2;
      var list = products.filter(function (p) { return p.c === cap && p.e === energy; })
                         .sort(function (a, b) { return a.a - b.a; });
      // higher use: bigger collector, or next capacity when there is only one collector option
      var pick = list[0];
      if (high) {
        if (list.length > 1) pick = list[list.length - 1];
        else if (cap < 220) {
          cap = cap === 130 ? 150 : 220;
          list = products.filter(function (p) { return p.c === cap && p.e === energy; }).sort(function (a, b) { return a.a - b.a; });
          pick = list[0];
        }
      }
      var who = people >= 7 ? '7+ άτομα — για μεγαλύτερες ανάγκες μιλήστε μαζί μας για συνδυασμό συστημάτων' : (people + (people === 1 ? ' άτομο' : ' άτομα'));
      $('cap').firstChild.nodeValue = String(cap);
      $('title').textContent = 'Σας προτείνουμε τον ' + pick.m;
      $('text').textContent = cap + ' λίτρα, ' + (energy === 3 ? 'τριπλής' : 'διπλής') + ' ενέργειας, συλλέκτης ' + fmt(pick.a) + ' m². Για ' + who + '.';
      var box = $('models'); box.textContent = '';
      list.forEach(function (p) { var a = document.createElement('a'); a.href = p.u; a.textContent = p.m + ' · ' + fmt(p.a) + ' m²'; box.appendChild(a); });
      $('link').setAttribute('href', pick.u);
      $('quote').setAttribute('href', '/epikoinonia/?model=' + encodeURIComponent(pick.m) + '#forma');
    };
    guide.addEventListener('change', update);
    update();
  }

  /* Click-to-load Google Maps (nothing loads from Google before the click) */
  document.querySelectorAll('[data-map-src]').forEach(function (box) {
    var btn = box.querySelector('button');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = box.getAttribute('data-map-src');
      f.title = box.getAttribute('data-map-title') || 'Χάρτης';
      f.loading = 'lazy';
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      f.setAttribute('allowfullscreen', '');
      box.textContent = '';
      box.classList.add('is-loaded');
      box.appendChild(f);
    });
  });

  /* Quote form: composes an email in the visitor's own mail app (static hosting, no server) */
  var form = document.querySelector('[data-mailform]');
  if (form) {
    var sel = form.querySelector('#f-model');
    var mm = /[?&]model=([^&#]+)/.exec(location.search);
    if (sel && mm) {
      var want = decodeURIComponent(mm[1].replace(/\+/g, ' '));
      for (var i = 0; i < sel.options.length; i++) { if (sel.options[i].text === want) { sel.selectedIndex = i; break; } }
    }
    form.addEventListener('submit', function (e) {
      if (!form.reportValidity()) return;
      e.preventDefault();
      var v = function (n) { return (form.elements[n] && form.elements[n].value || '').trim(); };
      var subject = 'Αίτημα προσφοράς' + (v('model') ? ' — ' + v('model') : '') + ' — ' + v('name');
      var body = 'Όνομα: ' + v('name') + '\nΤηλέφωνο: ' + v('phone') +
        '\nΕνδιαφέρομαι για: ' + (v('model') || '—') + '\nΠεριοχή: ' + (v('area') || '—') + '\n\n' + v('message') + '\n';
      location.href = 'mailto:' + form.getAttribute('data-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    });
  }
})();
