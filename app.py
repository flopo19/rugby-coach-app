import base64
import json
import os
import streamlit as st

# Configuration de la page Streamlit
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
    "nom_equipe": "MON ÉQUIPE DE RUGBY",
    "bg_color": "#121212",
    "card_bg": "#1e1e1e",
    "btn_color": "#2e7d32",
    "btn_text_color": "#ffffff",
    "text_color": "#e0e0e0",
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

# --- CSS ÉPURÉ, RESPONSIVE & HAUT CONTRASTE ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {config['bg_color']};
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .block-container {{
        max-width: 650px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}

    label, .stWidgetLabel, div[data-testid="stMarkdownContainer"] p {{
        color: #f0f0f0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    
    .stFileUploader small, div[data-testid="stUploadDropzone"] span {{
        color: #d0d0d0 !important;
    }}

    .main-header {{
        text-align: center;
        margin-bottom: 25px;
    }}
    .main-title {{
        color: #ffffff !important;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 0;
    }}
    .sub-title {{
        color: #cccccc !important;
        font-size: 0.95rem;
        margin-top: 5px;
    }}

    .stButton>button {{
        width: 100% !important;
        background-color: {config['btn_color']} !important;
        color: {config['btn_text_color']} !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 14px 20px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        margin-bottom: 10px !important;
        transition: transform 0.1s ease;
    }}
    .stButton>button:hover {{
        filter: brightness(1.1);
    }}

    .exo-card {{
        background-color: {config['card_bg']};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 5px solid #2e7d32;
    }}
    .exo-card-avants {{ border-left-color: #d32f2f; }}
    .exo-card-arrieres {{ border-left-color: #0288d1; }}
    .exo-card-collectif {{ border-left-color: #f57c00; }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""",
    unsafe_allow_html=True,
)

# --- EN-TÊTE CENTRÉ ---
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
  st.image(config["logo_path"], width=120)

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
      "<hr style='border: none; border-top: 1px solid #333; margin: 20px"
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
  st.markdown("---")

# -----------------------------------------------------------------------------
# 2. CRÉER UNE SÉANCE
# -----------------------------------------------------------------------------
if st.session_state.page == "seance":
  st.header("📋 Créer une Séance")
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

    st.subheader("1. Ateliers Séparés")
    sel_avant = st.selectbox(
        "🐗 Groupe Avants", ["Aucun"] + exos_avants, key="sel_av"
    )
    sel_arriere = st.selectbox(
        "⚡ Groupe Arrières", ["Aucun"] + exos_arrieres, key="sel_arr"
    )
    duree_ateliers = st.number_input(
        "Durée du bloc ateliers (min)", min_value=0, max_value=60, value=20
    )

    st.subheader("2. Séquences Collectives")
    sel_collectifs = st.multiselect(
        "🤝 Exercices Collectifs :", exos_collectif
    )

    st.markdown("---")
    st.markdown("### 📄 Déroulé de la séance")
    total_duration = 0

    if sel_avant != "Aucun" or sel_arriere != "Aucun":
      st.markdown(f"#### ⏱️ Ateliers Séparés — **{duree_ateliers} min**")

      if sel_avant != "Aucun":
        titre_clean = sel_avant.split(" [")[0]
        exo = next(e for e in data if e["titre"] == titre_clean)
        st.markdown(
            f"""
            <div class='exo-card exo-card-avants'>
                <strong style='color:#ef5350;'>🐗 Avants : {exo['titre']}</strong><br>
                <small>{exo['type']} | Espace : {exo['espace']}</small><br><br>
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
            <div class='exo-card exo-card-arrieres'>
                <strong style='color:#29b6f6;'>⚡ Arrières : {exo['titre']}</strong><br>
                <small>{exo['type']} | Espace : {exo['espace']}</small><br><br>
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
      st.markdown("#### 🤝 Séquences Collectives")
      for idx, item in enumerate(sel_collectifs):
        titre_clean = item.split(" [")[0]
        exo = next(e for e in data if e["titre"] == titre_clean)
        st.markdown(
            f"""
            <div class='exo-card exo-card-collectif'>
                <strong style='color:#ffa726;'>{idx+1}. {exo['titre']}</strong> ({exo['type']})<br>
                <small>Espace : {exo['espace']}</small><br><br>
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
# 3. BANQUE D'EXERCICES (AVEC ÉDITION & SUPPRESSION)
# -----------------------------------------------------------------------------
elif st.session_state.page == "banque":
  st.header("📚 Banque d'Exercices")
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

        if exo.get("image_path") and os.path.exists(exo["image_path"]):
          st.image(
              exo["image_path"],
              caption=f"Schéma de {exo['titre']}",
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
            # Suppression de l'image si présente
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
    st.header("✏️ Modifier l'exercice")
    exo_to_edit = data[st.session_state.edit_exo_idx]
  else:
    st.header("➕ Ajouter un exercice")
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
        "Nouveau schéma ou image (optionnel)", type=["png", "jpg", "jpeg"]
    )

    submitted = st.form_submit_button(
        "💾 Mettre à jour" if is_editing else "💾 Enregistrer"
    )

    if submitted and titre:
      image_path = exo_to_edit.get("image_path")

      if uploaded_file is not None:
        # Suppression de l'ancienne image le cas échéant
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
        st.success(f"L'exercice '{titre}' a été mis à jour !")
      else:
        data.append(updated_exo)
        st.success(f"L'exercice '{titre}' a été ajouté !")

      save_all_data(data)
      st.session_state.page = "banque"
      st.rerun()

# -----------------------------------------------------------------------------
# 5. PARAMÈTRES
# -----------------------------------------------------------------------------
elif st.session_state.page == "parametres":
  st.header("⚙️ Paramètres")

  with st.form("form_config"):
    nom_equipe = st.text_input(
        "Nom de l'équipe / du club", value=config["nom_equipe"]
    )

    st.subheader("🎨 Couleurs")
    bg_color = st.color_picker("Couleur de fond", value=config["bg_color"])
    card_bg = st.color_picker(
        "Couleur de fond des cartes", value=config["card_bg"]
    )
    btn_col = st.color_picker("Couleur des boutons", value=config["btn_color"])
    btn_txt = st.color_picker(
        "Couleur du texte des boutons", value=config["btn_text_color"]
    )

    st.subheader("🖼️ Logo du club")
    uploaded_logo = st.file_uploader(
        "Importer un logo", type=["png", "jpg", "jpeg"]
    )

    save_btn = st.form_submit_button("💾 Enregistrer")

    if save_btn:
      config["nom_equipe"] = nom_equipe
      config["bg_color"] = bg_color
      config["card_bg"] = card_bg
      config["btn_color"] = btn_col
      config["btn_text_color"] = btn_txt

      if uploaded_logo is not None:
        logo_filename = f"logo_custom.{uploaded_logo.name.split('.')[-1]}"
        with open(logo_filename, "wb") as f:
          f.write(uploaded_logo.getbuffer())
        config["logo_path"] = logo_filename

      save_config(config)
      st.success("Paramètres mis à jour !")
      st.rerun()
