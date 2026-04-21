# Gestion des quotas YouTube Data API v3

Les écritures coûtent cher en quota. Ce guide aide à planifier et surveiller l'utilisation.

## Coûts par opération

| Opération | Coût (unités) | Outil Composio |
|-----------|---------------|----------------|
| **Écritures** | **50** | `YOUTUBE_CREATE_COMMENT_REPLY`, `YOUTUBE_POST_COMMENT`, `YOUTUBE_RATE_VIDEO`, `YOUTUBE_DELETE_COMMENT`, `YOUTUBE_REPORT_VIDEO_ABUSE`, `YOUTUBE_SET_COMMENT_MODERATION_STATUS`, `YOUTUBE_UPDATE_COMMENT` |
| **Lectures** | 1 (sauf recherche) | `YOUTUBE_LIST_COMMENT_THREADS2`, `YOUTUBE_LIST_COMMENTS`, `YOUTUBE_GET_VIDEO_DETAILS_BATCH` |
| **Recherche** (`search.list`) | 100 | (utilisé en fallback par `YOUTUBE_LIST_CHANNEL_VIDEOS`) |
| **Upload** | 1600 | (non utilisé dans ce skill) |

## Quotas par défaut

- **Quota quotidien** : 10 000 unités (projet Google Cloud standard).
- **Quota par minute** : environ 300 000 unités (rarement limitant).

## Calcul des limites d'écriture

Avec 10 000 unités/jour :
- **Max écritures/jour** : `10 000 / 50 = 200` actions.
- **Marge de sécurité** : réserver 20 % pour les lectures → **160 écritures/jour max**.

Si vous avez besoin de plus, demandez une augmentation de quota dans [Google Cloud Console](https://console.cloud.google.com/apis/dashboard).

## Rate‑limiting recommandé

Pour éviter les erreurs `429 Too many requests` :

- **Espacement minimum** : 1 seconde entre chaque écriture.
- **Batch size** : ne pas envoyer plus de 10 écritures en 10 secondes.
- **Surveillance** : utiliser le script `rate_limiter.py` pour suivre la consommation.

## Surveillance du quota

Dans Google Cloud Console :
- **API & Services** → **Dashboard** → **YouTube Data API v3**.
- Graphique **Quota usage** (par jour).
- **Metrics** → `youtube.googleapis.com/quota/used`.

Vous pouvez aussi implémenter un webhook pour alerter quand le quota atteint 80 %.

## Bonnes pratiques

1. **Toujours vérifier le quota disponible** avant une série d'écritures.
2. **Journaliser chaque action** pour reconstituer la consommation.
3. **Préférer les lectures** (1 unité) aux écritures (50 unités).
4. **Éviter `search.list`** si possible (coût 100).
5. **Utiliser `maxResults`** pour limiter les pages de lecture.
6. **Tester avec un quota réduit** en développement.

## Exemple de calcul

```
Actions planifiées :
- Répondre à 50 commentaires : 50 × 50 = 2 500 unités
- Liker 10 vidéos : 10 × 50 = 500 unités
- Supprimer 5 commentaires : 5 × 50 = 250 unités
Total = 3 250 unités (32,5 % du quota quotidien)
```

## Liens utiles

- [Calculateur de quota officiel](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Demande d'augmentation de quota](https://support.google.com/code/contact/quota_increase)
- [Documentation des quotas](https://developers.google.com/youtube/v3/getting-started#quota)
