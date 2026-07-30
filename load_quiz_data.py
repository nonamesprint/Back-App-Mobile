# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# """
# Script pour charger les questions du quiz depuis un fichier JSON
# Exécution: python load_quiz_data.py
# """

# import os
# import sys
# import json
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
# django.setup()

# from plantes.models import QuizQuestion, QuizOption

# def load_quiz_data(json_file='data/quiz_questions.json'):
#     """Charge les questions du quiz depuis un fichier JSON"""
    
#     print("\n" + "="*60)
#     print("🌿 CHARGEMENT DES QUESTIONS DU QUIZ")
#     print("="*60 + "\n")
    
#     try:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print(f"❌ Fichier {json_file} introuvable")
#         return
#     except json.JSONDecodeError as e:
#         print(f"❌ Erreur de parsing JSON: {e}")
#         return
    
#     print(f"📊 Version: {data.get('version', 'N/A')}")
#     print(f"📅 Date: {data.get('date', 'N/A')}")
#     print(f"📝 Questions: {data.get('total_questions', 0)}\n")
    
#     # Supprimer les questions existantes
#     choix = input("Voulez-vous supprimer les questions existantes ? (o/n): ")
#     if choix.lower() == 'o':
#         QuizQuestion.objects.all().delete()
#         print("✅ Questions existantes supprimées\n")
    
#     created = 0
#     skipped = 0
    
#     for q_data in data['questions']:
#         # Vérifier si la question existe déjà
#         if QuizQuestion.objects.filter(question=q_data['question']).exists():
#             print(f"⏭️ Question déjà existante: {q_data['question'][:50]}...")
#             skipped += 1
#             continue
        
#         # Créer la question
#         question = QuizQuestion.objects.create(
#             question=q_data['question'],
#             niveau=q_data['niveau'],
#             points=q_data['points'],
#             temps_estime=q_data['temps_estime'],
#             est_active=True
#         )
        
#         # Créer les options
#         for opt_data in q_data['options']:
#             QuizOption.objects.create(
#                 question=question,
#                 texte=opt_data['texte'],
#                 est_correcte=opt_data['est_correcte'],
#                 ordre=opt_data['ordre']
#             )
        
#         created += 1
#         print(f"✅ {created:2d}. {q_data['question'][:50]}...")
    
#     print("\n" + "="*60)
#     print("📊 RÉSUMÉ")
#     print("="*60)
#     print(f"✅ Questions créées: {created}")
#     print(f"⏭️ Questions ignorées (déjà existantes): {skipped}")
#     print(f"📝 Total dans la base: {QuizQuestion.objects.count()} questions")
#     print("="*60 + "\n")

# if __name__ == "__main__":
#     load_quiz_data()




#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour charger les questions du quiz depuis un fichier JSON
Usage:
    python load_quiz_data.py                    # Charge sans supprimer
    python load_quiz_data.py --clear           # Supprime avant de charger
    python load_quiz_data.py --force           # Force le rechargement
    python load_quiz_data.py --clear --force   # Supprime et recharge
"""

import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from plantes.models import QuizQuestion, QuizOption

def load_quiz_data(json_file='data/quiz_questions.json', clear=False, force=False):
    """Charge les questions du quiz depuis un fichier JSON"""
    
    print("\n" + "="*60)
    print("🌿 CHARGEMENT DES QUESTIONS DU QUIZ")
    print("="*60 + "\n")
    
    # Vérifier l'existence du fichier
    if not os.path.exists(json_file):
        print(f"❌ Fichier {json_file} introuvable")
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return False
    
    print(f"📊 Version: {data.get('version', 'N/A')}")
    print(f"📅 Date: {data.get('date', 'N/A')}")
    print(f"📝 Questions: {data.get('total_questions', 0)}\n")
    
    # Supprimer les questions existantes si demandé
    if clear:
        QuizQuestion.objects.all().delete()
        print("🗑️  Questions existantes supprimées\n")
    
    created = 0
    skipped = 0
    
    for q_data in data.get('questions', []):
        # Vérifier si la question existe déjà
        if QuizQuestion.objects.filter(question=q_data['question']).exists():
            if force:
                # En mode force, on supprime l'ancienne et on la recrée
                QuizQuestion.objects.filter(question=q_data['question']).delete()
                print(f"🔄 Rechargement: {q_data['question'][:50]}...")
            else:
                print(f"⏭️ Question déjà existante: {q_data['question'][:50]}...")
                skipped += 1
                continue
        
        # Créer la question
        question = QuizQuestion.objects.create(
            question=q_data['question'],
            niveau=q_data.get('niveau', 1),
            points=q_data.get('points', 10),
            temps_estime=q_data.get('temps_estime', 30),
            est_active=q_data.get('est_active', True)
        )
        
        # Créer les options
        for opt_data in q_data.get('options', []):
            QuizOption.objects.create(
                question=question,
                texte=opt_data['texte'],
                est_correcte=opt_data['est_correcte'],
                ordre=opt_data.get('ordre', 0)
            )
        
        created += 1
        print(f"✅ {created:2d}. {q_data['question'][:50]}...")
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"✅ Questions créées: {created}")
    print(f"⏭️ Questions ignorées (déjà existantes): {skipped}")
    print(f"📝 Total dans la base: {QuizQuestion.objects.count()} questions")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    # Analyse des arguments
    clear = '--clear' in sys.argv or '-c' in sys.argv
    force = '--force' in sys.argv or '-f' in sys.argv
    
    # Afficher l'aide
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    # Exécuter le chargement
    success = load_quiz_data(clear=clear, force=force)
    sys.exit(0 if success else 1)