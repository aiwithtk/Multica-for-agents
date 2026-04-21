---
name: youtube-reader
description: |
  Lecture de données YouTube : récupère les nouveaux commentaires (triés par date), les statistiques vidéo (vues, likes, commentaires), les mentions (@username) et les réponses en attente. Utilise l'API YouTube Data v3 via Composio. Utiliser quand l'utilisateur demande : "récupère les commentaires de cette vidéo", "donne-moi les stats", "listes les mentions", "quels commentaires n'ont pas de réponse ?", "analyse les interactions YouTube". Ce skill est l'entrée du pipeline de traitement des commentaires YouTube.
---

# YouTube Reader Skill

Ce skill permet de lire les données d'une vidéo ou chaîne YouTube via l'API YouTube Data v3 (connectée via Composio).

## Fonctionnalités

1. **Récupérer les commentaires** d'une vidéo, triés du plus récent au plus ancien.
2. **Obtenir les statistiques** d'une vidéo (vues, likes, commentaires, etc.).
3. **Extraire les mentions** (`@username`) des textes de commentaires.
4. **Identifier les réponses en attente** (commentaires sans réponse du propriétaire de la chaîne).

## Outils Composio utilisés

- `YOUTUBE_LIST_COMMENT_THREADS2` – pour les threads de commentaires.
- `YOUTUBE_LIST_COMMENTS` – pour les réponses individuelles.
- `YOUTUBE_GET_VIDEO_DETAILS_BATCH` – pour les statistiques vidéo.
- `YOUTUBE_LIST_CHANNEL_VIDEOS` – pour lister les vidéos d'une chaîne.

## Workflow type

1. **Identifier la vidéo cible** (via `videoId` ou `channelId`).
2. **Récupérer les statistiques** avec `YOUTUBE_GET_VIDEO_DETAILS_BATCH`.
3. **Récupérer les commentaires** avec `YOUTUBE_LIST_COMMENT_THREADS2` (order=`time`).
4. **Extraire les mentions** avec une regex simple `@(\\w+)` sur `textDisplay`.
5. **Détecter les réponses en attente** en vérifiant l'absence de `replies` ou l'auteur des réponses.

## Comment utiliser ce skill

### 1. Identifier la vidéo ou la chaîne
- Si tu as un `videoId` (ex. `dQw4w9WgXcQ`), passe directement à l'étape 2.
- Si tu as un `channelId` (ex. `UC...`) ou un `@handle`, utilise d'abord `YOUTUBE_LIST_CHANNEL_VIDEOS` pour obtenir les vidéos récentes.

### 2. Récupérer les statistiques vidéo
```python
# Avec COMPOSIO_MULTI_EXECUTE_TOOL
tool_slug: YOUTUBE_GET_VIDEO_DETAILS_BATCH
arguments:
  part: "statistics,snippet"
  id: "videoId1,videoId2"
```

### 3. Récupérer les commentaires (tri chronologique)
```python
tool_slug: YOUTUBE_LIST_COMMENT_THREADS2
arguments:
  videoId: "dQw4w9WgXcQ"
  part: "snippet,replies"
  order: "time"
  maxResults: 100          # max par page
  textFormat: "plainText"  # pour éviter le HTML
```

**Pagination** : si la réponse contient `nextPageToken`, rappelle l'outil avec `pageToken` jusqu'à épuisement.

### 4. Extraire les mentions
Les mentions sont les `@username` dans le texte des commentaires. Utilise la regex `@(\\w+)` sur `textDisplay` ou `textOriginal`.

### 5. Identifier les réponses en attente
Un commentaire est « en attente » si :
- `replies` est absent ou `replies.comments` est vide, **ou**
- Aucune réponse n'a été postée par le propriétaire de la chaîne (vérifier `authorDisplayName`).

## Scripts disponibles

Dans `scripts/` se trouvent des fonctions prêtes à être utilisées dans le **sandbox Composio** (via `run_composio_tool`).

- **`fetch_comments.py`** – Récupère les commentaires d'une vidéo, extrait les mentions, détecte les réponses en attente.
- **`fetch_video_stats.py`** – Récupère les statistiques (vues, likes, etc.) pour une liste de vidéos.
- **`list_pending_replies.py`** – Filtre les commentaires sans réponse avec options de seuil et de date.

**Usage dans le workbench :**
```python
from scripts.fetch_comments import fetch_comments
comments = fetch_comments("dQw4w9WgXcQ", max_results=50)
```

## Références

- **`references/api_guide.md`** – Quotas, coûts, endpoints, limites.
- **`references/schema_examples.md`** – Exemples complets de réponses JSON pour comprendre la structure.

Charge ces fichiers **uniquement** quand tu as besoin de détails techniques ; ils ne sont pas nécessaires pour les opérations courantes.

## Pièges connus

- **403 Comments are disabled** : La vidéo a désactivé les commentaires → ignorer et passer à la suivante.
- **Les statistiques sont des chaînes** : Convertir `"123456"` en `int` avant calcul.
- **Quota limité** : Privilégier les lectures (1 unité) aux écritures (50 unités). Éviter `search.list` (100 unités) si possible.
- **Tokens de pagination** : Valides 5 minutes ; ne pas les stocker longtemps.

## Exemple complet (workbench)

Voir `examples/workbench_demo.py` (à créer) pour un scénario d'analyse d'une vidéo.
