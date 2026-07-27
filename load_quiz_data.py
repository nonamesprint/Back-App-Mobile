#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour charger les questions du quiz depuis un fichier JSON
Exécution: python load_quiz_data.py
"""

import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from plantes.models import QuizQuestion, QuizOption

def load_quiz_data(json_file='data/quiz_questions.json'):
    """Charge les questions du quiz depuis un fichier JSON"""
    
    print("\n" + "="*60)
    print("🌿 CHARGEMENT DES QUESTIONS DU QUIZ")
    print("="*60 + "\n")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier {json_file} introuvable")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return
    
    print(f"📊 Version: {data.get('version', 'N/A')}")
    print(f"📅 Date: {data.get('date', 'N/A')}")
    print(f"📝 Questions: {data.get('total_questions', 0)}\n")
    
    # Supprimer les questions existantes
    choix = input("Voulez-vous supprimer les questions existantes ? (o/n): ")
    if choix.lower() == 'o':
        QuizQuestion.objects.all().delete()
        print("✅ Questions existantes supprimées\n")
    
    created = 0
    skipped = 0
    
    for q_data in data['questions']:
        # Vérifier si la question existe déjà
        if QuizQuestion.objects.filter(question=q_data['question']).exists():
            print(f"⏭️ Question déjà existante: {q_data['question'][:50]}...")
            skipped += 1
            continue
        
        # Créer la question
        question = QuizQuestion.objects.create(
            question=q_data['question'],
            niveau=q_data['niveau'],
            points=q_data['points'],
            temps_estime=q_data['temps_estime'],
            est_active=True
        )
        
        # Créer les options
        for opt_data in q_data['options']:
            QuizOption.objects.create(
                question=question,
                texte=opt_data['texte'],
                est_correcte=opt_data['est_correcte'],
                ordre=opt_data['ordre']
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

if __name__ == "__main__":
    load_quiz_data()
