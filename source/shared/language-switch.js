(function () {
  document.querySelectorAll('[data-language-switch]').forEach(function (switcher) {
    var site = switcher.getAttribute('data-site');
    var key = site === 'playfight' ? 'lang_pf' : 'lang_ap';
    switcher.querySelectorAll('a[hreflang]').forEach(function (link) {
      link.addEventListener('click', function () {
        try { localStorage.setItem(key, link.getAttribute('hreflang')); } catch (error) { /* optional preference only */ }
      });
    });
  });
})();
