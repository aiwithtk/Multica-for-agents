# Modération des commentaires YouTube

L'outil `YOUTUBE_SET_COMMENT_MODERATION_STATUS` permet de contrôler la visibilité des commentaires sur vos propres vidéos.

## Statuts disponibles

| `moderationStatus` | Effet | Usage typique |
|-------------------|-------|---------------|
| **`published`** | Rend le commentaire visible publiquement. | **Approuver** un commentaire légitime (équivalent à "épingle" si vous le mettez en avant via l'interface YouTube). |
| **`heldForReview`** | Retire le commentaire de la vue publique et le place en file d'attente de modération. | **Mettre en attente** un commentaire douteux pour inspection manuelle. |
| **`rejected`** | Supprime le commentaire (semblable à une suppression). | **Rejeter** un commentaire inapproprié. Option `banAuthor` permet de bannir l'auteur. |

## Champs obligatoires

- **`id`** : liste d'IDs de commentaires séparés par des virgules (IDs de commentaire, pas de thread). Ex: `"UgxeL_zwJICryCEB_HR4AaABAg,UgyKBz5sMCzFBkQdYXl4AaABAg"`.
- **`moderationStatus`** : l'un des trois statuts ci‑dessus.

## Option `banAuthor`

- **Applicable uniquement** quand `moderationStatus="rejected"`.
- **`banAuthor=true`** : ajoute l'auteur du commentaire à la liste des bannis de la chaîne (ils ne pourront plus commenter).
- **`banAuthor=false`** (défaut) : supprime seulement le commentaire.

## Limitations

- **Droits requis** : vous devez être le propriétaire de la vidéo (ou avoir les droits de modération).
- **IDs valides** : seulement les commentaires sur vos propres vidéos.
- **Quota** : 50 unités par appel, quel que soit le nombre d'IDs.

## Exemples

### Approuver un commentaire
```python
tool_slug: YOUTUBE_SET_COMMENT_MODERATION_STATUS
arguments:
  id: "UgxeL_zwJICryCEB_HR4AaABAg"
  moderationStatus: "published"
```

### Mettre en attente pour modération
```python
tool_slug: YOUTUBE_SET_COMMENT_MODERATION_STATUS
arguments:
  id: "UgxeL_zwJICryCEB_HR4AaABAg,UgyKBz5sMCzFBkQdYXl4AaABAg"
  moderationStatus: "heldForReview"
```

### Rejeter et bannir l'auteur
```python
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
