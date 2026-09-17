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
SEANCES_FILE = "seances_rugby.json"
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

DEFAULT_CONFIG = {"nom_equipe": "STADE LÉONIEN"}


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


def load_seances():
  if os.path.exists(SEANCES_FILE):
    with open(SEANCES_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


def save_seance(seance_data):
  seances = load_seances()
  seances.append(seance_data)
  with open(SEANCES_FILE, "w", encoding="utf-8") as f:
    json.dump(seances, f, ensure_ascii=False, indent=4)


def calculate_total_duration(blocks):
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


def build_grouped_blocks(blocks):
  """Regroupe les blocs simultanés consécutifs par paire pour l'affichage côte à côte."""
  grouped = []
  i = 0
  while i < len(blocks):
    curr = blocks[i]
    if (
        curr.get("simultané", False)
        and i + 1 < len(blocks)
        and blocks[i + 1].get("simultané", False)
    ):
      grouped.append({"type": "pair", "items": [curr, blocks[i + 1]]})
      i += 2
    else:
      grouped.append({"type": "single", "items": [curr]})
      i += 1
  return grouped


def generate_export_html(titre_seance, nom_equipe, blocks, data):
  total_dur = calculate_total_duration(blocks)
  grouped = build_grouped_blocks(blocks)

  html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{titre_seance} - {nom_equipe}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #111; background: #fff; }}
        .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; text-transform: uppercase; }}
        .header h2 {{ margin: 5px 0 0 0; font-size: 18px; color: #555; }}
        .meta {{ font-size: 14px; font-weight: bold; margin-bottom: 15px; background: #eee; padding: 8px; border-radius: 4px; }}
        .row-single {{ margin-bottom: 12px; }}
        .row-pair {{ display: flex; gap: 10px; margin-bottom: 12px; }}
        .card {{ border: 1px solid #333; padding: 10px; border-radius: 6px; background: #fdfdfd; box-sizing: border-box; }}
        .card-full {{ width: 100%; }}
        .card-half {{ flex: 1; border-left: 4px solid #ff9800; }}
        .card-title {{ font-weight: bold; font-size: 15px; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-bottom: 6px; }}
        .card-meta {{ font-size: 12px; color: #555; margin-bottom: 6px; }}
        .card-body {{ font-size: 13px; line-height: 1.3; }}
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏉 {nom_equipe}</h1>
        <h2>Fiche de Séance : {titre_seance}</h2>
    </div>
    <div class="meta">Durée totale estimée : {total_dur} minutes</div>
"""
  exo_count = 1
  for group in grouped:
    if group["type"] == "single":
      block = group["items"][0]
      clean_title = block["exo_title"].split(" [")[0]
      exo = next((e for e in data if e["titre"] == clean_title), None)
      consignes = exo.get("consignes", "") if exo else ""
      grp_name = exo.get("groupe", "N/A") if exo else "N/A"
      esp = exo.get("espace", "N/A") if exo else "N/A"

      html_content += f"""
        <div class="row-single">
            <div class="card card-full">
                <div class="card-title">{exo_count}. {clean_title} ({block['duree']} min)</div>
                <div class="card-meta"><b>Groupe:</b> {grp_name} | <b>Matériel:</b> {esp}</div>
                <div class="card-body">{consignes}</div>
            </div>
        </div>"""
      exo_count += 1
    else:
      html_content += '<div class="row-pair">'
      for block in group["items"]:
        clean_title = block["exo_title"].split(" [")[0]
        exo = next((e for e in data if e["titre"] == clean_title), None)
        consignes = exo.get("consignes", "") if exo else ""
        grp_name = exo.get("groupe", "N/A") if exo else "N/A"
        esp = exo.get("espace", "N/A") if exo else "N/A"

        html_content += f"""
            <div class="card card-half">
                <div class="card-title">⚡ {exo_count}. {clean_title} ({block['duree']} min)</div>
                <div class="card-meta"><b>Groupe:</b> {grp_name} | <b>Matériel:</b> {esp}</div>
                <div class="card-body">{consignes}</div>
            </div>"""
        exo_count += 1
      html_content += "</div>"

  html_content += """
</body>
</html>"""
  return html_content


if "page" not in st.session_state:
  st.session_state.page = "home"

if "edit_exo_idx" not in st.session_state:
  st.session_state.edit_exo_idx = None

if "seance_blocks" not in st.session_state:
  st.session_state.seance_blocks = []

if "quick_create_mode" not in st.session_state:
  st.session_state.quick_create_mode = False

if "quick_create_insert_idx" not in st.session_state:
  st.session_state.quick_create_insert_idx = None

config = load_config()

st.markdown(
    """
    <style>
    .stApp { background-color: #0d0d0d !important; color: #ffffff !important; }
    .block-container { max-width: 720px !important; padding-top: 1.5rem !important; }
    label, .stWidgetLabel, p, h1, h2, h3, h4, span { color: #ffffff !important; }
    input, textarea, select, div[data-baseweb="select"] { background-color: #1a1a1a !important; color: #ffffff !important; border: 1px solid #444444 !important; }
    .main-header { text-align: center; padding-bottom: 15px; border-bottom: 1px solid #333333; margin-bottom: 20px; }
    .main-title { font-size: 1.8rem; font-weight: 800; text-transform: uppercase; margin: 0; }
    .stButton>button { width: 100% !important; background-color: #1e1e1e !important; color: #ffffff !important; font-weight: 600 !important; border: 1px solid #444444 !important; border-radius: 6px !important; }
    .stButton>button:hover { background-color: #ffffff !important; color: #000000 !important; }
    .exo-card { background-color: #141414; border: 1px solid #333333; border-radius: 6px; padding: 12px; margin-bottom: 8px; }
    .exo-card-simultane { border-left: 4px solid #ff9800 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="main-header">
        <h1 class="main-title">🏉 {config['nom_equipe']}</h1>
    </div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------
if st.session_state.page == "home":
  st.session_state.quick_create_mode = False
  if st.button("📋 Créer une Séance", key="btn_seance"):
    st.session_state.page = "seance"
    st.rerun()

  if st.button("📜 Historique des Séances", key="btn_histo"):
    st.session_state.page = "historique"
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

if st.session_state.page != "home":
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
    if st.button("➕ Ajouter un exercice"):
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
          st.image(exo["image_path"], use_container_width=True)

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
        "espace": "",
        "consignes": "",
        "image_path": None,
    }

  with st.form("form_add_exo"):
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

    submitted = st.form_submit_button("💾 ENREGISTRER L'EXERCICE")

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
      else:
        data.append(updated_exo)

      save_all_data(data)
      st.session_state.page = "banque"
      st.rerun()

# -----------------------------------------------------------------------------
# 3. CRÉATION DE SÉANCE
# -----------------------------------------------------------------------------
elif st.session_state.page == "seance":
  data = load_data()

  # Formulaire rapide de création d'exercice
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

      col_q1, col_q2 = st.columns(2)
      with col_q1:
        q_submitted = st.form_submit_button("💾 CRÉER ET INSÉRER")
      with col_q2:
        q_cancel = st.form_submit_button("❌ ANNULER")

      if q_cancel:
        st.session_state.quick_create_mode = False
        st.rerun()

      if q_submitted and q_titre:
        new_exo = {
            "titre": q_titre,
            "groupe": q_groupe,
            "type": q_type,
            "espace": q_espace,
            "consignes": q_consignes,
            "image_path": None,
        }
        data.append(new_exo)
        save_all_data(data)

        new_block = {
            "exo_title": f"{q_titre} [{q_type}]",
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
        st.rerun()

  elif not data:
    st.info("Aucun exercice dans la banque. Créez un exercice pour commencer.")
    if st.button("⚡ Créer un premier exercice"):
      st.session_state.quick_create_mode = True
      st.session_state.quick_create_insert_idx = 0
      st.rerun()

  else:
    st.subheader("📋 Création de la Séance")
    titre_seance = st.text_input("Thème de la séance", "Séance du jour")
    titles_list = [f"{e['titre']} [{e['type']}]" for e in data]

    # Barres d'actions haut de page
    col_a1, col_a2, col_a3 = st.columns([1.5, 1.8, 1])
    with col_a1:
      if st.button("➕ Ajouter exo"):
        st.session_state.seance_blocks.append(
            {"exo_title": titles_list[0], "duree": 15, "simultané": False}
        )
        st.rerun()
    with col_a2:
      if st.button("⚡ Créer & Insérer"):
        st.session_state.quick_create_mode = True
        st.session_state.quick_create_insert_idx = len(
            st.session_state.seance_blocks
        )
        st.rerun()
    with col_a3:
      if st.session_state.seance_blocks and st.button("➖ Vider"):
        st.session_state.seance_blocks = []
        st.rerun()

    st.markdown("---")

    # Liste simplifiée et épurée des blocs
    blocks_to_remove = []
    for idx, block in enumerate(st.session_state.seance_blocks):
      c_sel, c_dur, c_sim, c_opt = st.columns([3.5, 1.5, 1.5, 1])

      with c_sel:
        sel_idx = (
            titles_list.index(block["exo_title"])
            if block["exo_title"] in titles_list
            else 0
        )
        block["exo_title"] = st.selectbox(
            f"Exo {idx+1}",
            titles_list,
            index=sel_idx,
            key=f"b_title_{idx}",
            label_visibility="collapsed",
        )

      with c_dur:
        block["duree"] = st.number_input(
            "Min",
            min_value=1,
            max_value=90,
            value=int(block.get("duree", 15)),
            key=f"b_dur_{idx}",
            label_visibility="collapsed",
        )

      with c_sim:
        block["simultané"] = st.checkbox(
            "⚡ Simultané",
            value=block.get("simultané", False),
            key=f"b_sim_{idx}",
        )

      # Menu contextuel d'options épuré (popover)
      with c_opt:
        with st.popover("⚙️"):
          if idx > 0 and st.button("⬆️ Monter", key=f"up_{idx}"):
            st.session_state.seance_blocks[idx], (
                st.session_state.seance_blocks[idx - 1]
            ) = (
                st.session_state.seance_blocks[idx - 1],
                st.session_state.seance_blocks[idx],
            )
            st.rerun()

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

          if st.button("➕ Insérer exo ici", key=f"ins_ex_{idx}"):
            st.session_state.seance_blocks.insert(
                idx + 1,
                {
                    "exo_title": titles_list[0],
                    "duree": 15,
                    "simultané": False,
                },
            )
            st.rerun()

          if st.button("⚡ Créer & Insérer ici", key=f"ins_new_{idx}"):
            st.session_state.quick_create_mode = True
            st.session_state.quick_create_insert_idx = idx + 1
            st.rerun()

          if st.button("🗑️ Supprimer", key=f"del_{idx}"):
            blocks_to_remove.append(idx)

    if blocks_to_remove:
      for b_idx in reversed(blocks_to_remove):
        st.session_state.seance_blocks.pop(b_idx)
      st.rerun()

    # SECTION APERÇU ET ACTIONS FINALES
    if st.session_state.seance_blocks:
      st.markdown("---")
      total_duree = calculate_total_duration(st.session_state.seance_blocks)
      st.metric("Durée Totale Réelle", f"{total_duree} min")

      st.markdown("### 📄 Aperçu de la séance")

      # Visualisation côte à côte dans Streamlit
      grouped = build_grouped_blocks(st.session_state.seance_blocks)
      exo_counter = 1

      for group in grouped:
        if group["type"] == "single":
          b = group["items"][0]
          clean_title = b["exo_title"].split(" [")[0]
          exo = next((e for e in data if e["titre"] == clean_title), None)
          st.markdown(
              f"""
                    <div class='exo-card'>
                        <strong>{exo_counter}. {clean_title} ({b['duree']} min)</strong><br>
                        <small style='color:#aaa;'>{exo.get('groupe', '') if exo else ''} | Matériel: {exo.get('espace', '') if exo else ''}</small><br>
                        <span style='font-size:0.9rem;'>{exo.get('consignes', '') if exo else ''}</span>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
          exo_counter += 1
        else:
          col_s1, col_s2 = st.columns(2)
          cols = [col_s1, col_s2]
          for item_idx, b in enumerate(group["items"]):
            clean_title = b["exo_title"].split(" [")[0]
            exo = next((e for e in data if e["titre"] == clean_title), None)
            with cols[item_idx]:
              st.markdown(
                  f"""
                                <div class='exo-card exo-card-simultane'>
                                    <strong>⚡ {exo_counter}. {clean_title} ({b['duree']} min)</strong><br>
                                    <small style='color:#aaa;'>{exo.get('groupe', '') if exo else ''}</small><br>
                                    <span style='font-size:0.85rem;'>{exo.get('consignes', '') if exo else ''}</span>
                                </div>
                                """,
                  unsafe_allow_html=True,
              )
              exo_counter += 1

      st.markdown("---")

      col_save, col_exp = st.columns(2)
      with col_save:
        if st.button("💾 Enregistrer dans l'historique"):
          seance_obj = {
              "titre": titre_seance,
              "duree_totale": total_duree,
              "blocks": st.session_state.seance_blocks,
          }
          save_seance(seance_obj)
          st.success("Séance enregistrée dans l'historique !")

      with col_exp:
        html_file = generate_export_html(
            titre_seance,
            config["nom_equipe"],
            st.session_state.seance_blocks,
            data,
        )
        st.download_button(
            label="📥 Télécharger la Fiche Visuelle (HTML/PDF)",
            data=html_file,
            file_name=f"{titre_seance.lower().replace(' ', '_')}.html",
            mime="text/html",
        )

# -----------------------------------------------------------------------------
# 4. HISTORIQUE DES SÉANCES
# -----------------------------------------------------------------------------
elif st.session_state.page == "historique":
  st.subheader("📜 Historique des Séances")
  seances = load_seances()
  data = load_data()

  if seances:
    for s_idx, s in enumerate(reversed(seances)):
      with st.expander(f"{s['titre']} — {s['duree_totale']} min"):
        st.write(f"**Nombre d'exercices :** {len(s['blocks'])}")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
          if st.button("🔄 Charger dans l'éditeur", key=f"load_s_{s_idx}"):
            st.session_state.seance_blocks = s["blocks"]
            st.session_state.page = "seance"
            st.rerun()
        with col_h2:
          html_file = generate_export_html(
              s["titre"], config["nom_equipe"], s["blocks"], data
          )
          st.download_button(
              label="📥 Exporter la fiche",
              data=html_file,
              file_name=f"{s['titre'].lower().replace(' ', '_')}.html",
              mime="text/html",
              key=f"dl_s_{s_idx}",
          )
  else:
    st.info("Aucune séance enregistrée pour le moment.")

# -----------------------------------------------------------------------------
# 5. PARAMÈTRES
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
