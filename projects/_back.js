// Bandeau « retour au Cabinet » pour les applis qui ont leur propre look.
// Masqué dans les sorties OBS (#out-…) et quand la page est intégrée dans une autre.
(function () {
  if (window.top !== window || /^#out-/.test(location.hash)) return;
  var a = document.createElement('a');
  a.href = new URL('../../index.html', document.currentScript.src).href;
  a.setAttribute('aria-label', 'Retour au Cabinet');
  a.innerHTML = '<img src="' + new URL('../assets/icons/cabinet.svg', document.currentScript.src).href + '" alt="" width="22" height="22"><span>Le Cabinet</span>';
  a.style.cssText = 'position:fixed;left:calc(14px + env(safe-area-inset-left,0px));bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:2147483000;' +
    'display:flex;align-items:center;gap:8px;padding:6px 14px 6px 6px;border-radius:999px;font:600 13px/1 Inter,system-ui,sans-serif;' +
    'color:#eef0fb;text-decoration:none;background:rgba(8,11,22,.72);border:1px solid rgba(255,255,255,.18);' +
    'backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);box-shadow:0 8px 24px rgba(0,0,0,.35);opacity:.85;transition:opacity .15s,transform .15s';
  a.onmouseenter = function () { a.style.opacity = '1'; a.style.transform = 'translateY(-2px)'; };
  a.onmouseleave = function () { a.style.opacity = '.85'; a.style.transform = ''; };
  document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(a); });
})();
