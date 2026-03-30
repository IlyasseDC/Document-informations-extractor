"""
tools/ocr_tool.py
-----------------
Outil LangChain d'extraction de texte depuis une image ou un PDF.
- Images (jpg, jpeg, png) → pytesseract (Tesseract OCR)
- PDF                      → pdfplumber
"""

import os
from langchain.tools import tool


@tool
def extract_text_tool(file_path: str) -> str:
    """
    Extrait le texte brut d'un document (image JPG/PNG ou PDF).
    Prend en entrée le chemin absolu du fichier et retourne le texte extrait.
    """
    # Vérification de l'existence du fichier
    if not os.path.exists(file_path):
        return f"Erreur : le fichier '{file_path}' est introuvable."

    extension = os.path.splitext(file_path)[1].lower()

    # --- Extraction depuis une image ---
    if extension in (".jpg", ".jpeg", ".png"):
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(file_path)
            # lang='fra+eng' pour prendre en charge le français et l'anglais
            texte = pytesseract.image_to_string(image, lang="fra+eng")
            return texte.strip() if texte.strip() else "Aucun texte détecté dans l'image."
        except Exception as e:
            return f"Erreur OCR sur l'image : {e}"

    # --- Extraction depuis un PDF ---
    elif extension == ".pdf":
        try:
            import pdfplumber

            pages_texte = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    texte_page = page.extract_text()
                    if texte_page:
                        pages_texte.append(f"--- Page {i + 1} ---\n{texte_page}")

            if pages_texte:
                return "\n\n".join(pages_texte)
            return "Aucun texte détecté dans le PDF."
        except Exception as e:
            return f"Erreur extraction PDF : {e}"

    # --- Format non supporté ---
    else:
        return f"Format de fichier non supporté : '{extension}'. Utilisez jpg, jpeg, png ou pdf."
