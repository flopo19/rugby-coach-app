import json
import os
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Rugby Coach App",
    page_icon="🏉",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_FILE = "exercices_rugby.json"
CONFIG_FILE = "config_app.json"
IMAGE_DIR = "exercise_images"

if not os.path.exists(IMAGE_DIR):
  os.makedirs(IMAGE_DIR)

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

DEFAULT_CONFIG = {
    "nom_equipe": "STADE LÉONIEN",
    "bg_color": "#000000",
    "card_bg": "#121212",
    "btn_color": "#222222",
    "btn_text_color": "#ffffff",
    "text_color": "#ffffff",
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


def load_data():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


def save_all_data(data):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


if "page" not in st.session_state:
  st.session_state.page = "home"

if "edit_exo_idx" not in st.session_state:
  st.session_state.edit_exo_idx = None

config = load_config()

# --- DESIGN NOIR & BLANC ultra-lisible ---
st.markdown(
    """
    <style>
    /* Fond noir et texte blanc par défaut */
    .stApp {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        max-width: 650px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* Labels, titres et textes ultra lisibles */
    label, .stWidgetLabel, p, h1, h2, h3, h4, span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Input fields clairs sur fond noir */
    input, textarea, select, div[data-baseweb="select"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
    }

    /* En-tête minimaliste */
    .main-header {
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 1px solid #333333;
        margin-bottom: 20px;
    }
    .main-title {
        color: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 0;
    }
    .sub-title {
        color: #888888 !important;
        font-size: 0.85rem;
        margin-top: 4px;
        font-weight: 400 !important;
    }

    /* Boutons sobres */
    .stButton>button {
        width: 100% !important;
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        border: 1px solid #333333 !important;
        margin-bottom: 8px !important;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
    }

    /* Cartes exercices sobres */
    .exo-card {
        background-color: #141414;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }

    /* Zone dropzone upload d'images */
    div[data-testid="stUploadDropzone"] {
        background-color: #1a1a1a !important;
        border: 1px dashed #555555 !important;
    }
    div[data-testid="stUploadDropzone"] span {
        color: #cccccc !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- EN-TÊTE SOBRE ---
st.markdown(
    f"""
    <div class="main-header">
        <h1 class="main-title">🏉 {config['nom_equipe']}</h1>
        <p class="sub-title">Gestionnaire de Séances & Banque d'Exercices</p>
    </div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 1. ACCUEIL
# -----------------------------------------------------------------------------
if st.session_state.page == "home":
  st.write("")
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
      "<hr style='border: none; border-top: 1px solid #222; margin: 20px"
      " 0;'>",
      unsafe_allow_html=True,
  )

  if st.button("⚙️ Paramètres", key="btn_params"):
    st.session_state.page = "parametres"
    st.rerun()

if st.session_state.page != "home":
  if st.button("⬅️ Retour à l'accueil"):
    st.session_state.page = "home"
    st.session_state.edit_exo_idx = None
    st.rerun()
  st.markdown(
      "<hr style='border: none; border-top: 1px solid #222; margin: 15px"
      " 0;'>",
      unsafe_allow_html=True,
  )

# -----------------------------------------------------------------------------
# 2. CRÉER UNE SÉANCE
# -----------------------------------------------------------------------------
if st.session_state.page == "seance":
  st.subheader("📋 Créer une Séance")
  data = load_data()

  if not data:
    st.info("La banque d'exercices est vide. Ajoutez un exercice d'abord.")
  else:
    titre_seance = st.text_input("Thème de la séance", "Séance du jour")

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

    st.markdown("### 1. Ateliers Séparés")
    sel_avant = st.selectbox(
        "Groupe Avants", ["Aucun"] + exos_avants, key="sel_av"
    )
    sel_arriere = st.selectbox(
        "Groupe Arrières", ["Aucun"] + exos_arrieres, key="sel_arr"
    )
    duree_ateliers = st.number_input(
        "Durée ateliers (min)", min_value=0, max_value=60, value=20
    )

    st.markdown("### 2. Séquences Collectives")
    sel_collectifs = st.multiselect(
        "Exercices Collectifs :", exos_collectif
    )

    st.markdown(
        "<hr style='border: none; border-top: 1px solid #333; margin: 20px"
        " 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown("### 📄 Déroulé de la séance")
    total_duration = 0

    if sel_avant != "Aucun" or sel_arriere != "Aucun":
      st.markdown(f"**⏱️ Ateliers Séparés ({duree_ateliers} min)**")

      if sel_avant != "Aucun":
        titre_clean = sel_avant.split(" [")[0]
        exo = next(e for e in data if e["titre"] == titre_clean)
        st.markdown(
            f"""
            <div class='exo-card'>
                <strong style='color:#ffffff;'>🐗 Avants : {exo['titre']}</strong><br>
                <span style='color:#aaaaaa;'>{exo['type']} | Espace : {exo['espace']}</span><br><br>
                {exo['consignes']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if exo.get("image_path") and os.path.exists(exo["image_path"]):
          st.image(
              exo["image_path"],
              caption=f"Schéma : {exo['titre']}",
              use_container_width=True,
          )

      if sel_arriere != "Aucun":
        titre_clean = sel_arriere.split(" [")[0]
        exo = next(e for e in data if e["titre"] == titre_clean)
        st.markdown(
            f"""
            <div class='exo-card'>
                <strong style='color:#ffffff;'>⚡ Arrières : {exo['titre']}</strong><br>
                <span style='color:#aaaaaa;'>{exo['type']} | Espace : {exo['espace']}</span><br><br>
                {exo['consignes']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if exo.get("image_path") and os.path.exists(exo["image_path"]):
          st.image(
              exo["image_path"],
              caption=f"Schéma : {exo['titre']}",
              use_container_width=True,
          )

      total_duration += duree_ateliers

    if sel_collectifs:
      st.markdown("**🤝 Séquences Collectives**")
      for idx, item in enumerate(sel_collectifs):
        titre_clean = item.split(" [")[0]
        exo = next(e for e in data if e["titre"] == titre_clean)
        st.markdown(
            f"""
            <div class='exo-card'>
                <strong style='color:#ffffff;'>{idx+1}. {exo['titre']}</strong> ({exo['type']})<br>
                <span style='color:#aaaaaa;'>Espace : {exo['espace']}</span><br><br>
                {exo['consignes']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if exo.get("image_path") and os.path.exists(exo["image_path"]):
          st.image(
              exo["image_path"],
              caption=f"Schéma : {exo['titre']}",
              use_container_width=True,
          )

        dur = st.number_input(
            f"Durée {exo['titre']} (min)",
            value=int(exo["duree"]),
            key=f"dur_coll_{idx}",
        )
        total_duration += dur

    st.metric("Durée Totale Estimée", f"{total_duration} min")

# -----------------------------------------------------------------------------
# 3. BANQUE D'EXERCICES
# -----------------------------------------------------------------------------
elif st.session_state.page == "banque":
  st.subheader("📚 Banque d'Exercices")
  data = load_data()

  if data:
    grp_filter = st.selectbox(
        "Filtrer par Groupe :", ["Tous"] + CATEGORIES_GROUPE
    )
    type_filter = st.selectbox("Filtrer par Type :", ["Tous"] + TYPES_EXERCICE)

    for real_idx, exo in enumerate(data):
      if grp_filter != "Tous" and exo.get("groupe") != grp_filter:
        continue
      if type_filter != "Tous" and exo.get("type") != type_filter:
        continue

      with st.expander(
          f"{exo['titre']} — {exo.get('groupe', 'N/A')} ({exo['duree']} min)"
      ):
        st.write(f"**Type :** {exo.get('type', 'N/A')}")
        st.write(f"**Espace / Matériel :** {exo['espace']}")
        st.write(f"**Consignes :** {exo['consignes']}")

        if exo.get("image_path") and os.path.exists(exo["image_path"]):
          st.image(
              exo["image_path"],
              caption=f"Schéma : {exo['titre']}",
              use_container_width=True,
          )

        col1, col2 = st.columns(2)
        with col1:
          if st.button("✏️ Modifier", key=f"edit_{real_idx}"):
            st.session_state.edit_exo_idx = real_idx
            st.session_state.page = "ajouter"
            st.rerun()

        with col2:
          if st.button("🗑️ Supprimer", key=f"del_{real_idx}"):
            if exo.get("image_path") and os.path.exists(exo["image_path"]):
              try:
                os.remove(exo["image_path"])
              except OSError:
                pass

            data.pop(real_idx)
            save_all_data(data)
            st.success(f"Exercice '{exo['titre']}' supprimé !")
            st.rerun()
  else:
    st.info("Aucun exercice enregistré pour le moment.")

# -----------------------------------------------------------------------------
# 4. AJOUTER / MODIFIER UN EXERCICE
# -----------------------------------------------------------------------------
elif st.session_state.page == "ajouter":
  data = load_data()
  is_editing = st.session_state.edit_exo_idx is not None

  if is_editing:
    st.subheader("✏️ Modifier l'exercice")
    exo_to_edit = data[st.session_state.edit_exo_idx]
  else:
    st.subheader("➕ Ajouter un exercice")
    exo_to_edit = {
        "titre": "",
        "groupe": CATEGORIES_GROUPE[0],
        "type": TYPES_EXERCICE[0],
        "duree": 15,
        "espace": "",
        "consignes": "",
        "image_path": None,
    }

  with st.form("form_add_exo", clear_on_submit=False):
    titre = st.text_input("Nom de l'exercice", value=exo_to_edit["titre"])

    idx_grp = (
        CATEGORIES_GROUPE.index(exo_to_edit["groupe"])
        if exo_to_edit["groupe"] in CATEGORIES_GROUPE
        else 0
    )
    groupe = st.selectbox("Groupe", CATEGORIES_GROUPE, index=idx_grp)

    idx_type = (
        TYPES_EXERCICE.index(exo_to_edit["type"])
        if exo_to_edit["type"] in TYPES_EXERCICE
        else 0
    )
    type_exo = st.selectbox("Type d'exercice", TYPES_EXERCICE, index=idx_type)

    duree = st.number_input(
        "Durée conseillée (minutes)",
        min_value=5,
        max_value=60,
        value=int(exo_to_edit["duree"]),
    )
    espace = st.text_input(
        "Terrain / Matériel requis", value=exo_to_edit["espace"]
    )
    consignes = st.text_area(
        "Consignes & Règles du jeu", value=exo_to_edit["consignes"]
    )

    uploaded_file = st.file_uploader(
        "Schéma ou image (optionnel)", type=["png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button(
        "💾 Mettre à jour" if is_editing else "💾 Enregistrer"
    )

    if submitted and titre:
      image_path = exo_to_edit.get("image_path")

      if uploaded_file is not None:
        if image_path and os.path.exists(image_path):
          try:
            os.remove(image_path)
          except OSError:
            pass

        filename = (
            f"{titre.lower().replace(' ', '_')}_{uploaded_file.name[-8:]}"
        )
        image_path = os.path.join(IMAGE_DIR, filename)
        with open(image_path, "wb") as f:
          f.write(uploaded_file.getbuffer())

      updated_exo = {
          "titre": titre,
          "groupe": groupe,
          "type": type_exo,
          "duree": duree,
          "espace": espace,
          "consignes": consignes,
          "image_path": image_path,
      }

      if is_editing:
        data[st.session_state.edit_exo_idx] = updated_exo
        st.session_state.edit_exo_idx = None
        st.success(f"Exercice '{titre}' mis à jour !")
      else:
        data.append(updated_exo)
        st.success(f"Exercice '{titre}' ajouté !")

      save_all_data(data)
      st.session_state.page = "banque"
      st.rerun()

# -----------------------------------------------------------------------------
# 5. PARAMÈTRES
# -----------------------------------------------------------------------------
elif st.session_state.page == "parametres":
  st.subheader("⚙️ Paramètres")

  with st.form("form_config"):
    nom_equipe = st.text_input(
        "Nom du club / de l'équipe", value=config["nom_equipe"]
    )
    save_btn = st.form_submit_button("💾 Enregistrer")

    if save_btn:
      config["nom_equipe"] = nom_equipe
      save_config(config)
      st.success("Paramètres mis à jour !")
      st.rerun()
