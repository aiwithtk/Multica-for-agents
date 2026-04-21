# Raisons de signalement (abuse report)

L'outil `YOUTUBE_REPORT_VIDEO_ABUSE` utilise un code `reasonId` pour spécifier le type de contenu abusif.

## Codes `reasonId`

| Code | Signification | Description |
|------|---------------|-------------|
| **`N`** | **Sex or nudity** | Contenu sexuellement explicite ou nudité. |
| **`V`** | **Violent, hateful, or dangerous** | Violence, discours haineux, incitation à la haine, ou contenu dangereux. |
| **`C`** | **Child abuse** | Abus sur mineur, exploitation infantile. |
| **`M`** | **Medical misinformation** | Désinformation médicale (ex. faux remèdes, théories non prouvées). |
| **`E`** | **Violent extremism** | Extrémisme violent, terrorisme, recrutement. |
| **`H`** | **Harassment or bullying** | Harcèlement, intimidation, cyber‑harcèlement. |

## Champs secondaires

- **`secondaryReasonId`** : précise la sous‑catégorie (optionnel). Les valeurs dépendent de `reasonId`. Pour les obtenir, appelez `YOUTUBE_LIST_VIDEO_ABUSE_REPORT_REASONS` avec `part=snippet`.
- **`comments`** : texte libre pour expliquer le signalement.
- **`language`** : code langue de l'utilisateur qui signale (ex. `"fr"`).

## Exemples d'utilisation

### Signalement pour harcèlement
```python
tool_slug: YOUTUBE_REPORT_VIDEO_ABUSE
arguments:
  videoId: "dQw4w9WgXcQ"
  reasonId: "H"
  comments: "Cette vidéo cible une personne avec des menaces répétées."
  language: "fr"
```

### Signalement pour désinformation médicale
```python
tool_slug: YOUTUBE_REPORT_VIDEO_ABUSE
arguments:
  videoId: "dQw4w9WgXcQ"
  reasonId: "M"
  comments: "Prétend guérir le cancer avec de l'eau citronnée, aucune preuve scientifique."
```

## Récupérer les labels localisés

Pour afficher les libellés complets dans une langue donnée :

```python
tool_slug: YOUTUBE_LIST_VIDEO_ABUSE_REPORT_REASONS
arguments:
  hl: "fr_FR"
  part: "snippet"
```

La réponse contient une liste de `items` avec `id` (le code) et `snippet.label` (le libellé traduit).

## Limitations

- **Quota** : 50 unités par signalement.
- **Authentification requise** : vous devez être connecté avec un compte Google.
- **Pas de rétroaction** : YouTube ne confirme pas l'issue du signalement.
- **Abus du système** : les signalements malveillants peuvent entraîner la suspension de votre compte.

## Bonnes pratiques

1. **Choisir la raison la plus précise**.
2. **Remplir `comments`** avec une explication concise.
3. **Ne pas signaler massivement** sous peine de déclencher des limitations.
4. **Vérifier que la vidéo enfreint bien les [Règles de la communauté YouTube](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/)**.

## Liens

- [Documentation officielle de `videos.reportAbuse`](https://developers.google.com/youtube/v3/docs/videos/reportAbuse)
- [Règles de la communauté YouTube](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/)
