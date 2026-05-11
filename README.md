# Potag'IA

Potag'IA est une application mobile (Expo/React Native) avec un backend FastAPI.
Elle propose un tableau de bord de jardin, un calendrier mensuel interactif et
des recommandations de plantation.

## Fonctionnalites

- Calendrier mensuel cliquable avec details par jour
- Recommandations de plantation (ex: varietes de tomates)
- Bibliotheque de plantes
- Backend REST FastAPI + base Postgres (config locale)

## Prerequis

- Node.js 18+
- Python 3.11+
- Postgres local (ou credentials equivalentes)

## Installation

1. Frontend
   - npm install

2. Backend
   - cd backend
   - python -m venv venv
   - .\venv\Scripts\activate
   - pip install -r requirements.txt

## Lancer le backend

- cd backend
- python -m uvicorn main:app --host 0.0.0.0 --reload

## Lancer le frontend (Expo)

- npm run start

## Configuration reseau (Expo Go)

Si l'app tourne sur un telephone, utilisez l'IP locale du PC dans les requetes
API (ex: http://172.23.119.189:8000). Les fichiers principaux sont:

- app/(tabs)/index.tsx
- app/(tabs)/garden.tsx
- app/(tabs)/library.tsx

## Structure du projet

Projetdetudes/
app/ Frontend Expo (mobile)
assets/ Images / icones
backend/ API FastAPI
components/ Composants UI
constants/ Constantes

## Notes

- Le calendrier mensuel et le modal de details se trouvent dans app/(tabs)/index.tsx.
- Les varietes de tomates sont definies en dur pour l'instant (placeholder IA).
