# Le Cabinet 🗄️

Ma bibliothèque personnelle de trucs — jeux, outils, expériences, écrits — accessible partout sur **https://maximethillbell-png.github.io**.

## Ajouter un truc

1. Crée un dossier dans `projects/` avec un `index.html`.
2. Ajoute une entrée dans `projects.json` :

```json
{
  "title": "Nom du truc",
  "emoji": "🎲",
  "description": "Une phrase.",
  "category": "jeu",
  "date": "2026-07-23",
  "url": "projects/mon-truc/index.html",
  "wip": false,
  "icon": "assets/icons/mon-truc.svg",
  "accent": "#7b8cff",
  "tagline": "Une phrase d'accroche pour la vitrine.",
  "features": ["Point fort 1", "Point fort 2"],
  "shot": "assets/shots/mon-truc.jpg",
  "featured": true
}
```

`icon`, `accent`, `tagline`, `features`, `shot` et `featured` sont optionnels : `featured: true` place l'outil dans la section « À la une » (défilement animé), `shot` est la capture affichée (sinon l'icône sert d'affiche).

Les applis qui ont leur propre look ajoutent juste `<script src="../_back.js"></script>` dans leur `<head>` pour avoir le bouton « Le Cabinet » en bas à gauche.

La page d'accueil (`index.html`) génère les tuiles, les filtres par catégorie et la recherche automatiquement. Tri par date décroissante.

## Structure

```
index.html            page d'accueil (vitrine + toutes les apps)
assets/icons/         icônes d'app (SVG)
assets/shots/         captures pour « À la une »
projects/_page.css    style partagé des fiches
projects/_back.js     bouton retour pour les applis
projects.json         liste des trucs
projects/<slug>/      un dossier par truc
.nojekyll             sert les fichiers tels quels
```
