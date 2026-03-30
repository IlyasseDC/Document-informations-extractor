# Document Extractor

Extracteur automatique d'informations personnelles depuis des documents d'identité (images ou PDF), propulsé par Claude via LangChain.

## Prérequis

- Python 3.10+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installé sur le système et accessible dans le PATH
  - Windows : télécharger l'installeur sur le lien ci-dessus, cocher "French" lors de l'installation
  - Linux : `sudo apt install tesseract-ocr tesseract-ocr-fra`
  - macOS : `brew install tesseract tesseract-lang`

## Installation

```bash
# 1. Cloner / télécharger le projet
cd document-extractor

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et renseigner votre clé Anthropic
```

## Lancement

```bash
streamlit run app.py
```

L'interface s'ouvre automatiquement sur `http://localhost:8501`.

## Utilisation

1. Uploadez un fichier JPG, PNG ou PDF via l'interface.
2. Patientez quelques secondes pendant l'extraction OCR et l'analyse par Claude.
3. Le JSON structuré s'affiche avec les informations personnelles trouvées.
4. Dépliez "Voir le texte brut extrait" pour consulter le texte OCR brut.

## Structure du projet

```
document-extractor/
├── app.py              # Interface Streamlit
├── agent.py            # Agent LangChain ReAct (Claude)
├── tools/
│   └── ocr_tool.py     # Outil OCR (pytesseract + pdfplumber)
├── requirements.txt
├── .env.example
└── README.md
```
