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
