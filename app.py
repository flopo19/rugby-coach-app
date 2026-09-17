# --- CSS ÉPURÉ, RESPONSIVE & HAUT CONTRASTE ---
st.markdown(
    f"""
    <style>
    /* Fond principal */
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

    /* Labels des formulaires & champs (Correction contraste) */
    label, .stWidgetLabel, div[data-testid="stMarkdownContainer"] p {{
        color: #f0f0f0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    
    /* Textes d'aide et zones d'upload */
    .stFileUploader small, div[data-testid="stUploadDropzone"] span {{
        color: #d0d0d0 !important;
    }}

    /* Titres et en-tête */
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

    /* Boutons de navigation principal */
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

    /* Cartes exercices */
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
