---
name: youtube-writer
description: Encapsule toutes les actions d'écriture YouTube : poster une réponse, liker un commentaire, épingler, signaler, supprimer. Centralise les logs et le rate‑limiting pour respecter les quotas (écritures = 50 unités). Utiliser quand l'utilisateur demande à interagir avec YouTube : "réponds à ce commentaire", "like cette vidéo", "signale ce contenu", "supprime mon commentaire", "épingle ce commentaire". Ce skill est la sortie du pipeline de traitement des commentaires.
---

# YouTube Writer Skill

Ce skill regroupe toutes les actions d'écriture sur YouTube via l'API YouTube Data v3. Il inclut un système de log et de rate‑limiting pour éviter de dépasser les quotas.

## Fonctionnalités

1. **Poster une réponse** à un commentaire (`YOUTUBE_CREATE_COMMENT_REPLY`).
2. **Poster un commentaire** sur une vidéo (`YOUTUBE_POST_COMMENT`).
3. **Liker/disliker une vidéo** (`YOUTUBE_RATE_VIDEO`).
4. **Supprimer un commentaire** (`YOUTUBE_DELETE_COMMENT`).
5. **Signaler une vidéo** abusive (`YOUTUBE_REPORT_VIDEO_ABUSE`).
6. **Modérer un commentaire** (approuver, rejeter, tenir en attente) (`YOUTUBE_SET_COMMENT_MODERATION_STATUS`).
7. **Mettre à jour un commentaire** (`YOUTUBE_UPDATE_COMMENT`).

**Note :** L'action "épingler un commentaire" (pin) n'est pas directement exposée dans l'API v3 ; elle peut être simulée en approuvant le commentaire (`moderationStatus=published`) et en le mettant en avant via l'interface YouTube.

## Requêtes API utilisées

- `comments.insert` (en réponse)
- `commentThreads.insert` (nouveau fil)
- `videos.rate`
- `comments.delete`
- `videos.reportAbuse`
- `comments.setModerationStatus`
- `comments.update`

## Workflow type

1. **Vérifier le quota** disponible (via le rate‑limiter).
2. **Journaliser l'action** avant exécution (logs).
3. **Appeler l'API Google correspondante**.
4. **Vérifier la réponse** et journaliser le résultat.
5. **Mettre à jour les compteurs** de quota.

## Comment utiliser ce skill

### 1. Répondre à un commentaire
```python
# API: comments().insert()
arguments:
  parentId: "Ugzoh2L2gIZm-rzh6hp4AaABAg"
  textOriginal: "Merci pour votre retour !"
```

### 2. Liker une vidéo
```python
# API: videos().rate()
arguments:
  id: "dQw4w9WgXcQ"
  rating: "like"   # ou "dislike", "none" pour retirer
```

### 3. Signaler une vidéo
```python
# API: videos().reportAbuse()
arguments:
  videoId: "dQw4w9WgXcQ"
  reasonId: "H"   # Harassment or bullying
  comments: "Contenu harcelant."
```

### 4. Modérer un commentaire (épingle/approbation)
```python
# API: comments().setModerationStatus()
arguments:
  id: "Ugzoh2L2gIZm-rzh6hp4AaABAg"
  moderationStatus: "published"   # "heldForReview", "likelySpam", "rejected"
```

### 5. Supprimer un commentaire
```python
# API: comments().delete()
arguments:
  id: "Ugzoh2L2gIZm-rzh6hp4AaABAg"
```

## Scripts disponibles

Dans `scripts/` :

- **`rate_limiter.py`** – Gère les quotas (50 unités/écriture) et espace les requêtes.
- **`action_logger.py`** – Journalise chaque action (timestamp, type, cible, succès/erreur).
- **`reply_to_comment.py`** – Répond à un commentaire avec log et rate‑limiting.
- **`like_video.py`** – Like/dislike une vidéo.
- **`moderate_comment.py`** – Modère un commentaire (publish, hold, spam).
- **`report_video.py`** – Signale une vidéo abusive.
- **`delete_comment.py`** – Supprime un commentaire.

**Usage dans le workbench :**
```python
from scripts.reply_to_comment import reply_to_comment
success, log_id = reply_to_comment(parent_id="...", text="Merci !")
```

## Références

- **`references/quota_guide.md`** – Coûts en quota, limites de taux, bonnes pratiques.
- **`references/moderation_status.md`** – Signification des status de modération.
- **`references/abuse_reasons.md`** – Codes `reasonId` pour les signalements.

## Log centralisé

Toutes les actions passent par `action_logger.py` qui écrit dans un fichier JSON structuré (`logs/actions_YYYY‑MM‑DD.json`). Chaque entrée contient :

```json
{
  "timestamp": "2026‑04‑21T14:30:00Z",
  "action": "CREATE_COMMENT_REPLY",
  "target": {"parentId": "..."},
  "success": true,
  "response": {...},
  "quota_used": 50
}
```

## Rate‑limiting

- **Coût par écriture** : 50 unités de quota.
- **Limite quotidienne** : 10 000 unités par défaut → max 200 écritures/jour.
- **Espacement automatique** : le rate‑limiter attend 1 seconde entre les écritures pour éviter les erreurs 429.

## Pièges connus

- **403 Forbidden** : L'utilisateur n'a pas les droits nécessaires (ex. supprimer un commentaire d'un autre).
- **404 Not found** : La ressource (vidéo, commentaire) a été supprimée.
- **429 Too many requests** : Rate‑limiter insuffisant ; augmenter l'espacement.
- **Quota dépassé** : Surveiller les compteurs et arrêter les écritures.

## Exemple complet (workbench)

Voir `examples/workbench_demo.py` pour un scénario de réponse groupée aux commentaires en attente.
