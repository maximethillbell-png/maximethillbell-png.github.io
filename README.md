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
  "wip": false
}
```

La page d'accueil (`index.html`) génère les tuiles, les filtres par catégorie et la recherche automatiquement. Tri par date décroissante.

## Structure

```
index.html            page d'accueil (grille de tuiles)
projects.json         liste des trucs
projects/<slug>/      un dossier par truc
.nojekyll             sert les fichiers tels quels
```
