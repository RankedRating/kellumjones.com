/* kellumjones.com: small enhancements. The site works without this file. */
(function () {
  'use strict';

  // Menu: open and close without changing the address, trap Escape, restore focus.
  var menu = document.getElementById('menu');
  if (menu) {
    var lastFocus = null;
    var open = function (e) {
      if (e) e.preventDefault();
      lastFocus = document.activeElement;
      menu.classList.add('is-open');
      document.documentElement.style.overflow = 'hidden';
      var close = menu.querySelector('[data-menu-close]');
      if (close) close.focus();
    };
    var shut = function (e) {
      if (e) e.preventDefault();
      menu.classList.remove('is-open');
      document.documentElement.style.overflow = '';
      if (location.hash === '#menu') history.replaceState(null, '', location.pathname + location.search);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    document.querySelectorAll('[data-menu-open]').forEach(function (el) { el.addEventListener('click', open); });
    menu.querySelectorAll('[data-menu-close]').forEach(function (el) { el.addEventListener('click', shut); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && (menu.classList.contains('is-open') || location.hash === '#menu')) shut();
    });
    if (location.hash === '#menu') open();
  }

  // Languages.
  // The visitor's browser languages, most wanted first, lower case: ['ja', 'en-us', ...].
  var wanted = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''])
    .map(function (t) { return String(t).toLowerCase(); }).filter(Boolean);
  var chinese = function (t) { return /hant|-tw|-hk|-mo/.test(t) ? 'zh-hant' : 'zh-hans'; };

  // The list under the language button: open and close in place, close on Escape or a click elsewhere.
  var panel = document.getElementById('lang');
  var langButton = document.querySelector('[data-lang-open]');
  if (panel && langButton) {
    var shown = function () { return panel.classList.contains('is-open') || location.hash === '#lang'; };
    var hidePanel = function (refocus) {
      panel.classList.remove('is-open');
      langButton.setAttribute('aria-expanded', 'false');
      if (location.hash === '#lang') history.replaceState(null, '', location.pathname + location.search);
      if (refocus) langButton.focus();
    };
    var showPanel = function () {
      panel.classList.add('is-open');
      langButton.setAttribute('aria-expanded', 'true');
      var first = panel.querySelector('a[aria-current]') || panel.querySelector('a[data-lang]');
      if (first) first.focus({ preventScroll: true });
    };
    langButton.setAttribute('aria-expanded', String(shown()));
    langButton.addEventListener('click', function (e) { e.preventDefault(); if (shown()) hidePanel(true); else showPanel(); });
    panel.querySelectorAll('[data-lang-close]').forEach(function (el) {
      el.addEventListener('click', function (e) { e.preventDefault(); hidePanel(true); });
    });
    document.addEventListener('click', function (e) {
      var opener = e.target.closest ? e.target.closest('[data-lang-more]') : null;
      if (shown() && !opener && !panel.contains(e.target) && !langButton.contains(e.target)) hidePanel(false);
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && shown()) hidePanel(true); });

    // "Other languages": Google's automatic translation, for languages the site is not written in.
    // The visitor's own language goes first; if it is not in the list, it is added.
    var more = panel.querySelector('details.lang-more');
    if (more) {
      var list = more.querySelector('.lang-more-list');
      var written = {};
      panel.querySelectorAll('a[data-lang]').forEach(function (a) { written[a.getAttribute('data-lang')] = true; });
      var alias = { he: 'iw', nb: 'no', nn: 'no', fil: 'tl' };
      for (var j = 0; j < wanted.length; j++) {
        var base = wanted[j].split('-')[0];
        if (base === 'en' || base === 'zh' || written[base]) continue;
        var google = alias[base] || base;
        var own = list.querySelector('a[data-auto="' + google + '"]');
        if (!own) {
          var label = base;
          try { label = new Intl.DisplayNames([base], { type: 'language' }).of(base) || base; } catch (err) { label = base; }
          own = document.createElement('a');
          own.href = more.getAttribute('data-auto-url').replace('tl=CODE', 'tl=' + encodeURIComponent(google));
          own.lang = base;
          own.rel = 'nofollow noopener';
          own.setAttribute('translate', 'no');
          own.setAttribute('data-auto', google);
          own.textContent = label.charAt(0).toUpperCase() + label.slice(1);
        }
        list.insertBefore(own, list.firstChild);
        more.open = true;
        break;
      }
      document.querySelectorAll('[data-lang-more]').forEach(function (el) {
        el.addEventListener('click', function (e) {
          e.preventDefault();
          more.open = true;
          showPanel();
          panel.scrollIntoView({ block: 'start' });
          more.querySelector('summary').focus({ preventScroll: true });
        });
      });
    }
  }

  // Offer the visitor's own language once. Nothing is redirected: the page stays as it is until they choose.
  // The choice (or the refusal) is remembered in this browser, so the offer does not come back.
  var remember = function (code) { try { localStorage.setItem('kj-lang', code); } catch (err) { /* private window: ask again next time */ } };
  var remembered = null;
  try { remembered = localStorage.getItem('kj-lang'); } catch (err) { remembered = null; }
  document.querySelectorAll('a[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { remember(a.getAttribute('data-lang')); });
  });
  if (panel && !remembered) {
    var here = panel.getAttribute('data-current');
    var have = {};
    panel.querySelectorAll('a[data-lang]').forEach(function (a) { have[a.getAttribute('data-lang')] = a; });
    var best = null;
    for (var i = 0; i < wanted.length && !best; i++) {
      var code = wanted[i].indexOf('zh') === 0 ? chinese(wanted[i]) : wanted[i].split('-')[0];
      if (have[code]) best = code;
    }
    if (best && best !== here) {
      var offer = document.createElement('div');
      offer.className = 'lang-offer';
      var go = document.createElement('a');
      go.href = have[best].getAttribute('href');
      go.lang = have[best].lang;
      go.textContent = have[best].getAttribute('data-offer');
      go.addEventListener('click', function () { remember(best); });
      var no = document.createElement('button');
      no.type = 'button';
      var closeLabel = panel.querySelector('[data-lang-close]');
      no.setAttribute('aria-label', closeLabel ? closeLabel.getAttribute('aria-label') : 'Close');
      no.innerHTML = '<svg aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="2" y1="2" x2="22" y2="22"></line><line x1="22" y1="2" x2="2" y2="22"></line></svg>';
      no.addEventListener('click', function () { remember(here); offer.remove(); });
      offer.appendChild(go);
      offer.appendChild(no);
      document.body.appendChild(offer);
    }
  }

  // Contact form: with no form service set, hand the message to the visitor's mail app.
  var form = document.querySelector('form[data-mailto]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var get = function (name) { var el = form.elements[name]; return el ? el.value.trim() : ''; };
      var subject = get('about') || 'Message from kellumjones.com';
      var body = get('message') + '\n\n' + get('name') + (get('email') ? '\n' + get('email') : '');
      location.href = 'mailto:' + form.getAttribute('data-mailto') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    });
  }
})();
