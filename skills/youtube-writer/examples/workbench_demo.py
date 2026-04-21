#!/usr/bin/env python3
"""
Démonstration d'utilisation du skill youtube‑writer dans le sandbox Composio.
Scénario : répondre aux commentaires en attente (simulé) avec rate‑limiting et log.
"""

import sys
sys.path.insert(0, 'scripts')

from rate_limiter import get_quota_status
from action_logger import summary_today, get_recent_logs
from reply_to_comment import reply_to_comment
from like_video import like_video
from moderate_comment import moderate_comment

def demo_single_actions():
    """Exécute quelques actions individuelles (simulées si pas d'IDs réels)."""
    print("=== Démonstration YouTube Writer ===\n")
    
    # 1. État du quota
    quota = get_quota_status()
    print(f"📊 Quota aujourd'hui : {quota['quota_used_today']}/{quota['quota_daily_limit']}")
    print(f"   Actions possibles : {quota['can_perform_action']}")
    print()
    
    # 2. Résumé des actions du jour
    summary = summary_today()
    print(f"📈 Actions aujourd'hui : {summary['total_actions']} "
          f"({summary['successful']} ✅, {summary['failed']} ❌)")
    print(f"   Quota consommé : {summary['quota_used']}")
    print()
    
    # 3. Dernières actions
    print("🕐 5 dernières actions :")
    for log in get_recent_logs(5):
        ts = log.get('timestamp', '')[:19]
        status = '✅' if log.get('success') else '❌'
        print(f"   {ts} {status} {log.get('action')} -> {log.get('target')}")
    print()
    
    # 4. Actions simulées (commentées car nécessitent de vrais IDs)
    print("🎬 Actions simulées (décommentez et remplacez les IDs) :")
    print()
    print("# Répondre à un commentaire")
    print("""
# parent_id = 'Ugzoh2L2gIZm-rzh6hp4AaABAg'  # remplacer par un vrai ID
# result = reply_to_comment(parent_id, 'Merci pour votre retour !')
# print(f'Réponse postée : {result.get("success")}')
""")
    
    print("# Liker une vidéo")
    print("""
# video_id = 'dQw4w9WgXcQ'  # remplacer par un vrai ID
# result = like_video(video_id, 'like')
# print(f'Vidéo likée : {result.get("success")}')
""")
    
    print("# Modérer un commentaire (approuver)")
    print("""
# comment_id = 'UgxeL_zwJICryCEB_HR4AaABAg'  # remplacer par un vrai ID
# result = moderate_comment([comment_id], 'published')
# print(f'Commentaire approuvé : {result.get("success")}')
""")
    
    print("\n🔧 Pour exécuter ces actions, éditez le script avec de vrais IDs YouTube.")


def simulate_pending_replies():
    """Simule une réponse groupée aux commentaires en attente."""
    print("\n=== Scénario : Réponses groupées aux commentaires en attente ===\n")
    
    # Liste simulée de commentaires en attente (ID, texte de réponse)
    pending = [
        ("Ugzoh2L2gIZm-rzh6hp4AaABAg", "Merci pour votre commentaire !"),
        ("UgyKBz5sMCzFBkQdYXl4AaABAg", "Nous prenons note de votre suggestion."),
        ("UgxeL_zwJICryCEB_HR4AaABAg", "Excellente question, nous y répondrons en direct."),
    ]
    
    print(f"📋 {len(pending)} commentaires en attente de réponse")
    quota = get_quota_status()
    needed_quota = len(pending) * 50
    if quota['quota_remaining'] < needed_quota:
        print(f"❌ Quota insuffisant. Il reste {quota['quota_remaining']} unités, "
              f"besoin de {needed_quota}.")
        return
    
    print("⚠️  Ce scénario est simulé. Pour l'exécuter, décommentez le code ci‑dessous.")
    print("""
for parent_id, reply_text in pending:
    result = reply_to_comment(parent_id, reply_text)
    if result.get('success'):
        print(f'✅ Réponse à {parent_id[:12]}...')
    else:
        print(f'❌ Erreur : {result.get("error")}')
""")
    
    print("\n🎯 Fin de la démonstration.")


if __name__ == "__main__":
    demo_single_actions()
    simulate_pending_replies()
