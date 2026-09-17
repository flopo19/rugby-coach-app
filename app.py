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

CATEGORIES_GROUPE = [
    "Avants",
    "Arrières",
    "Collectif",
    "Avants & Arrières (Séparés)",
]
TYPES_EXERCICE = ["Échauffement", "Exercices", "Opposition"]

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

if "seance_blocks" not in st.session_state:
  st.session_state.seance_blocks = []

config = load_config()

# --- STYLES CSS SOBRES ET LISIBLES ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        max-width: 680px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    label, .stWidgetLabel, p, h1, h2, h3, h4, span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    input, textarea, select, div[data-baseweb="select"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
    }

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

    .stButton>button {
        width: 100% !important;
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        border-radius: 6px !important;
        border: 1px solid #444444 !important;
        margin-bottom: 8px !important;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
    }

    /* Style spécifique pour le bouton de soumission de formulaire */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        border: 1px solid #ffffff !important;
        padding: 12px 16px !important;
        margin-top: 10px !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #cccccc !important;
        color: #000000 !important;
    }

    .exo-card {
        background-color: #141414;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }

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

# En-tête
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
# NAVIGATION ACCUEIL / RETOUR
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
    st.session_state.edit_exo_idx = None
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
# 1. BANQUE D'EXERCICES
# -----------------------------------------------------------------------------
if st.session_state.page == "banque":
  col_title, col_add = st.columns([2, 1])
  with col_title:
    st.subheader("📚 Banque d'Exercices")
  with col_add:
    if st.button("➕ Cet exercice", key="btn_add_from_bank"):
      st.session_state.edit_exo_idx = None
      st.session_state.page = "ajouter"
      st.rerun()

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

        c1, c2 = st.columns(2)
        with c1:
          if st.button("✏️ Modifier", key=f"edit_{real_idx}"):
            st.session_state.edit_exo_idx = real_idx
            st.session_state.page = "ajouter"
            st.rerun()
        with c2:
          if st.button("🗑️ Supprimer", key=f"del_{real_idx}"):
            if exo.get("image_path") and os.path.exists(exo["image_path"]):
              try:
                os.remove(exo["image_path"])
              except OSError:
                pass
            data.pop(real_idx)
            save_all_data(data)
            st.success("Exercice supprimé !")
            st.rerun()
  else:
    st.info("Aucun exercice enregistré pour le moment.")

# -----------------------------------------------------------------------------
# 2. CRÉER / MODIFIER UN EXERCICE
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

    btn_label = (
        "💾 Mettre à jour l'exercice"
        if is_editing
        else "💾 Enregistrer l'exercice"
    )
    submitted = st.form_submit_button(btn_label)

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
        st.success(f"Exercice '{titre}' enregistré !")

      save_all_data(data)
      st.session_state.page = "banque"
      st.rerun()

# -----------------------------------------------------------------------------
# 3. CRÉATION DE SÉANCE SÉQUENTIELLE & LIBRE
# -----------------------------------------------------------------------------
elif st.session_state.page == "seance":
  st.subheader("📋 Créer une Séance Libre")
  data = load_data()

  if not data:
    st.info("La banque d'exercices est vide. Ajoutez d'abord des exercices.")
  else:
    titre_seance = st.text_input("Thème de la séance", "Séance du jour")

    titles_list = [f"{e['titre']} [{e['type']}]" for e in data]

    st.markdown("### 1. Construction de la séquence")

    # Bouton pour ajouter un bloc dans la séance
    if st.button("➕ Ajouter une étape / un atelier"):
      st.session_state.seance_blocks.append({
          "exo_title": titles_list[0],
          "duree": 15,
          "groupe_custom": "Tout le groupe",
      })
      st.rerun()

    # Gestion des blocs de la séance
    blocks_to_remove = []
    for idx, block in enumerate(st.session_state.seance_blocks):
      st.markdown(f"--- **Étape {idx+1}** ---")
      c_exo, c_grp, c_dur = st.columns([3, 2, 2])

      with c_exo:
        sel_idx = (
            titles_list.index(block["exo_title"])
            if block["exo_title"] in titles_list
            else 0
        )
        block["exo_title"] = st.selectbox(
            f"Exercice", titles_list, index=sel_idx, key=f"blk_exo_{idx}"
        )

      with c_grp:
        block["groupe_custom"] = st.text_input(
            "Groupe concerné",
            value=block.get("groupe_custom", "Tout le groupe"),
            key=f"blk_grp_{idx}",
        )

      with c_dur:
        block["duree"] = st.number_input(
            "Durée (min)",
            min_value=1,
            max_value=90,
            value=int(block["duree"]),
            key=f"blk_dur_{idx}",
        )

      col_up, col_down, col_del = st.columns(3)
      with col_up:
        if idx > 0 and st.button("⬆️ Monter", key=f"up_{idx}"):
          st.session_state.seance_blocks[idx], (
              st.session_state.seance_blocks[idx - 1]
          ) = (
              st.session_state.seance_blocks[idx - 1],
              st.session_state.seance_blocks[idx],
          )
          st.rerun()

      with col_down:
        if (
            idx < len(st.session_state.seance_blocks) - 1
            and st.button("⬇️ Descendre", key=f"down_{idx}")
        ):
          st.session_state.seance_blocks[idx], (
              st.session_state.seance_blocks[idx + 1]
          ) = (
              st.session_state.seance_blocks[idx + 1],
              st.session_state.seance_blocks[idx],
          )
          st.rerun()

      with col_del:
        if st.button("🗑️ Enlever", key=f"rm_{idx}"):
          blocks_to_remove.append(idx)

    if blocks_to_remove:
      for b_idx in reversed(blocks_to_remove):
        st.session_state.seance_blocks.pop(b_idx)
      st.rerun()

    # Affichage récapitulatif
    st.markdown("---")
    st.markdown(f"### 📄 Déroulé : {titre_seance}")

    total_duree = 0
    if st.session_state.seance_blocks:
      for idx, block in enumerate(st.session_state.seance_blocks):
        clean_title = block["exo_title"].split(" [")[0]
        exo = next((e for e in data if e["titre"] == clean_title), None)

        if exo:
          total_duree += block["duree"]
          st.markdown(
              f"""
                <div class='exo-card'>
                    <strong style='color:#ffffff; font-size:1.1rem;'>{idx+1}. {exo['titre']} ({block['duree']} min)</strong><br>
                    <span style='color:#aaaaaa;'>Groupe : {block['groupe_custom']} | Type : {exo['type']} | Espace : {exo['espace']}</span><br><br>
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

      st.metric("Durée Totale de la Séance", f"{total_duree} min")
    else:
      st.info("Cliquez sur 'Ajouter une étape' pour construire votre séance.")

# -----------------------------------------------------------------------------
# 4. PARAMÈTRES
# -----------------------------------------------------------------------------
elif st.session_state.page == "parametres":
  st.subheader("⚙️ Paramètres")

  with st.form("form_config"):
    nom_equipe = st.text_input(
        "Nom du club / de l'équipe", value=config["nom_equipe"]
    )
    save_btn = st.form_submit_button("💾 Enregistrer la configuration")

    if save_btn:
      config["nom_equipe"] = nom_equipe
      save_config(config)
      st.success("Paramètres mis à jour !")
      st.rerun()
