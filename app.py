import json
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Rugby Coach - Séances & Ateliers", page_icon="🏉", layout="wide"
)

DB_FILE = "exercices_rugby.json"


# Fonctions de gestion des données
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


st.title("🏉 Rugby Coach App — Gestionnaire de Séances")

tab1, tab2, tab3 = st.tabs(
    ["📋 Créer une Séance", "📚 Banque d'Exercices", "➕ Ajouter un Exercice"]
)

# --- ONGLET 1 : CRÉER UNE SÉANCE ---
with tab1:
    st.header("Composition de la séance du jour")
    data = load_data()

    if not data:
        st.info(
            "La banque d'exercices est vide. Rendez-vous dans l'onglet 'Ajouter un Exercice' !"
        )
    else:
        titre_seance = st.text_input(
            "Titre / Thème de la séance", "Séance Séparée & Collectif"
        )

        exos_avants = [e["titre"] for e in data if e["categorie"] == "Avants"]
        exos_arrieres = [e["titre"] for e in data if e["categorie"] == "Arrières"]
        exos_collectif = [
            e["titre"] for e in data if e["categorie"] == "Collectif"
        ]

        st.subheader("1. Ateliers Séparés (Simultanés)")
        st.caption(
            "Les groupes Avants et Arrières travaillent en parallèle pendant le même créneau."
        )

        col_av, col_arr = st.columns(2)
        with col_av:
            sel_avant = st.selectbox(
                "Exercice Avants", ["Aucun"] + exos_avants, key="sel_av"
            )
        with col_arr:
            sel_arriere = st.selectbox(
                "Exercice Arrières", ["Aucun"] + exos_arrieres, key="sel_arr"
            )

        duree_ateliers = st.number_input(
            "Durée du bloc d'ateliers séparés (min)",
            min_value=0,
            max_value=60,
            value=20,
        )

        st.subheader("2. Séquence Collectives (Tout le groupe)")
        sel_collectifs = st.multiselect(
            "Sélectionnez les exercices collectifs :", exos_collectif
        )

        # Affichage du recap de la séance
        st.markdown("---")
        st.subheader("📄 Déroulé de la séance")

        total_duration = 0

        # Bloc Ateliers
        if sel_avant != "Aucun" or sel_arriere != "Aucun":
            st.markdown(
                f"### ⏱️ Bloc Ateliers Séparés — **{duree_ateliers} min**"
            )
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🐗 Groupe Avants")
                if sel_avant != "Aucun":
                    exo = next(e for e in data if e["titre"] == sel_avant)
                    st.write(f"**{exo['titre']}**")
                    st.caption(exo["consignes"])
                else:
                    st.info("Pas d'exercice spécifique")

            with c2:
                st.markdown("#### ⚡ Groupe Arrières")
                if sel_arriere != "Aucun":
                    exo = next(e for e in data if e["titre"] == sel_arriere)
                    st.write(f"**{exo['titre']}**")
                    st.caption(exo["consignes"])
                else:
                    st.info("Pas d'exercice spécifique")

            total_duration += duree_ateliers

        # Bloc Collectif
        if sel_collectifs:
            st.markdown("### 🤝 Séquence Collective")
            for idx, title in enumerate(sel_collectifs):
                exo = next(e for e in data if e["titre"] == title)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{idx+1}. {exo['titre']}**")
                    st.caption(exo["consignes"])
                with col_b:
                    dur = st.number_input(
                        "Durée (min)",
                        value=int(exo["duree"]),
                        key=f"dur_coll_{idx}",
                    )
                    total_duration += dur

        st.metric("Durée Totale de la Séance", f"{total_duration} min")

# --- ONGLET 2 : BANQUE D'EXERCICES ---
with tab2:
    st.header("Banque d'Exercices par Catégorie")
    data = load_data()

    if data:
        cat_filter = st.radio(
            "Filtrer par :",
            ["Tous", "Avants", "Arrières", "Collectif"],
            horizontal=True,
        )
        filtered_data = (
            data
            if cat_filter == "Tous"
            else [e for e in data if e["categorie"] == cat_filter]
        )

        for exo in filtered_data:
            badge = (
                "🐗"
                if exo["categorie"] == "Avants"
                else ("⚡" if exo["categorie"] == "Arrières" else "🤝")
            )
            with st.expander(
                f"{badge} {exo['titre']} ({exo['categorie']}) — {exo['duree']} min"
            ):
                st.write(f"**Espace / Matériel :** {exo['espace']}")
                st.write(f"**Consignes :** {exo['consignes']}")

# --- ONGLET 3 : AJOUTER UN EXERCICE ---
with tab3:
    st.header("Ajouter un nouvel exercice")

    with st.form("form_add_exo", clear_on_submit=True):
        titre = st.text_input("Titre de l'exercice")
        categorie = st.selectbox(
            "Catégorie",
            [
                "Avants",
                "Arrières",
                "Collectif",
            ],  # Strictement limité aux 3 catégories
        )
        duree = st.number_input(
            "Durée conseillée (minutes)", min_value=5, max_value=60, value=15
        )
        espace = st.text_input("Espace requis (ex: 20x15m, 10 plots, boudins)")
        consignes = st.text_area("Consignes et règles du jeu")

        submitted = st.form_submit_button("💾 Enregistrer l'exercice")

        if submitted and titre:
            new_exo = {
                "titre": titre,
                "categorie": categorie,
                "duree": duree,
                "espace": espace,
                "consignes": consignes,
            }
            save_exercice(new_exo)
            st.success(
                f"Exercice '{titre}' ajouté avec succès dans la catégorie {categorie} !"
            )
