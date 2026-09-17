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


def calculate_total_duration(blocks):
  """Calcule la durée totale en prenant le max pour deux exercices consécutifs en simultané."""
  total = 0
  skip_next = False
  for i in range(len(blocks)):
    if skip_next:
      skip_next = False
      continue

    curr = blocks[i]
    is_sim = curr.get("simultané", False)

    if is_sim and i + 1 < len(blocks) and blocks[i + 1].get("simultané", False):
      total += max(int(curr["duree"]), int(blocks[i + 1]["duree"]))
      skip_next = True
    else:
      total += int(curr["duree"])
  return total


if "page" not in st.session_state:
  st.session_state.page = "home"

if "edit_exo_idx" not in st.session_state:
  st.session_state.edit_exo_idx = None

if "seance_blocks" not in st.session_state:
  st.session_state.seance_blocks = []

if "print_mode" not in st.session_state:
  st.session_state.print_mode = False

if "quick_create_mode" not in st.session_state:
  st.session_state.quick_create_mode = False

if "quick_create_insert_idx" not in st.session_state:
  st.session_state.quick_create_insert_idx = None

config = load_config()

# --- STYLES CSS SOBRES ET HAUT CONTRASTE + STYLE IMPRESSION ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        max-width: 720px !important;
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

    div[data-testid="stFormSubmitButton"] > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        border: 2px solid #ffffff !important;
        padding: 14px 20px !important;
        margin-top: 15px !important;
        border-radius: 6px !important;
    }
    div[data-testid="stFormSubmitButton"] > button * {
        color: #000000 !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #dddddd !important;
        border-color: #dddddd !important;
    }

    .exo-card {
        background-color: #141414;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .exo-card-simultane {
        border-left: 4px solid #ff9800 !important;
    }

    @media print {
        body, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .no-print, header, footer, .stButton {
            display: none !important;
        }
        .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
        .print-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .print-card {
            border: 1px solid #000000 !important;
            padding: 10px !important;
            page-break-inside: avoid;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .print-card * {
            color: #000000 !important;
        }
        .print-title {
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-bottom: 1px solid #000;
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# En-tête
if not st.session_state.print_mode:
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
# NAVIGATION
# -----------------------------------------------------------------------------
if st.session_state.page == "home":
  st.session_state.print_mode = False
  st.session_state.quick_create_mode = False
  st.write("")
  if st.button("📋 Créer une Séance", key="btn_seance"):
    st.session_state.page = "seance"
    st.rerun()

  if st.button("📚 Banque d'Exercices", key="btn_banque"):
    st.session_state.page = "banque"
    st.rerun()

  if st.button("➕ Ajouter un Exercice à la banque", key="btn_ajouter"):
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

if st.session_state.page != "home" and not st.session_state.print_mode:
  if st.button("⬅️ Retour à l'accueil"):
    st.session_state.page = "home"
    st.session_state.edit_exo_idx = None
    st.session_state.quick_create_mode = False
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
  col_title, col_add = st.columns([1.8, 1.2])
  with col_title:
    st.subheader("📚 Banque d'Exercices")
  with col_add:
    if st.button("➕ Ajouter un exercice", key="btn_add_from_bank"):
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

      with st.expander(f"{exo['titre']} — {exo.get('groupe', 'N/A')}"):
        st.write(f"**Groupe :** {exo.get('groupe', 'N/A')}")
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
          if st.button("🗑️ Supprimer l'exercice", key=f"del_{real_idx}"):
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
# 2. CRÉER / MODIFIER UN EXERCICE (BANQUE)
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
    groupe = st.selectbox("Groupe concerné", CATEGORIES_GROUPE, index=idx_grp)

    idx_type = (
        TYPES_EXERCICE.index(exo_to_edit["type"])
        if exo_to_edit["type"] in TYPES_EXERCICE
        else 0
    )
    type_exo = st.selectbox("Type d'exercice", TYPES_EXERCICE, index=idx_type)

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
        "💾 METTRE À JOUR L'EXERCICE"
        if is_editing
        else "💾 ENREGISTRER L'EXERCICE"
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
# 3. CRÉATION DE SÉANCE SÉQUENTIELLE
# -----------------------------------------------------------------------------
elif st.session_state.page == "seance":
  data = load_data()

  # MODAL/FORMULAIRE DE CRÉATION RAPIDE D'EXERCICE DEPUIS LA SÉANCE
  if st.session_state.quick_create_mode:
    st.subheader("⚡ Créer et insérer un nouvel exercice")

    with st.form("form_quick_add_exo"):
      q_titre = st.text_input("Nom de l'exercice")
      q_groupe = st.selectbox("Groupe concerné", CATEGORIES_GROUPE)
      q_type = st.selectbox("Type d'exercice", TYPES_EXERCICE)
      q_duree = st.number_input(
          "Durée pour cette séance (min)",
          min_value=1,
          max_value=90,
          value=15,
      )
      q_espace = st.text_input("Terrain / Matériel requis")
      q_consignes = st.text_area("Consignes & Règles du jeu")
      q_uploaded_file = st.file_uploader(
          "Schéma ou image (optionnel)", type=["png", "jpg", "jpeg"]
      )

      col_q1, col_q2 = st.columns(2)
      with col_q1:
        q_submitted = st.form_submit_button("💾 CRÉER ET INSÉRER")
      with col_q2:
        q_cancel = st.form_submit_button("❌ ANNULER")

      if q_cancel:
        st.session_state.quick_create_mode = False
        st.rerun()

      if q_submitted and q_titre:
        q_image_path = None
        if q_uploaded_file is not None:
          filename = f"{q_titre.lower().replace(' ', '_')}_{q_uploaded_file.name[-8:]}"
          q_image_path = os.path.join(IMAGE_DIR, filename)
          with open(q_image_path, "wb") as f:
            f.write(q_uploaded_file.getbuffer())

        new_exo = {
            "titre": q_titre,
            "groupe": q_groupe,
            "type": q_type,
            "espace": q_espace,
            "consignes": q_consignes,
            "image_path": q_image_path,
        }
        data.append(new_exo)
        save_all_data(data)

        new_title_formatted = f"{q_titre} [{q_type}]"
        new_block = {
            "exo_title": new_title_formatted,
            "duree": int(q_duree),
            "simultané": False,
        }

        idx_insert = st.session_state.quick_create_insert_idx
        if idx_insert is None or idx_insert >= len(
            st.session_state.seance_blocks
        ):
          st.session_state.seance_blocks.append(new_block)
        else:
          st.session_state.seance_blocks.insert(idx_insert, new_block)

        st.session_state.quick_create_mode = False
        st.success(f"Exercice '{q_titre}' créé et inséré !")
        st.rerun()

  elif not data:
    st.info(
        "La banque d'exercices est vide. Vous pouvez soit créer votre premier"
        " exercice ci-dessous, soit passer par la banque."
    )
    if st.button("⚡ Créer un premier exercice"):
      st.session_state.quick_create_mode = True
      st.session_state.quick_create_insert_idx = 0
      st.rerun()

  else:
    if st.session_state.print_mode:
      st.markdown(f"# 🏉 {config['nom_equipe']}")
      st.markdown(
          f"### Séance : {st.session_state.get('titre_seance', 'Sans titre')}"
      )

      total_dur = calculate_total_duration(st.session_state.seance_blocks)
      st.markdown(f"**Durée totale de la séance :** {total_dur} min")
      st.markdown("---")

      cards_html = "<div class='print-grid'>"
      for idx, block in enumerate(st.session_state.seance_blocks):
        clean_title = block["exo_title"].split(" [")[0]
        exo = next((e for e in data if e["titre"] == clean_title), None)
        if exo:
          sim_tag = "⚡ (Simultané)" if block.get("simultané") else ""
          cards_html += f"""
                    <div class='print-card' style='border: 1px solid #444; padding: 10px; margin-bottom: 10px; border-radius: 4px;'>
                        <div class='print-title'><strong>{idx+1}. {exo['titre']} {sim_tag}</strong> ({block['duree']} min)</div>
                        <div style='font-size: 0.85rem; color: #aaa; margin-bottom: 6px;'>
                            <b>Groupe :</b> {exo.get('groupe', 'N/A')} | <b>Type :</b> {exo.get('type', 'N/A')}<br>
                            <b>Matériel :</b> {exo.get('espace', 'N/A')}
                        </div>
                        <div style='font-size: 0.9rem;'>{exo.get('consignes', '')}</div>
                    </div>
                    """
      cards_html += "</div>"
      st.markdown(cards_html, unsafe_allow_html=True)

      st.markdown("<br>", unsafe_allow_html=True)
      col_p1, col_p2 = st.columns(2)
      with col_p1:
        if st.button("🖨️ Lancer l'impression (Navigateur)"):
          st.components.v1.html(
              "<script>window.print();</script>", height=0, width=0
          )
      with col_p2:
        if st.button("⬅️ Quitter la vue d'impression"):
          st.session_state.print_mode = False
          st.rerun()

    else:
      st.subheader("📋 Créer une Séance Libre")
      titre_seance = st.text_input("Thème de la séance", "Séance du jour")
      st.session_state.titre_seance = titre_seance
      titles_list = [f"{e['titre']} [{e['type']}]" for e in data]

      st.markdown("### 1. Sélection et ordonnancement")

      col_btn_add, col_btn_new, col_btn_clear = st.columns([1.5, 1.8, 1])
      with col_btn_add:
        if st.button("➕ Exercice existant"):
          st.session_state.seance_blocks.insert(
              0,
              {
                  "exo_title": titles_list[0],
                  "duree": 15,
                  "simultané": False,
              },
          )
          st.rerun()

      with col_btn_new:
        if st.button("⚡ Créer & Insérer un exo"):
          st.session_state.quick_create_mode = True
          st.session_state.quick_create_insert_idx = 0
          st.rerun()

      with col_btn_clear:
        if st.session_state.seance_blocks and st.button("➖ Vider"):
          st.session_state.seance_blocks = []
          st.rerun()

      blocks_to_remove = []
      insert_index = None

      for idx, block in enumerate(st.session_state.seance_blocks):
        clean_title = block["exo_title"].split(" [")[0]
        exo_current = next(
            (e for e in data if e["titre"] == clean_title), data[0]
        )

        st.markdown(f"--- **Exercice {idx+1}** ---")
        c_exo, c_dur = st.columns([4, 2])

        with c_exo:
          sel_idx = (
              titles_list.index(block["exo_title"])
              if block["exo_title"] in titles_list
              else 0
          )
          new_exo_title = st.selectbox(
              "Exercice", titles_list, index=sel_idx, key=f"blk_exo_{idx}"
          )

          if new_exo_title != block["exo_title"]:
            block["exo_title"] = new_exo_title
            st.rerun()

        with c_dur:
          block["duree"] = st.number_input(
              "Durée séance (min)",
              min_value=1,
              max_value=90,
              value=int(block.get("duree", 15)),
              key=f"blk_dur_{idx}",
          )

        block["simultané"] = st.checkbox(
            "⚡ En simultané (ne double pas le décompte temps)",
            value=block.get("simultané", False),
            key=f"sim_{idx}",
        )

        st.caption(
            f"🎯 Groupe : **{exo_current.get('groupe', 'Non défini')}** | Type :"
            f" {exo_current.get('type', 'N/A')}"
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
          if st.button("➖ Retirer", key=f"rm_{idx}"):
            blocks_to_remove.append(idx)

        c_ins1, c_ins2 = st.columns(2)
        with c_ins1:
          if st.button(
              f"➕ Insérer existant après {idx+1}", key=f"add_after_{idx}"
          ):
            insert_index = idx + 1
        with c_ins2:
          if st.button(
              f"⚡ Créer & Insérer après {idx+1}", key=f"new_after_{idx}"
          ):
            st.session_state.quick_create_mode = True
            st.session_state.quick_create_insert_idx = idx + 1
            st.rerun()

      if insert_index is not None:
        st.session_state.seance_blocks.insert(
            insert_index,
            {
                "exo_title": titles_list[0],
                "duree": 15,
                "simultané": False,
            },
        )
        st.rerun()

      if blocks_to_remove:
        for b_idx in reversed(blocks_to_remove):
          st.session_state.seance_blocks.pop(b_idx)
        st.rerun()

      st.markdown("---")
      col_sec_title, col_sec_print = st.columns([1.8, 1.2])
      with col_sec_title:
        st.markdown(f"### 📄 Aperçu : {titre_seance}")
      with col_sec_print:
        if st.session_state.seance_blocks and st.button(
            "🖨️ Vue Impression (2 col.)"
        ):
          st.session_state.print_mode = True
          st.rerun()

      if st.session_state.seance_blocks:
        for idx, block in enumerate(st.session_state.seance_blocks):
          clean_title = block["exo_title"].split(" [")[0]
          exo = next((e for e in data if e["titre"] == clean_title), None)

          if exo:
            is_sim = block.get("simultané", False)
            sim_badge = " ⚡ [SIMULTANÉ]" if is_sim else ""
            card_class = "exo-card exo-card-simultane" if is_sim else "exo-card"

            st.markdown(
                f"""
                  <div class='{card_class}'>
                      <strong style='color:#ffffff; font-size:1.1rem;'>{idx+1}. {exo['titre']} ({block['duree']} min){sim_badge}</strong><br>
                      <span style='color:#aaaaaa;'>Groupe : {exo.get('groupe', 'N/A')} | Type : {exo['type']} | Espace : {exo['espace']}</span><br><br>
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

        total_duree = calculate_total_duration(st.session_state.seance_blocks)
        st.metric(
            "Durée Totale Réelle de la Séance",
            f"{total_duree} min",
            help=(
                "Les ateliers cochés 'simultané' consécutifs prennent la durée"
                " max du groupe au lieu de s'additionner."
            ),
        )
      else:
        st.info("Ajoutez des exercices pour composer votre programme.")

# -----------------------------------------------------------------------------
# 4. PARAMÈTRES
# -----------------------------------------------------------------------------
elif st.session_state.page == "parametres":
  st.subheader("⚙️ Paramètres")

  with st.form("form_config"):
    nom_equipe = st.text_input(
        "Nom du club / de l'équipe", value=config["nom_equipe"]
    )
    save_btn = st.form_submit_button("💾 ENREGISTRER LA CONFIGURATION")

    if save_btn:
      config["nom_equipe"] = nom_equipe
      save_config(config)
      st.success("Paramètres mis à jour !")
      st.rerun()
