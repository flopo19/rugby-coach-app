import json
import os
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Rugby Coach App",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_FILE = "exercices_rugby.json"
CONFIG_FILE = "config_app.json"
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

# --- CHARGEMENT / SAUVEGARDE DE LA CONFIGURATION ---
DEFAULT_CONFIG = {
    "nom_equipe": "MON ÉQUIPE DE RUGBY",
    "bg_color_1": "#132a13",
    "bg_color_2": "#31572c",
    "bg_color_3": "#4f772d",
    "btn_color": "#4f772d",
    "btn_text_color": "#ffffff",
    "logo_path": None,
}


def load_config():
  if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
      cfg = json.load(f)
      for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
      return cfg
  return DEFAULT_CONFIG.copy()


def save_config(config):
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=4)


# Navigation via la session state
if "page" not in st.session_state:
  st.session_state.page = "home"

config = load_config()

# --- APPLIQUE LES STYLES DYNAMIQUES SELON LES PARAMÈTRES ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, {config['bg_color_1']} 0%, {config['bg_color_2']} 50%, {config['bg_color_3']} 100%);
        color: #ecf39e;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}

    .main-header {{
        text-align: center;
        padding: 20px 0 10px 0;
    }}
    .main-title {{
        color: #ecf39e;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
    }}
    .sub-title {{
        color: #90a955;
        font-size: 1rem;
        font-weight: 500;
        margin-top: 5px;
    }}

    /* Styles des boutons de l'application */
    .stButton>button {{
        width: 100%;
        background-color: {config['btn_color']} !important;
        color: {config['btn_text_color']} !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        margin-bottom: 8px !important;
    }}

    /* Cartes des exercices */
    .exo-card {{
        background: rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        border-left: 6px solid #90a955;
        backdrop-filter: blur(5px);
    }}
    .exo-card-avants {{ border-left-color: #e76f51; }}
    .exo-card-arrieres {{ border-left-color: #2a9d8f; }}
    .exo-card-collectif {{ border-left-color: #e9c46a; }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""",
    unsafe_allow_html=True,
)


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


# --- EN-TÊTE DE L'ÉQUIPE ---
st.markdown(
    f"""
    <div class="main-header">
        <h1 class="main-title">🏉 {config['nom_equipe']}</h1>
        <p class="sub-title">Rugby Coach App — Gestionnaire de Séances</p>
    </div>
""",
    unsafe_allow_html=True,
)

if config.get("logo_path") and os.path.exists(config["logo_path"]):
  col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
  with col_l2:
    st.image(config["logo_path"], use_container_width=True)

# -----------------------------------------------------------------------------
# 1. PAGE D'ACCUEIL : LES BOUTONS EMPILÉS
# -----------------------------------------------------------------------------
if st.session_state.page == "home":
  st.write("")
  col_a, col_b, col_c = st.columns([1, 2, 1])

  with col_b:
    if st.button("📋 Créer une Séance", key="btn_seance"):
      st.session_state.page = "seance"
      st.rerun()

    if st.button("📚 Banque d'Exercices", key="btn_banque"):
      st.session_state.page = "banque"
      st.rerun()

    if st.button("➕ Ajouter un Exercice", key="btn_ajouter"):
      st.session_state.page = "ajouter"
      st.rerun()

    st.markdown(
        "<br><hr style='border-color: rgba(255,255,255,0.2);'><br>",
        unsafe_allow_html=True,
    )

    if st.button("⚙️ Paramètres", key="btn_params"):
      st.session_state.page = "parametres"
      st.rerun()

# BOUTON RETOUR (sur toutes les sous-pages)
if st.session_state.page != "home":
  if st.button("⬅️ Retour à l'accueil"):
    st.session_state.page = "home"
    st.rerun()
  st.markdown("---")

# -----------------------------------------------------------------------------
# 2. PAGE : CRÉER UNE SÉANCE
# -----------------------------------------------------------------------------
if st.session_state.page == "seance":
  st.header("📋 Créer une Séance")
  data = load_data()

  if not data:
    st.info(
        "La banque d'exercices est vide. Ajoutez un premier exercice depuis"
        " l'accueil !"
    )
  else:
    titre_seance = st.text_input(
        "Intitulé / Thème de la séance", "Séance de terrain"
    )

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
        "Durée du bloc ateliers (min)", min_value=0, max_value=60, value=20
    )

    st.subheader("2. Séquences Collectives")
    sel_collectifs = st.multiselect(
        "🤝 Exercices Collectifs (Tout le groupe) :", exos_collectif
    )

    st.markdown("---")
    st.markdown("### 📄 Déroulé de la séance")

    total_duration = 0

    if sel_avant != "Aucun" or sel_arriere != "Aucun":
      st.markdown(f"#### ⏱️ Ateliers Séparés — **{duree_ateliers} min**")
      c1, c2 = st.columns(2)
      with c1:
        if sel_avant != "Aucun":
          titre_clean = sel_avant.split(" [")[0]
          exo = next(e for e in data if e["titre"] == titre_clean)
          st.markdown(
              f"""
            <div class='exo-card exo-card-avants'>
                <strong style='color:#e76f51;'>🐗 Avants : {exo['titre']}</strong><br>
                <small>{exo['type']} | Espace/Matériel : {exo['espace']}</small><br><br>
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
                <strong style='color:#2a9d8f;'>⚡ Arrières : {exo['titre']}</strong><br>
                <small>{exo['type']} | Espace/Matériel : {exo['espace']}</small><br><br>
                {exo['consignes']}
            </div>
            """,
              unsafe_allow_html=True,
          )
      total_duration += duree_ateliers

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
                <strong style='color:#e9c46a;'>{idx+1}. {exo['titre']}</strong> ({exo['type']})<br>
                <small>Espace/Matériel : {exo['espace']}</small><br><br>
                {exo['consignes']}
            </div>
            """,
              unsafe_allow_html=True,
          )
        with col_b:
          dur = st.number_input(
              "Durée (min)", value=int(exo["duree"]), key=f"dur_coll_{idx}"
          )
          total_duration += dur

    st.metric("Durée Totale Estimée", f"{total_duration} min")

# -----------------------------------------------------------------------------
# 3. PAGE : BANQUE D'EXERCICES
# -----------------------------------------------------------------------------
elif st.session_state.page == "banque":
  st.header("📚 Banque d'Exercices")
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
          f"{badge} {exo['titre']} — {exo.get('groupe', 'N/A')} ({exo['duree']}"
          " min)"
      ):
        st.write(f"**Type :** {exo.get('type', 'N/A')}")
        st.write(f"**Espace / Matériel :** {exo['espace']}")
        st.write(f"**Consignes :** {exo['consignes']}")

# -----------------------------------------------------------------------------
# 4. PAGE : AJOUTER UN EXERCICE
# -----------------------------------------------------------------------------
elif st.session_state.page == "ajouter":
  st.header("➕ Ajouter un nouvel exercice")

  with st.form("form_add_exo", clear_on_submit=True):
    titre = st.text_input("Nom de l'exercice")
    col1, col2 = st.columns(2)
    with col1:
      groupe = st.selectbox("Groupe", CATEGORIES_GROUPE)
    with col2:
      type_exo = st.selectbox("Type d'exercice", TYPES_EXERCICE)

    duree = st.number_input(
        "Durée conseillée (minutes)", min_value=5, max_value=60, value=15
    )
    espace = st.text_input("Terrain / Matériel requis")
    consignes = st.text_area("Consignes & Règles du jeu")

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
      st.success(f"L'exercice '{titre}' a été ajouté à la banque !")

# -----------------------------------------------------------------------------
# 5. PAGE : PARAMÈTRES ET PERSONNALISATION
# -----------------------------------------------------------------------------
elif st.session_state.page == "parametres":
  st.header("⚙️ Paramètres & Personnalisation")

  with st.form("form_config"):
    nom_equipe = st.text_input(
        "Nom de l'équipe / du club", value=config["nom_equipe"]
    )

    st.subheader("🎨 Couleurs de l'application")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
      bg1 = st.color_picker(
          "Couleur de fond (Haut)", value=config["bg_color_1"]
      )
      bg2 = st.color_picker(
          "Couleur de fond (Milieu)", value=config["bg_color_2"]
      )
      bg3 = st.color_picker(
          "Couleur de fond (Bas)", value=config["bg_color_3"]
      )
    with col_c2:
      btn_col = st.color_picker(
          "Couleur des boutons", value=config["btn_color"]
      )
      btn_txt = st.color_picker(
          "Couleur du texte des boutons", value=config["btn_text_color"]
      )

    st.subheader("🖼️ Logo du club")
    uploaded_logo = st.file_uploader(
        "Importer une image de logo (PNG, JPG)", type=["png", "jpg", "jpeg"]
    )

    save_btn = st.form_submit_button("💾 Enregistrer les modifications")

    if save_btn:
      config["nom_equipe"] = nom_equipe
      config["bg_color_1"] = bg1
      config["bg_color_2"] = bg2
      config["bg_color_3"] = bg3
      config["btn_color"] = btn_col
      config["btn_text_color"] = btn_txt

      if uploaded_logo is not None:
        logo_filename = f"logo_custom.{uploaded_logo.name.split('.')[-1]}"
        with open(logo_filename, "wb") as f:
          f.write(uploaded_logo.getbuffer())
        config["logo_path"] = logo_filename

      save_config(config)
      st.success("Paramètres enregistrés avec succès !")
      st.rerun()
