// YouTube Clean Subscriptions
// Supprime les sections "Pertinentes" et tous les Shorts de la page Abonnements

const SHORTS_SELECTORS = [
  // Shelf entier dédié aux Shorts (ex: "Shorts de tes abonnements")
  'ytd-rich-shelf-renderer[is-shorts]',
  // Chips/filtres Shorts dans la barre de navigation
  'yt-chip-cloud-chip-renderer',
];

const SECTION_TITLE_KEYWORDS = [
  // FR
  'pertinente',
  'recommandé',
  'recommandée',
  // EN (au cas où la langue change)
  'relevant',
  'recommended for you',
  'suggested',
];

function isShortVideo(element) {
  // Un short dans le feed normal a un overlay ou un badge "Shorts"
  const overlayText = element.querySelector('ytd-thumbnail-overlay-time-status-renderer');
  if (overlayText) {
    const style = overlayText.getAttribute('overlay-style');
    if (style === 'SHORTS') return true;
  }
  // Lien vers /shorts/
  const link = element.querySelector('a[href*="/shorts/"]');
  if (link) return true;

  return false;
}

function isSectionRelevante(element) {
  // Cherche le titre de la section shelf
  const titleEl = element.querySelector(
    '#title, #shelf-title, yt-formatted-string, span.title'
  );
  if (!titleEl) return false;
  const text = titleEl.textContent.toLowerCase().trim();
  return SECTION_TITLE_KEYWORDS.some(kw => text.includes(kw));
}

function clean() {
  // 1. Supprimer les shelfs entiers dédiés aux Shorts
  document.querySelectorAll('ytd-rich-shelf-renderer[is-shorts]').forEach(el => {
    el.closest('ytd-rich-section-renderer, ytd-rich-item-renderer, ytd-shelf-renderer') ?
      el.closest('ytd-rich-section-renderer, ytd-rich-item-renderer, ytd-shelf-renderer').remove() :
      el.remove();
  });

  // 2. Supprimer les sections "Pertinentes" / "Recommandées"
  document.querySelectorAll(
    'ytd-rich-shelf-renderer, ytd-shelf-renderer, ytd-rich-section-renderer'
  ).forEach(el => {
    if (isSectionRelevante(el)) {
      const wrapper = el.closest('ytd-rich-section-renderer, ytd-rich-item-renderer') || el;
      wrapper.remove();
    }
  });

  // 3. Supprimer les vidéos Shorts individuels dans le feed
  document.querySelectorAll('ytd-rich-item-renderer').forEach(el => {
    if (isShortVideo(el)) el.remove();
  });
}

// Lancer au chargement
clean();

// Observer les changements du DOM (YouTube est une SPA)
const observer = new MutationObserver(() => {
  clean();
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});
