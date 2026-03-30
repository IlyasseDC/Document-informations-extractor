"""
app.py
------
Interface Streamlit pour l'extracteur d'informations personnelles.
L'utilisateur uploade un document (image ou PDF) et l'agent retourne
les informations structurées en JSON.
"""

import os
import json
import tempfile

import streamlit as st
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

# Import de l'agent (après load_dotenv pour que la clé API soit disponible)
from agent import extraire_informations
from tools.ocr_tool import extract_text_tool

# ---------------------------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Extracteur de documents",
    page_icon="🪪",
    layout="centered",
)

st.title("Extracteur d'informations personnelles")
st.markdown(
    "Uploadez un document d'identité (image ou PDF) pour en extraire "
    "automatiquement les informations personnelles."
)

# ---------------------------------------------------------------------------
# Zone d'upload
# ---------------------------------------------------------------------------
fichier_uploade = st.file_uploader(
    label="Choisissez un fichier",
    type=["jpg", "jpeg", "png", "pdf"],
    help="Formats acceptés : JPG, JPEG, PNG, PDF",
)

# ---------------------------------------------------------------------------
# Traitement du fichier uploadé
# ---------------------------------------------------------------------------
if fichier_uploade is not None:
    st.info(f"Fichier reçu : **{fichier_uploade.name}**")

    with st.spinner("Extraction en cours… Cela peut prendre quelques secondes."):
        try:
            # Sauvegarde temporaire du fichier uploadé
            suffixe = os.path.splitext(fichier_uploade.name)[1].lower()
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffixe, dir=tempfile.gettempdir()
            ) as tmp:
                tmp.write(fichier_uploade.read())
                chemin_tmp = tmp.name

            # --- Extraction du texte brut via l'outil OCR directement ---
            texte_brut = extract_text_tool.invoke(chemin_tmp)

            # --- Appel de l'agent pour structurer les informations ---
            reponse_agent = extraire_informations(chemin_tmp)

            # Nettoyage du fichier temporaire
            os.unlink(chemin_tmp)

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
            st.stop()

    # --- Affichage du JSON structuré ---
    st.subheader("Informations extraites")

    # Tentative de parsing du JSON retourné par l'agent
    try:
        # Nettoyage au cas où l'agent encapsule le JSON dans des balises markdown
        reponse_nettoyee = reponse_agent.strip()
        if reponse_nettoyee.startswith("```"):
            lignes = reponse_nettoyee.split("\n")
            # Supprime la première et la dernière ligne (``` json / ```)
            reponse_nettoyee = "\n".join(lignes[1:-1])

        donnees_json = json.loads(reponse_nettoyee)
        st.json(donnees_json)

    except json.JSONDecodeError:
        # Si ce n'est pas du JSON valide, affiche la réponse brute
        st.warning("La réponse de l'agent n'est pas un JSON valide. Réponse brute :")
        st.text(reponse_agent)

    # --- Expander pour le texte brut OCR ---
    with st.expander("Voir le texte brut extrait"):
        st.text_area(
            label="Texte OCR",
            value=texte_brut,
            height=300,
            disabled=True,
        )
