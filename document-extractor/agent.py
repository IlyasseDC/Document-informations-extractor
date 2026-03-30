"""
agent.py
--------
Crée et expose un agent LangChain ReAct utilisant Claude (claude-sonnet-4-20250514).
L'agent dispose de l'outil OCR et structure les informations personnelles en JSON.
"""

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from tools.ocr_tool import extract_text_tool

# Chargement de la clé API depuis le fichier .env
load_dotenv()

# ---------------------------------------------------------------------------
# System prompt de l'agent
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Tu es un assistant spécialisé dans l'extraction d'informations personnelles depuis des documents officiels.

Ton fonctionnement est le suivant :
1. Quand l'utilisateur te fournit le chemin d'un fichier, tu DOIS appeler l'outil `extract_text_tool` avec ce chemin pour extraire le texte brut du document.
2. Une fois le texte extrait, tu analyses son contenu et tu identifies les informations personnelles présentes.
3. Tu retournes uniquement un objet JSON valide contenant les champs trouvés parmi les suivants (n'inclus que les champs effectivement présents dans le document) :
   - nom
   - prenom
   - date_de_naissance
   - adresse
   - numero_piece_identite
   - nationalite
   - date_expiration

GUARDRAIL IMPORTANT : Si la demande de l'utilisateur n'est PAS liée à l'extraction d'informations depuis un document, réponds UNIQUEMENT avec :
"Je suis uniquement capable d'extraire des informations personnelles depuis un document."

Format de réponse finale (après avoir utilisé l'outil) : un JSON valide et uniquement le JSON, sans texte supplémentaire.

Tu as accès aux outils suivants :
{tools}

Utilise le format suivant :

Question: la question de l'utilisateur
Thought: réfléchis à ce que tu dois faire
Action: le nom de l'outil à utiliser, doit être l'un de [{tool_names}]
Action Input: l'entrée pour l'outil
Observation: le résultat de l'outil
... (répète Thought/Action/Action Input/Observation si nécessaire)
Thought: j'ai maintenant la réponse finale
Final Answer: le JSON structuré avec les informations personnelles trouvées

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def creer_agent() -> AgentExecutor:
    """
    Instancie et retourne un AgentExecutor LangChain ReAct avec Claude.
    """
    # Initialisation du modèle Claude via langchain-anthropic
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0,  # Déterministe pour l'extraction structurée
        max_tokens=2048,
    )

    # Liste des outils disponibles pour l'agent
    outils = [extract_text_tool]

    # Construction du prompt ReAct
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

    # Création de l'agent ReAct
    agent = create_react_agent(llm=llm, tools=outils, prompt=prompt)

    # Encapsulation dans un AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=outils,
        verbose=True,          # Affiche les étapes dans le terminal
        handle_parsing_errors=True,
        max_iterations=5,      # Limite le nombre d'appels d'outils
    )

    return agent_executor


def extraire_informations(chemin_fichier: str) -> str:
    """
    Point d'entrée principal : lance l'agent sur le fichier fourni.

    Args:
        chemin_fichier: Chemin absolu vers le fichier à analyser.

    Returns:
        Chaîne JSON contenant les informations personnelles extraites.
    """
    agent_executor = creer_agent()

    # Construction de la question envoyée à l'agent
    question = (
        f"Extrais les informations personnelles du document situé à : {chemin_fichier}"
    )

    resultat = agent_executor.invoke({"input": question})
    return resultat.get("output", "Aucune information extraite.")
