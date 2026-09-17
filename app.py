import json
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Rugby App - Gestionnaire de Séances",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Insert du CSS personnalisé pour le style mobile & design
st.markdown(
    """
    <style>
    /* Styles généraux */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* En-tête / Header */
    .main-title {
        color: #1b4332;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        margin-bottom: 0px;
        text-align: center;
    }
    .sub-title {
        color: #555555;
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }

    /* Cartes pour les exercices */
    .exo-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2d6a4f;
    }
    .exo-card-avants { border-left-color: #81b29a; }
    .exo-card-arrieres { border-left-color: #e07a5f; }
    .exo-card-collectif { border-left-color: #3d405b; }

    /* Customisation des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
    }

    /* Masquer le pied de page Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

DB_FILE = "exercices_rugby.json"
CATEGORIES_GROUPE = ["Avants", "Arrières", "Collectif"]
TYPES_EXERCICE = [
    "Échauffement",
    "Lancement / Combinaison",
    "Duels / Appuis",
    "Conservation / Ruck",
    "Surnombre / 4vs4",
    "Jeu au pied",
    "Match / Spécifique",
]


def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_exercice(exo):
    data = load_data()
    data.append(exo)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- HEADER AVEC LOGO ET TITRE ---
col_logo, col_header = st.columns([1, 4])
with col_logo:
    # Remplace l'URL ci-dessous par le lien vers le logo de ton club si tu en as un
    st.image("images.png", width=80)    )
with col_header:
    st.markdown(
        "<h1 class='main-title'>RUGBY COACH APP</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p class='sub-title'>Gestion de la banque d'exercices & préparation des séances</p>",
        unsafe_allow_html=True,
    )

tab1, tab2, tab3 = st.tabs(
    ["📋 Créer une Séance", "📚 Banque d'Exercices", "➕ Ajouter un Exercice"]
)

# --- ONGLET 1 : CRÉER UNE SÉANCE ---
with tab1:
    data = load_data()

    if not data:
        st.info("La banque d'exercices est vide. Ajoutez un premier exercice !")
    else:
        titre_seance = st.text_input("Intitulé de la séance", "Séance du Mardi")

        exos_avants = [
            f"{e['titre']} [{e['type']}]"
            for e in data
            if e.get("groupe") == "Avants"
        ]
        exos_arrieres = [
            f"{e['titre']} [{e['type']}]"
            for e in data
            if e.get("groupe") == "Arrières"
        ]
        exos_collectif = [
            f"{e['titre']} [{e['type']}]"
            for e in data
            if e.get("groupe") == "Collectif"
        ]

        st.subheader("1. Ateliers Séparés (Simultanés)")
        col_av, col_arr = st.columns(2)
        with col_av:
            sel_avant = st.selectbox(
                "🐗 Groupe Avants", ["Aucun"] + exos_avants, key="sel_av"
            )
        with col_arr:
            sel_arriere = st.selectbox(
                "⚡ Groupe Arrières", ["Aucun"] + exos_arrieres, key="sel_arr"
            )

        duree_ateliers = st.number_input(
            "Durée des ateliers (min)", min_value=0, max_value=60, value=20
        )

        st.subheader("2. Séquences Collectives")
        sel_collectifs = st.multiselect(
            "🤝 Exercices tout groupe :", exos_collectif
        )

        st.markdown("---")
        st.markdown("### 📄 Déroulé de la séance")

        total_duration = 0

        # Bloc Ateliers
        if sel_avant != "Aucun" or sel_arriere != "Aucun":
            st.markdown(
                f"#### ⏱️ Ateliers Séparés — **{duree_ateliers} min**"
            )
            c1, c2 = st.columns(2)
            with c1:
                if sel_avant != "Aucun":
                    titre_clean = sel_avant.split(" [")[0]
                    exo = next(e for e in data if e["titre"] == titre_clean)
                    st.markdown(
                        f"""
                    <div class='exo-card exo-card-avants'>
                        <strong>🐗 Avants : {exo['titre']}</strong><br>
                        <small>{exo['type']} | Espace : {exo['espace']}</small><br><br>
                        {exo['consignes']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            with c2:
                if sel_arriere != "Aucun":
                    titre_clean = sel_arriere.split(" [")[0]
                    exo = next(e for e in data if e["titre"] == titre_clean)
                    st.markdown(
                        f"""
                    <div class='exo-card exo-card-arrieres'>
                        <strong>⚡ Arrières : {exo['titre']}</strong><br>
                        <small>{exo['type']} | Espace : {exo['espace']}</small><br><br>
                        {exo['consignes']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

            total_duration += duree_ateliers

        # Bloc Collectif
        if sel_collectifs:
            st.markdown("#### 🤝 Séquences Collectives")
            for idx, item in enumerate(sel_collectifs):
                titre_clean = item.split(" [")[0]
                exo = next(e for e in data if e["titre"] == titre_clean)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(
                        f"""
                    <div class='exo-card exo-card-collectif'>
                        <strong>{idx+1}. {exo['titre']}</strong> ({exo['type']})<br>
                        <small>Espace : {exo['espace']}</small><br><br>
                        {exo['consignes']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                with col_b:
                    dur = st.number_input(
                        "Durée (min)",
                        value=int(exo["duree"]),
                        key=f"dur_coll_{idx}",
                    )
                    total_duration += dur

        st.metric("Durée Totale estimée", f"{total_duration} min")

# --- ONGLET 2 : BANQUE D'EXERCICES ---
with tab2:
    st.header("Banque d'Exercices")
    data = load_data()

    if data:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            grp_filter = st.selectbox(
                "Filtrer par Groupe :", ["Tous"] + CATEGORIES_GROUPE
            )
        with col_f2:
            type_filter = st.selectbox(
                "Filtrer par Type :", ["Tous"] + TYPES_EXERCICE
            )

        filtered_data = data
        if grp_filter != "Tous":
            filtered_data = [
                e for e in filtered_data if e.get("groupe") == grp_filter
            ]
        if type_filter != "Tous":
            filtered_data = [
                e for e in filtered_data if e.get("type") == type_filter
            ]

        for exo in filtered_data:
            badge = (
                "🐗"
                if exo.get("groupe") == "Avants"
                else ("⚡" if exo.get("groupe") == "Arrières" else "🤝")
            )
            with st.expander(
                f"{badge} {exo['titre']} — {exo.get('groupe', 'N/A')} ({exo['duree']} min)"
            ):
                st.write(f"**Type :** {exo.get('type', 'N/A')}")
                st.write(f"**Espace / Matériel :** {exo['espace']}")
                st.write(f"**Consignes :** {exo['consignes']}")

# --- ONGLET 3 : AJOUTER UN EXERCICE ---
with tab3:
    st.header("Nouveau contenu")

    with st.form("form_add_exo", clear_on_submit=True):
        titre = st.text_input("Nom de l'exercice")
        col1, col2 = st.columns(2)
        with col1:
            groupe = st.selectbox("Groupe", CATEGORIES_GROUPE)
        with col2:
            type_exo = st.selectbox("Type", TYPES_EXERCICE)

        duree = st.number_input(
            "Durée (minutes)", min_value=5, max_value=60, value=15
        )
        espace = st.text_input("Terrain / Matériel requis")
        consignes = st.text_area("Consignes & règles")

        submitted = st.form_submit_button("💾 Enregistrer dans la banque")

        if submitted and titre:
            new_exo = {
                "titre": titre,
                "groupe": groupe,
                "type": type_exo,
                "duree": duree,
                "espace": espace,
                "consignes": consignes,
            }
            save_exercice(new_exo)
            st.success(f"Exercice '{titre}' enregistré !")
