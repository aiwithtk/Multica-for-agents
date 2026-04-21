---
name: youtube-writer
description: Interaction avec YouTube : poster des réponses, liker des vidéos, modérer les commentaires (approuver, rejeter, bannir), supprimer des commentaires et signaler des abus. Utilise l'API YouTube Data v3 via Composio. Utiliser quand l'utilisateur demande : "réponds à ce commentaire", "like cette vidéo", "vire ce troll", "approuve les messages", "supprime mon commentaire", "signale cette vidéo". Ce skill gère les actions d'écriture et de modération.
---

# YouTube Writer Skill

Ce skill permet d'effectuer des actions d'écriture et de modération sur YouTube via l'API YouTube Data v3 (connectée via Composio).

## Fonctionnalités

1. **Répondre à un commentaire** (thread).
2. **Liker une vidéo** (vidéos uniquement, pas les commentaires via cet API).
3. **Modérer (approuver/rejeter)** des commentaires en attente de modération.
4. **Supprimer** vos propres commentaires ou les commentaires sur vos vidéos.
5. **Signaler** une vidéo pour contenu abusif.

## Outils Composio utilisés

- `YOUTUBE_INSERT_COMMENT_REPLY` – pour répondre.
- `YOUTUBE_RATE_VIDEO` – pour liker/disliker.
- `YOUTUBE_SET_COMMENT_MODERATION_STATUS` – pour approuver/rejeter.
- `YOUTUBE_DELETE_COMMENT` – pour supprimer.
- `YOUTUBE_REPORT_VIDEO_ABUSE` – pour signaler.

## Workflow type

### 1. Poster une réponse
- Identifie le `parentId` (ID du commentaire parent).
- Utilise `YOUTUBE_INSERT_COMMENT_REPLY`.

### 2. Modérer un message
- Indique le(s) `id` du commentaire.
- Choisis `moderationStatus` : `published` (approuvé), `rejected` (rejeté), `heldForReview`.

### 3. Liker une vidéo
- Passe `videoId` et `rating="like"`.

## Scripts disponibles

Dans `scripts/` se trouvent des scripts intégrant le **rate-limiting** pour protéger ton quota API.

- **`post_comment.py`** : Publie une réponse à un commentaire existant.
- **`moderate_comment.py`** : Approuve ou rejette un commentaire (avec option de ban).
- **`like_video.py`** : Like/dislike une vidéo.
- **`delete_comment.py`** : Supprime un commentaire par son ID.
- **`report_video.py`** : Signale une vidéo avec motif et description.
- **`rate_limiter.py`** : Gère les quotas (décorateur `@quota_decorator`).
- **`action_logger.py`** : Journalise les actions dans `~/.openclaw/logs/youtube_actions.json`.

## Configuration de sécurité

- **Rate-limit** : Le décorateur `quota_decorator` bloque l'action si le quota journalier est atteint (défaut: 10,000 unités/jour).
- **Audit** : Toutes les écritures sont tracées avec timestamp et cible.

## Exemples (Composio Multi Execute)

```python
# Liker une vidéo
tool_slug: YOUTUBE_RATE_VIDEO
arguments:
  id: "dQw4w9WgXcQ"
  rating: "like"

# Rejeter et bannir un auteur
tool_slug: YOUTUBE_SET_COMMENT_MODERATION_STATUS
arguments:
  id: "UgxeL_zwJICryCEB_HR4AaABAg"
  moderationStatus: "rejected"
  banAuthor: true
```

## Épingler un commentaire (pin)

L'API v3 ne propose pas directement l'action "épingler". Cependant, vous pouvez :
1. **Approuver le commentaire** (`moderationStatus="published"`).
2. **Aller sur l'interface YouTube** et l'épingler manuellement (c'est la seule façon).

Si vous automatisez via Selenium/Playwright, vous pouvez simuler le clic sur "Épingler" dans l'interface – mais cela sort du scope de ce skill.

## Erreurs courantes

- **403 Forbidden** : vous n'êtes pas propriétaire de la vidéo.
- **404 Not found** : le commentaire a déjà été supprimé.
- **400 Invalid value** : `moderationStatus` incorrect ou `banAuthor` utilisé avec un statut autre que `rejected`.
