import io
import os
import sys
import base64
import glob
import sqlite3
import requests
import uuid
import streamlit as st
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Lista de Presença - Festa de Sábado 🎉",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
    /* Quando a sidebar é recolhida, o Streamlit deixa um pequeno
       controle "flutuante" (a setinha ">>" para reabrir) do lado
       esquerdo. Forçamos o fundo dele (e de tudo dentro) para branco. */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] * {
        background-color: #ffffff !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        border-radius: 8px;
    }
    button[aria-label="Open sidebar"],
    button[aria-label="Expand sidebar"] {
        background-color: #ffffff !important;
    }
    .ticket-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px dashed #3b82f6;
        border-radius: 16px;
        padding: 24px;
        color: #f8fafc;
        margin: 20px 0;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .ticket-header {
        text-align: center;
        border-bottom: 1px dashed #475569;
        padding-bottom: 16px;
        margin-bottom: 20px;
    }
    .ticket-title {
        color: #4ade80;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
    }
    .ticket-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 4px;
    }
    .ticket-notice {
        background-color: rgba(251, 191, 36, 0.15);
        border: 1px solid #f59e0b;
        color: #fef08a;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        margin-top: 10px;
    }
    .ticket-item {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-family: monospace, monospace;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ticket-number {
        color: #60a5fa;
        font-weight: bold;
        font-size: 18px;
    }
    .ticket-footer {
        text-align: center;
        border-top: 1px dashed #475569;
        margin-top: 20px;
        padding-top: 12px;
        color: #64748b;
        font-size: 12px;
    }
    .checkin-badge-ok {
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid #4ade80;
        color: #4ade80;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }
    .checkin-badge-pending {
        background: rgba(148, 163, 184, 0.15);
        border: 1px solid #64748b;
        color: #94a3b8;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }
    .qr-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        margin-bottom: 6px;
    }
    .qr-card-name {
        color: #0f172a;
        font-weight: 800;
        font-size: 15px;
        margin-top: 6px;
    }
    .qr-card-number {
        color: #2563eb;
        font-weight: 700;
        font-size: 13px;
    }
    .scan-result-ok {
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid #4ade80;
        color: #4ade80;
        padding: 14px;
        border-radius: 10px;
        font-weight: 700;
        text-align: center;
        margin: 10px 0;
    }
    .scan-result-warn {
        background: rgba(251, 191, 36, 0.15);
        border: 1px solid #f59e0b;
        color: #fef08a;
        padding: 14px;
        border-radius: 10px;
        font-weight: 700;
        text-align: center;
        margin: 10px 0;
    }
    .scan-result-error {
        background: rgba(248, 113, 113, 0.15);
        border: 1px solid #f87171;
        color: #f87171;
        padding: 14px;
        border-radius: 10px;
        font-weight: 700;
        text-align: center;
        margin: 10px 0;
    }
    /* Cartão 3D que "flutua" sobre o fundo da festa, envolvendo o
       formulário/ticket do convidado, para manter tudo legível mesmo
       com uma imagem de fundo pesada. */
    div[class*="st-key-guest_page_card"] {
        background: rgba(30, 41, 59, 0.275);
        backdrop-filter: blur(1px);
        -webkit-backdrop-filter: blur(1px);
        border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 28px 24px 20px 24px;
        margin: 14px auto 40px auto;
        max-width: 640px;
        transform: perspective(1400px) rotateX(1.2deg);
        box-shadow:
            0 30px 60px -15px rgba(0, 0, 0, 0.65),
            0 10px 25px -8px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.04) inset;
        transition: transform 0.25s ease;
    }
    div[class*="st-key-guest_page_card"]:hover {
        transform: perspective(1400px) rotateX(0deg) translateY(-2px);
    }
    /* Garante texto claro e legível dentro do card, independente do
       tema (claro/escuro) do Streamlit — título, parágrafos, labels
       de campos e texto de erro/aviso. */
    div[class*="st-key-guest_page_card"] h1,
    div[class*="st-key-guest_page_card"] h2,
    div[class*="st-key-guest_page_card"] h3,
    div[class*="st-key-guest_page_card"] p,
    div[class*="st-key-guest_page_card"] span,
    div[class*="st-key-guest_page_card"] label,
    div[class*="st-key-guest_page_card"] .stMarkdown,
    div[class*="st-key-guest_page_card"] [data-testid="stMarkdownContainer"] {
        color: #f8fafc !important;
    }
    div[class*="st-key-guest_page_card"] [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
        font-weight: 600;
    }
    
    /* Corrige a cor da caixa de texto (código) após a inclusão */
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"],
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] * {
        color: #000000 !important;
        text-shadow: none !important;
    }
    /* Centraliza o card na página (layout wide não centraliza sozinho). */
    div[class*="st-key-guest_page_card"] {
        margin-left: auto;
        margin-right: auto;
    }
    @media (max-width: 640px) {
        div[class*="st-key-guest_page_card"] {
            transform: none;
            border-radius: 18px;
            padding: 20px 16px 14px 16px;
        }
        div[class*="st-key-guest_page_card"]:hover {
            transform: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. GERENCIAMENTO DO BANCO DE DADOS (SQLite)
# ==========================================
DB_FILE = "guests.db"

# ==========================================
# PASTA DE FUNDO PERSONALIZADO POR FESTA
# ==========================================
# Para trocar o fundo do formulário: coloque uma imagem (jpg, jpeg, png
# ou webp) dentro da pasta "fundo_festa" (na raiz do projeto). Só pode
# ter UMA imagem por vez ali — se tiver mais de uma, a primeira encontrada
# é usada. Para a próxima festa, é só trocar o arquivo dessa pasta.
FUNDO_FESTA_DIR = "fundo_festa"


def get_form_background_css():
    """Procura uma imagem dentro da pasta fundo_festa/ e devolve o bloco de
    CSS que aplica essa imagem como fundo (camada) só na área do
    formulário/tela do convidado. Retorna string vazia se não achar
    nenhuma imagem (fundo padrão é mantido)."""
    if not os.path.isdir(FUNDO_FESTA_DIR):
        return ""

    padroes = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    arquivos = []
    for padrao in padroes:
        arquivos.extend(glob.glob(os.path.join(FUNDO_FESTA_DIR, padrao)))

    if not arquivos:
        return ""

    caminho_imagem = sorted(arquivos)[0]
    ext = os.path.splitext(caminho_imagem)[1].lower().replace(".", "")
    mime = "jpeg" if ext == "jpg" else ext

    with open(caminho_imagem, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    return f"""
    <style>
        /* Imagem no tamanho NATURAL/original (background-size: contain),
           sem cortar nem distorcer, e sem nenhum filtro/overlay escuro
           por cima — a foto aparece com as cores originais.
        */
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stMain"] {{
            min-height: 100vh;
            background-color: #06080e !important;
            background-image:
                url("data:image/{mime};base64,{img_b64}") !important;
            background-size: contain !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        @media (max-width: 640px) {{
            [data-testid="stAppViewContainer"] > .main,
            [data-testid="stMain"] {{
                background-attachment: scroll !important;
            }}
        }}
    </style>
    """


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _create_guests_table(c):
    c.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_guest TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            is_companion INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checked_in INTEGER NOT NULL DEFAULT 0,
            checked_in_at TIMESTAMP
        )
    ''')
    existing_cols = {row["name"] for row in c.execute("PRAGMA table_info(guests)")}
    if "checked_in" not in existing_cols:
        c.execute("ALTER TABLE guests ADD COLUMN checked_in INTEGER NOT NULL DEFAULT 0")
    if "checked_in_at" not in existing_cols:
        c.execute("ALTER TABLE guests ADD COLUMN checked_in_at TIMESTAMP")


def init_db():
    """Cria a tabela 'guests' e garante que as colunas de check-in existam
    (inclusive em bancos antigos, via ALTER TABLE).

    Se o arquivo guests.db existir mas estiver corrompido/malformado
    (ex.: gravação interrompida no meio), o arquivo é automaticamente
    apagado e recriado do zero, para o app nunca ficar travado nisso."""
    try:
        conn = get_conn()
        c = conn.cursor()
        _create_guests_table(c)
        conn.commit()
        conn.close()
    except sqlite3.DatabaseError:
        try:
            conn.close()
        except Exception:
            pass
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        conn = get_conn()
        c = conn.cursor()
        _create_guests_table(c)
        conn.commit()
        conn.close()


def register_guests(responsible_name, guest_names):
    """Registra apenas os convidados informados, vinculados ao nome do
    responsável (quem convidou). O responsável em si NÃO vira uma linha
    na lista nem recebe QR Code — ele só aparece como referência embaixo
    do QR Code de cada convidado dele."""
    conn = get_conn()
    c = conn.cursor()

    registered = []

    for guest_name in guest_names:
        guest_name_clean = guest_name.strip()
        if guest_name_clean:
            c.execute('''
                INSERT INTO guests (main_guest, guest_name, is_companion, created_at)
                VALUES (?, ?, 1, datetime('now', 'localtime'))
            ''', (responsible_name, guest_name_clean))

            guest_id = c.lastrowid
            registered.append({
                "id": guest_id,
                "guest_name": guest_name_clean,
                "is_companion": True,
                "main_guest": responsible_name
            })

    conn.commit()
    conn.close()
    return registered


def get_all_guests():
    conn = get_conn()
    df = pd.read_sql_query('''
        SELECT
            id,
            guest_name,
            main_guest,
            is_companion,
            created_at,
            checked_in,
            checked_in_at
        FROM guests
        ORDER BY id ASC
    ''', conn)
    conn.close()
    return df


def set_checked_in(guest_id, value: bool):
    conn = get_conn()
    c = conn.cursor()
    if value:
        c.execute('''UPDATE guests SET checked_in = 1,
                      checked_in_at = datetime('now', 'localtime')
                      WHERE id = ?''', (guest_id,))
    else:
        c.execute('''UPDATE guests SET checked_in = 0, checked_in_at = NULL
                      WHERE id = ?''', (guest_id,))
    conn.commit()
    conn.close()


def update_guest_name(guest_id, new_name):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE guests SET guest_name = ? WHERE id = ?', (new_name, guest_id))
    conn.commit()
    conn.close()


def reset_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS guests')
    c.execute('''
        CREATE TABLE guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_guest TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            is_companion INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checked_in INTEGER NOT NULL DEFAULT 0,
            checked_in_at TIMESTAMP
        )
    ''')
    c.execute("DELETE FROM sqlite_sequence WHERE name='guests'")
    conn.commit()
    conn.close()


# ==========================================
# 1C. CONFIGURAÇÕES DO APP (Tamanho da Fonte)
# ==========================================
DEFAULT_ADMIN_FONT_SIZE = 16
DEFAULT_GUEST_FONT_SIZE = 16
ADMIN_FONT_SIZE_KEY = "admin_font_size"
GUEST_FONT_SIZE_KEY = "guest_font_size"


def _create_settings_table(c):
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')



def get_next_saturday_str():
    import datetime
    today = datetime.date.today()
    days_ahead = 5 - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return (today + datetime.timedelta(days=days_ahead)).strftime("%d/%m/%Y")

def get_setting(key: str, default):
    conn = get_conn()
    c = conn.cursor()
    _create_settings_table(c)
    conn.commit()
    row = c.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row is None:
        return default
    try:
        if isinstance(default, int):
            return int(row["value"])
        elif isinstance(default, float):
            return float(row["value"])
        else:
            return row["value"]
    except (TypeError, ValueError):
        return default


def set_setting(key: str, value):
    conn = get_conn()
    c = conn.cursor()
    _create_settings_table(c)
    c.execute('''
        INSERT INTO app_settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    ''', (key, str(value)))
    conn.commit()
    conn.close()


def build_font_size_css(scope_selector: str, size_px: int) -> str:
    """Gera um bloco <style> que ajusta o tamanho da fonte de todos os
    textos dentro de 'scope_selector' (títulos escalam proporcionalmente
    ao tamanho base escolhido)."""
    return f"""
    <style>
        {scope_selector} h1 {{ font-size: {size_px + 10}px !important; }}
        {scope_selector} h2 {{ font-size: {size_px + 6}px !important; }}
        {scope_selector} h3 {{ font-size: {size_px + 3}px !important; }}
        {scope_selector} p,
        {scope_selector} span,
        {scope_selector} label,
        {scope_selector} li,
        {scope_selector} div,
        {scope_selector} .stMarkdown,
        {scope_selector} [data-testid="stMarkdownContainer"],
        {scope_selector} [data-testid="stWidgetLabel"] p,
        {scope_selector} .stButton button p,
        {scope_selector} .stButton button,
        {scope_selector} input,
        {scope_selector} textarea {{
            font-size: {size_px}px !important;
        }}
    </style>
    """


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Gera um .xlsx em memória a partir do DataFrame de convidados."""
    output = io.BytesIO()
    export_df = df.copy()
    export_df["#ID"] = export_df["id"].apply(lambda x: f"#{x:03d}")
    export_df["Status"] = export_df["checked_in"].apply(lambda x: "Chegou" if x == 1 else "Aguardando")
    export_df = export_df.rename(columns={
        "guest_name": "Nome do Convidado",
        "main_guest": "Convidado de",
        "created_at": "Confirmado em",
        "checked_in_at": "Chegou em",
    })
    export_df = export_df[["#ID", "Nome do Convidado", "Convidado de",
                            "Status", "Confirmado em", "Chegou em"]]
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Convidados")
    return output.getvalue()


# ==========================================
# 1B. GERAÇÃO E LEITURA DE QR CODE
# ==========================================
QR_PREFIX = "FESTA-"


def _load_font(size: int):
    """Tenta carregar uma fonte TrueType comum; usa a fonte padrão do
    Pillow como último recurso (garante que sempre funcione, mesmo
    em ambientes sem as fontes do sistema)."""
    caminhos_possiveis = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                return ImageFont.truetype(caminho, size)
            except Exception:
                pass
    return ImageFont.load_default()


def decode_qr_from_image_bytes(image_bytes: bytes):
    """Decodifica um QR Code a partir dos bytes de uma foto (ex: vindos do
    st.camera_input). Retorna o texto decodificado, None se não achar
    nenhum QR Code na imagem, ou 'ERRO_DEPENDENCIA' se a biblioteca de
    leitura não estiver instalada."""
    try:
        import numpy as np
        import cv2
    except ImportError:
        return "ERRO_DEPENDENCIA"

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_cv is None:
        return None

    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img_cv)
    if data:
        return data
    return None


def guest_id_from_qr_payload(payload: str):
    """Extrai o ID do convidado de um texto de QR Code válido do sistema.
    Retorna None se o texto não seguir o formato esperado."""
    if not payload or not payload.startswith(QR_PREFIX):
        return None
    raw_id = payload[len(QR_PREFIX):].strip()
    if raw_id.isdigit():
        return int(raw_id)
    return None


def get_guest_by_id(guest_id: int):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM guests WHERE id = ?", (guest_id,)).fetchone()
    conn.close()
    return row


init_db()

# ==========================================
# APLICA OS TAMANHOS DE FONTE SALVOS
# ==========================================
_admin_font_size = get_setting(ADMIN_FONT_SIZE_KEY, DEFAULT_ADMIN_FONT_SIZE)
_guest_font_size = get_setting(GUEST_FONT_SIZE_KEY, DEFAULT_GUEST_FONT_SIZE)

st.markdown(build_font_size_css('section[data-testid="stSidebar"]', _admin_font_size), unsafe_allow_html=True)
st.markdown(build_font_size_css('div[class*="st-key-guest_page_card"]', _guest_font_size), unsafe_allow_html=True)


@st.dialog("Consultar Convidado")
def consultar_dialog():
    from st_keyup import st_keyup
    st.write("Verifique se seu nome já está na lista.")
    search_term = st_keyup("Digite seu nome para consultar:", key="consult_search")
    
    if "edit_guest_id" not in st.session_state:
        st.session_state["edit_guest_id"] = None

    if search_term:
        df_guests = get_all_guests()
        if not df_guests.empty:
            df_display = df_guests.copy()
            term = search_term.strip().lower()
            mask = df_display['guest_name'].str.lower().str.contains(term)
            results = df_display[mask]
            if not results.empty:
                st.success(f"🎉 Encontrado(s) {len(results)} resultado(s):")
                for _, row in results.iterrows():
                    guest_id = row['id']
                    current_name = row['guest_name']
                    
                    if st.session_state["edit_guest_id"] == guest_id:
                        new_name = st.text_input("Alterar Nome:", value=current_name, key=f"edit_input_{guest_id}")
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Salvar", key=f"save_{guest_id}", type="primary", use_container_width=True):
                                if new_name.strip():
                                    update_guest_name(guest_id, new_name.strip())
                                    st.session_state["edit_guest_id"] = None
                                    st.success("✅ Nome atualizado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("O nome não pode ser vazio.")
                        with col_cancel:
                            if st.button("Cancelar", key=f"cancel_{guest_id}", use_container_width=True):
                                st.session_state["edit_guest_id"] = None
                                st.rerun()
                    else:
                        col_info, col_act = st.columns([0.7, 0.3])
                        with col_info:
                            st.write(f"#{guest_id:03d} - {current_name}")
                        with col_act:
                            if st.button("Alterar", key=f"alter_{guest_id}", use_container_width=True):
                                st.session_state["edit_guest_id"] = guest_id
                                st.rerun()
            else:
                st.warning("⚠️ Nome não encontrado. Se ainda não enviou, preencha o formulário e clique em Incluir.")
        else:
            st.info("A lista ainda está vazia.")

# ==========================================
# PAINEL LATERAL (ANFITRIÃO / PORTARIA)
if "nav_radio" not in st.session_state:
    st.session_state["nav_radio"] = "🎉 Cadastro de Convidados"

# ==========================================
LOGO_PATH = os.path.join("logo", "logo_botteco_transparent.png")
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)

# ---------------------------------------------------------
# Botão de Copiar Lista no Menu Principal (Visível para todos)
# ---------------------------------------------------------
st.sidebar.markdown("---")

df_sidebar = get_all_guests()
if not df_sidebar.empty:
    t_header1 = get_setting("list_header1", "*LISTA VIP BOTTECO MUSIC*")
    t_header2 = get_setting("list_header2", "*Gardila / Marcelo / Jonas*")
    formatted_lines_sidebar = [
        t_header1,
        f"*Sábado - {get_next_saturday_str()}*",
        t_header2,
        ""
    ]
    for idx, row in enumerate(df_sidebar.itertuples(), start=1):
        line = f"{idx}. {row.guest_name}"
        formatted_lines_sidebar.append(line)
    
    import json
    formatted_text_json_sidebar = json.dumps("\n".join(formatted_lines_sidebar))
    
    import streamlit.components.v1 as components
    with st.sidebar:
        components.html(
            f'''
            <script>
            function copyToClipboardSidebar() {{
                const text = {formatted_text_json_sidebar};
                navigator.clipboard.writeText(text).then(() => {{
                    const btn = document.getElementById('copy-btn-sidebar');
                    btn.innerText = '✅ Copiado!';
                    setTimeout(() => {{ btn.innerText = '📋 Copiar Lista completa!'; }}, 2000);
                }});
            }}
            
            function applyThemeSidebar() {{
                try {{
                    const parentBody = window.parent.document.body;
                    const parentColor = window.parent.getComputedStyle(parentBody).color;
                    const btn = document.getElementById('copy-btn-sidebar');
                    btn.style.color = parentColor;
                    btn.style.borderColor = parentColor;
                    btn.style.opacity = '0.7';
                    
                    btn.addEventListener('mouseover', () => {{
                        btn.style.borderColor = '#ff4b4b';
                        btn.style.color = '#ff4b4b';
                        btn.style.opacity = '1';
                    }});
                    btn.addEventListener('mouseout', () => {{
                        btn.style.borderColor = parentColor;
                        btn.style.color = parentColor;
                        btn.style.opacity = '0.7';
                    }});
                }} catch(e) {{}}
            }}
            document.addEventListener("DOMContentLoaded", applyThemeSidebar);
            window.parent.document.addEventListener("themeChanged", applyThemeSidebar);
            </script>
            <style>
            body {{ margin: 0; padding: 0; background: transparent; }}
            #copy-btn-sidebar {{
                width: 100%;
                padding: 0.5rem 1rem;
                background-color: transparent;
                border-radius: 0.5rem;
                font-size: 1rem;
                line-height: 1.6;
                cursor: pointer;
                font-family: "Source Sans Pro", sans-serif;
                transition: border-color 0.2s, color 0.2s, opacity 0.2s;
                color: #FAFAFA;
                border: 1px solid rgba(128,128,128,0.5);
            }}
            @media (prefers-color-scheme: light) {{
                #copy-btn-sidebar {{ color: #31333F; }}
            }}
            </style>
            <button id="copy-btn-sidebar" onclick="copyToClipboardSidebar()">
                📋 Copiar Lista completa!
            </button>
            ''',
            height=60
        )
else:
    st.sidebar.info("A lista está vazia.")

st.sidebar.markdown("---")

st.sidebar.title("🔐 Área Restrita")
st.sidebar.caption("Acesso para Portaria e Anfitrião")

# A senha vem de variável de ambiente / st.secrets — nunca fica exposta no código.
# Configure ADMIN_PASSWORD no arquivo .env (local) ou em "Secrets" (Streamlit Cloud).
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or st.secrets.get("ADMIN_PASSWORD", None)

if not ADMIN_PASSWORD:
    st.sidebar.warning(
        "⚠️ Nenhuma senha de anfitrião configurada.\n\n"
        "Defina a variável de ambiente **ADMIN_PASSWORD** "
        "(ou em `.streamlit/secrets.toml`) antes de publicar o app."
    )
    is_admin = False
else:
    password_input = st.sidebar.text_input("Digite a Senha do Anfitrião:", type="password")
    is_admin = (password_input == ADMIN_PASSWORD)
    is_portaria = (password_input == "Antonio")
    if password_input and not is_admin and not is_portaria:
        st.sidebar.error("❌ Senha incorreta!")

# ==========================================
# NAVEGAÇÃO / ABA PRINCIPAL
# ==========================================
if is_admin:
    st.sidebar.success("✅ Acesso Liberado")
    mode = st.sidebar.radio("Navegação:", [
        "🎉 Cadastro de Convidados",
        "📋 Painel do Anfitrião / Portaria",
        "📷 Check-in por Câmera",
        "📊 Estatísticas",
        "🖼️ Mudar Foto da Festa",
        "⚙️ Configurações",
    ], key="nav_radio")
elif is_portaria:
    st.sidebar.success("✅ Portaria Liberada")
    if st.session_state.get("nav_radio") != "🚪 Check-in na Portaria":
        st.session_state["nav_radio"] = "🚪 Check-in na Portaria"
    mode = st.sidebar.radio("Navegação:", [
        "🚪 Check-in na Portaria",
    ], key="nav_radio")
else:
    mode = "🎉 Cadastro de Convidados"

# ==========================================
# 2. INTERFACE PÚBLICA DO CONVIDADO
# ==========================================
if mode == "🎉 Cadastro de Convidados":
    st.markdown(get_form_background_css(), unsafe_allow_html=True)

    with st.container(key="guest_page_card"):
        t_title = get_setting("guest_title", "Lista VIP")
        t_subtitle = get_setting("guest_subtitle", "Cole os nomes e receba os números!")
        
        st.markdown(f"<h1 style='text-align: center; font-size: 9em;'>{t_title}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 2em; font-weight: bold;'>{t_subtitle}</p>", unsafe_allow_html=True)

        if "pending_guests" in st.session_state and st.session_state["pending_guests"]:
            duplicates = st.session_state.get("duplicate_warnings", [])
            st.warning("⚠️ Atenção! O(s) convidado(s) a seguir já estão na lista:")
            for d in set(duplicates):
                st.write(f"- {d}")
            st.write("Deseja adicionar mesmo assim?")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Sim, adicionar mesmo assim", use_container_width=True, type="primary"):
                    registered = register_guests("Lista VIP", st.session_state["pending_guests"])
                    st.session_state["ticket_data"] = registered
                    st.session_state["ticket_responsible"] = "Lista VIP"
                    st.session_state["pending_guests"] = None
                    st.session_state["duplicate_warnings"] = None
                    st.session_state["form_nonce"] = st.session_state.get("form_nonce", 0) + 1
                    st.rerun()
            with c2:
                if st.button("❌ Não, cancelar", use_container_width=True):
                    st.session_state["pending_guests"] = None
                    st.session_state["duplicate_warnings"] = None
                    st.rerun()

        elif "ticket_data" in st.session_state and st.session_state["ticket_data"]:
            ticket = st.session_state["ticket_data"]
            responsible_name = st.session_state.get("ticket_responsible", "")

            t_success_title = get_setting("guest_success_title", "✅ INCLUSÃO CONFIRMADA!")
            st.success(t_success_title)
            
            text_lines = []
            for g in ticket:
                text_lines.append(f"{g['id']:03d} - {g['guest_name']}")
                
            list_text = "\n".join(text_lines)
            
            st.code(list_text, language="plaintext")

            if st.button(get_setting("guest_btn_another", "➕ Adicionar"), use_container_width=False):
                st.session_state["ticket_data"] = None
                st.session_state["ticket_responsible"] = None
                st.rerun()

        else:
            # Nota: os campos abaixo NÃO ficam dentro de um st.form, propositalmente.
            # Dentro de um st.form, os widgets só atualizam a tela depois do clique em
            # "Confirmar" — por isso as caixinhas de convidado não apareciam na hora
            # certa. Fora do form, a tela reage imediatamente.
            if "form_nonce" not in st.session_state:
                st.session_state["form_nonce"] = 0
            nonce = st.session_state["form_nonce"]

            st.subheader("📝 Formulário de Confirmação")

            t_question = get_setting("guest_question", "Cole os nomes. *")
            guests_text = st.text_area(
                t_question,
                placeholder="Cole os nomes (um por linha)...",
                key=f"guests_text_{nonce}"
            )
            guests_text = guests_text or ""

            t_btn_submit = get_setting("guest_btn_submit", "Incluir")
            
            c_btn1, c_space, c_btn2 = st.columns([2, 5, 2])
            with c_btn1:
                submitted = st.button(
                    t_btn_submit,
                    type="primary",
                    use_container_width=True
                )
            with c_btn2:
                if st.button("Consultar", use_container_width=True):
                    consultar_dialog()

            if submitted:
                import re
                def clean_name(text):
                    text = re.sub(r'\(.*?\)', '', text)
                    text = re.sub(r'\d+', '', text)
                    text = re.sub(r'[^\w\s]', '', text)
                    text = text.replace('_', '')
                    words = text.split()

                    return " ".join(w.capitalize() for w in words)

                raw_lines = guests_text.split('\n')
                guest_list = [clean_name(name) for name in raw_lines]
                guest_list = [name for name in guest_list if name]
                
                if not guest_list:
                    st.error("⚠️ Por favor, cole os nomes dos convidados!")
                else:
                    df_all = get_all_guests()
                    existing_names = set(df_all['guest_name'].str.lower()) if not df_all.empty else set()
                    duplicates = [name for name in guest_list if name.lower() in existing_names]
                    
                    if duplicates:
                        st.session_state["pending_guests"] = guest_list
                        st.session_state["duplicate_warnings"] = duplicates
                        st.rerun()
                    else:
                        registered = register_guests("Lista VIP", guest_list)
                        st.session_state["ticket_data"] = registered
                        st.session_state["ticket_responsible"] = "Lista VIP"
                        st.session_state["form_nonce"] = nonce + 1
                        st.rerun()

# ==========================================
# 3. PAINEL DO ANFITRIÃO / PORTARIA
# ==========================================
elif mode in ["📋 Painel do Anfitrião / Portaria", "🚪 Check-in na Portaria"]:
    st.title(mode)
    if mode == "📋 Painel do Anfitrião / Portaria":
        st.caption("Acesso administrativo para controle de entrada e geração de listas.")
    else:
        st.caption("Acesso para controle de entrada e check-in de convidados.")


    df_guests = get_all_guests()

    total_confirmed = len(df_guests)
    total_responsaveis = df_guests['main_guest'].nunique() if not df_guests.empty else 0
    total_arrived = len(df_guests[df_guests['checked_in'] == 1]) if not df_guests.empty else 0

    if total_responsaveis == 1:
        resp_value = "Gardila"
    else:
        resp_value = f"{total_responsaveis}"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Convidados", f"{total_confirmed}")
    col2.metric("Responsável", resp_value)
    col3.metric("✅ Já Chegaram", f"{total_arrived}")
    col4.metric("⏳ Faltam Chegar", f"{total_confirmed - total_arrived}")

    if total_confirmed > 0:
        st.progress(total_arrived / total_confirmed, text=f"{total_arrived} de {total_confirmed} já chegaram na festa")

    st.markdown("---")

    # -------------------------------------------------
    # Check-in na Portaria
    # -------------------------------------------------
    from st_keyup import st_keyup
    st.subheader("🚪 Check-in na Portaria")
    search_term = st_keyup(
        "Buscar por Nome ou por Número de Entrada (#ID):",
        placeholder="Digite nome ou número ex: 14 ou João...",
        key="checkin_search"
    )

    if not df_guests.empty:
        df_display = df_guests.copy()
        df_display['#ID'] = df_display['id'].apply(lambda x: f"#{x:03d}")

        results = df_display
        if search_term:
            term = search_term.strip().lower().replace('#', '')
            mask = (
                df_display['#ID'].str.lower().str.contains(term) |
                df_display['guest_name'].str.lower().str.contains(term) |
                df_display['main_guest'].str.lower().str.contains(term)
            )
            results = df_display[mask]

        if search_term and results.empty:
            st.info("Nenhum convidado encontrado com esse termo.")
        elif search_term:
            selected_to_checkin = []
            for _, row in results.iterrows():
                is_checked_in = (row['checked_in'] == 1)
                
                if is_checked_in:
                    val = st.checkbox(f"{row['#ID']} - {row['guest_name']} ✅ Já ENTROU", value=True, key=f"chk_{row['id']}")
                    if not val:
                        st.session_state[f"chk_{row['id']}"] = True
                        st.toast("O Convidado Já ENTROU!", icon="⚠️")
                        st.rerun()
                else:
                    val = st.checkbox(f"{row['#ID']} - {row['guest_name']}", value=False, key=f"chk_{row['id']}")
                    if val:
                        selected_to_checkin.append(row['id'])
                        
            if st.button("Salvar", type="primary"):
                if selected_to_checkin:
                    for cid in selected_to_checkin:
                        set_checked_in(cid, True)
                    st.success("✅ Check-in salvo com sucesso!")
                    st.rerun()
                else:
                    st.info("Nenhum novo convidado selecionado.")
        else:
            st.caption("Digite um nome ou número acima para fazer o check-in do convidado.")
    else:
        st.info("Nenhum convidado confirmado até o momento.")

    if mode == "📋 Painel do Anfitrião / Portaria":
        st.markdown("---")

        # -------------------------------------------------
        # Tabela completa
        # -------------------------------------------------
        st.subheader("🔍 Lista Completa")

        if not df_guests.empty:
            df_display = df_guests.copy()
            df_display['#ID'] = df_display['id'].apply(lambda x: f"#{x:03d}")
            df_display['Status'] = df_display['checked_in'].apply(lambda x: "✅ Chegou" if x == 1 else "⏳ Aguardando")

            df_show = df_display[['#ID', 'guest_name', 'main_guest', 'Status', 'created_at']].rename(columns={
                'guest_name': 'Nome do Convidado',
                'main_guest': 'Convidado de',
                'created_at': 'Data/Hora Confirmado'
            })

            st.dataframe(df_show, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇️ Baixar lista completa em Excel (.xlsx)",
                data=to_excel_bytes(df_guests),
                file_name="lista_de_presenca_festa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            t_header1 = get_setting("list_header1", "*LISTA VIP BOTTECO MUSIC*")
            t_header2 = get_setting("list_header2", "*Gardila / Marcelo / Jonas*")
            formatted_lines = [
                t_header1,
                f"*Sábado - {get_next_saturday_str()}*",
                t_header2,
                ""
            ]
            for idx, row in enumerate(df_guests.itertuples(), start=1):
                import re
                name_parts = re.sub(r'[^\w\s]', '', row.guest_name).split()

                clean_name = " ".join(w.capitalize() for w in name_parts)
                line = f"{row.id:03d} - {clean_name}"
                formatted_lines.append(line)
            import json
            formatted_text_json = json.dumps("\n".join(formatted_lines))

            import streamlit.components.v1 as components
            components.html(
                f"""
                <script>
                function copyToClipboard() {{
                    const text = {formatted_text_json};
                    navigator.clipboard.writeText(text).then(() => {{
                        const btn = document.getElementById('copy-btn');
                        btn.innerText = '✅ Copiado!';
                        setTimeout(() => {{ btn.innerText = '📋 Copiar Lista completa!'; }}, 2000);
                    }});
                }}
                
                function applyTheme() {{
                    try {{
                        const parentBody = window.parent.document.body;
                        const parentColor = window.parent.getComputedStyle(parentBody).color;
                        const btn = document.getElementById('copy-btn');
                        btn.style.color = parentColor;
                        btn.style.borderColor = parentColor;
                        btn.style.opacity = '0.7';
                        
                        btn.addEventListener('mouseover', () => {{
                            btn.style.borderColor = '#ff4b4b';
                            btn.style.color = '#ff4b4b';
                            btn.style.opacity = '1';
                        }});
                        btn.addEventListener('mouseout', () => {{
                            btn.style.borderColor = parentColor;
                            btn.style.color = parentColor;
                            btn.style.opacity = '0.7';
                        }});
                    }} catch(e) {{}}
                }}
                document.addEventListener("DOMContentLoaded", applyTheme);
                window.parent.document.addEventListener("themeChanged", applyTheme);
                </script>
                <style>
                body {{ margin: 0; padding: 0; background: transparent; }}
                #copy-btn {{
                    width: 100%;
                    padding: 0.5rem 1rem;
                    background-color: transparent;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    line-height: 1.6;
                    cursor: pointer;
                    font-family: "Source Sans Pro", sans-serif;
                    transition: border-color 0.2s, color 0.2s, opacity 0.2s;
                    color: #FAFAFA; /* fallback */
                    border: 1px solid rgba(128,128,128,0.5); /* fallback */
                }}
                @media (prefers-color-scheme: light) {{
                    #copy-btn {{ color: #31333F; }}
                }}
                </style>
                <button id="copy-btn" onclick="copyToClipboard()">
                    📋 Copiar Lista completa!
                </button>
                """,
                height=60
            )
        else:
            st.info("Nenhum convidado confirmado até o momento.")

        st.markdown("---")

        # -------------------------------------------------
        # Lista Formatada para WhatsApp
        # -------------------------------------------------
        st.subheader("📱 Lista Completa Formatada (Para WhatsApp)")
        st.markdown("Copie o texto abaixo e cole diretamente no seu grupo ou conversa do WhatsApp:")

        if not df_guests.empty:
            t_header1 = get_setting("list_header1", "*LISTA VIP BOTTECO MUSIC*")
            t_header2 = get_setting("list_header2", "*Gardila / Marcelo / Jonas*")
            formatted_lines = [
                t_header1,
                f"*Sábado - {get_next_saturday_str()}*",
                t_header2,
                ""
            ]
            for idx, row in enumerate(df_guests.itertuples(), start=1):
                line = f"{idx}. {row.guest_name}"
                formatted_lines.append(line)

            formatted_text = "\n".join(formatted_lines)

            st.text_area("Lista Pronta para Copiar:", value=formatted_text, height=250)

            with st.expander("Ver formato alternativo com Número de Entrada (#ID)"):
                t_header1 = get_setting("list_header1", "*LISTA VIP BOTTECO MUSIC*")
                t_header2 = get_setting("list_header2", "*Gardila / Marcelo / Jonas*")
                alt_lines = [
                    t_header1,
                    f"*Sábado - {get_next_saturday_str()}*",
                    t_header2,
                    ""
                ]
                for idx, row in enumerate(df_guests.itertuples(), start=1):
                    num_id = f"#{row.id:03d}"
                    line = f"{num_id} - {row.guest_name}"
                    alt_lines.append(line)
                st.text_area("Lista com #ID para WhatsApp:", value="\n".join(alt_lines), height=250)
        else:
            st.write("A lista está vazia.")

        st.markdown("---")

        # -------------------------------------------------
        # ZERAR LISTA
        # -------------------------------------------------
        st.subheader("⚠️ Reiniciar Banco de Dados para Próxima Festa")
        st.warning("Esta ação apagará **TODOS** os convidados da lista atual e reiniciará a numeração de entrada a partir do número #001.")

        confirm_reset = st.checkbox("Tenho certeza que desejo apagar a lista e reiniciar a numeração.")

        if st.button("🗑️ Zerar Lista para a Próxima Festa", type="primary", disabled=not confirm_reset):
            reset_db()
            st.success("✅ Lista zerada com sucesso! A próxima confirmação iniciará no #001.")
            st.rerun()

# ==========================================
# 4. CHECK-IN POR CÂMERA (LEITURA DE QR CODE)
# ==========================================
elif mode == "📷 Check-in por Câmera":
    st.title("📷 Check-in por Câmera")
    st.caption("Aponte a câmera para o QR Code do convidado e tire a foto para liberar a entrada automaticamente.")

    if "cam_scan_nonce" not in st.session_state:
        st.session_state["cam_scan_nonce"] = 0

    photo = st.camera_input(
        "Escanear QR Code",
        key=f"cam_input_{st.session_state['cam_scan_nonce']}",
        label_visibility="collapsed",
    )

    if photo is not None:
        payload = decode_qr_from_image_bytes(photo.getvalue())

        if payload == "ERRO_DEPENDENCIA":
            st.markdown(
                '<div class="scan-result-error">⚠️ Biblioteca de leitura de QR Code não está instalada. '
                'Rode: <code>pip install opencv-python-headless numpy</code></div>',
                unsafe_allow_html=True,
            )
        elif payload is None:
            st.markdown(
                '<div class="scan-result-warn">🔍 Nenhum QR Code encontrado na foto. '
                'Aproxime mais a câmera e tente novamente.</div>',
                unsafe_allow_html=True,
            )
        else:
            guest_id = guest_id_from_qr_payload(payload)
            if guest_id is None:
                st.markdown(
                    '<div class="scan-result-error">❌ Este QR Code não pertence a esta festa.</div>',
                    unsafe_allow_html=True,
                )
            else:
                guest_row = get_guest_by_id(guest_id)
                if guest_row is None:
                    st.markdown(
                        '<div class="scan-result-error">❌ Convidado não encontrado (ID inválido ou lista foi reiniciada).</div>',
                        unsafe_allow_html=True,
                    )
                elif guest_row["checked_in"] == 1:
                    horario_anterior = ""
                    if guest_row["checked_in_at"]:
                        try:
                            horario_anterior = f" às {str(guest_row['checked_in_at'])[-8:-3]}"
                        except Exception:
                            horario_anterior = ""
                    st.markdown(
                        f'<div class="scan-result-warn">🚫 QR Code JÁ UTILIZADO! '
                        f'<strong>{guest_row["guest_name"]}</strong> '
                        f'(#{guest_id:03d}) já entrou na festa{horario_anterior}. '
                        f'Este código não pode ser usado novamente.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    set_checked_in(guest_id, True)
                    st.markdown(
                        f'<div class="scan-result-ok">✅ Entrada liberada para <strong>{guest_row["guest_name"]}</strong> '
                        f'(#{guest_id:03d})!</div>',
                        unsafe_allow_html=True,
                    )
                    st.balloons()

        if st.button("📷 Escanear próximo convidado", type="primary", use_container_width=True):
            st.session_state["cam_scan_nonce"] += 1
            st.rerun()

    st.markdown("---")
    st.caption("Prefere digitar o nome ou número em vez de usar a câmera? Use a busca na aba **📋 Painel do Anfitrião / Portaria**.")

# ==========================================
# 5. ESTATÍSTICAS DA FESTA
# ==========================================
elif mode == "📊 Estatísticas":
    st.title("📊 Estatísticas da Festa")
    st.caption("Visão geral de confirmações, presença e faltas.")

    df_stats = get_all_guests()

    if df_stats.empty:
        st.info("Ainda não há convidados confirmados para gerar estatísticas.")
    else:
        total = len(df_stats)
        arrived = int((df_stats["checked_in"] == 1).sum())
        no_show = total - arrived
        total_responsaveis = df_stats["main_guest"].nunique()

        if total_responsaveis == 1:
            resp_display_stats = "Gardila"
        else:
            resp_display_stats = f"{total_responsaveis}"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Confirmados", total)
        col2.metric("✅ Compareceram", arrived, f"{(arrived/total*100):.0f}%")
        col3.metric("❌ Não Compareceram", no_show, f"{(no_show/total*100):.0f}%" if total else "0%")
        col4.metric("👤 Responsável", resp_display_stats)

        st.markdown("---")

        # -------------------------------------------------
        # Presença por responsável (quem convidou)
        # -------------------------------------------------
        st.subheader("👥 Presença por Responsável")
        presenca_resp = (
            df_stats.assign(Status=df_stats["checked_in"].map({1: "Compareceu", 0: "Faltou"}))
            .groupby(["main_guest", "Status"])
            .size()
            .reset_index(name="Quantidade")
            .pivot(index="main_guest", columns="Status", values="Quantidade")
            .fillna(0)
        )
        st.bar_chart(presenca_resp)

        st.markdown("---")

        # -------------------------------------------------
        # Linha do tempo de chegada
        # -------------------------------------------------
        st.subheader("⏱️ Fluxo de Chegada na Festa")
        arrived_df = df_stats[df_stats["checked_in"] == 1].copy()
        if not arrived_df.empty:
            arrived_df["checked_in_at"] = pd.to_datetime(arrived_df["checked_in_at"])
            arrived_df["Faixa (15 min)"] = arrived_df["checked_in_at"].dt.floor("15min").dt.strftime("%H:%M")
            timeline = arrived_df.groupby("Faixa (15 min)").size().reset_index(name="Chegadas")
            timeline = timeline.set_index("Faixa (15 min)")
            st.bar_chart(timeline)

            primeira = arrived_df["checked_in_at"].min().strftime("%H:%M:%S")
            ultima = arrived_df["checked_in_at"].max().strftime("%H:%M:%S")
            c1, c2 = st.columns(2)
            c1.metric("🥇 Primeira Chegada", primeira)
            c2.metric("🕐 Última Chegada", ultima)
        else:
            st.caption("Ninguém fez check-in ainda — o gráfico de fluxo aparece assim que a primeira pessoa chegar.")

        st.markdown("---")

        # -------------------------------------------------
        # Ranking de responsáveis que mais trouxeram convidados
        # -------------------------------------------------
        st.subheader("🏆 Ranking — Quem Mais Trouxe Convidados")
        ranking = (
            df_stats.groupby("main_guest")
            .size()
            .reset_index(name="Convidados")
            .sort_values("Convidados", ascending=False)
        )
        if not ranking.empty:
            st.dataframe(ranking.rename(columns={"main_guest": "Responsável"}), use_container_width=True, hide_index=True)
        else:
            st.caption("Ainda não há convidados cadastrados.")

        st.markdown("---")

        # -------------------------------------------------
        # Lista de quem confirmou e não compareceu (no-show)
        # -------------------------------------------------
        st.subheader("🚫 Confirmaram e Não Compareceram")
        faltantes = df_stats[df_stats["checked_in"] == 0].copy()
        if not faltantes.empty:
            faltantes_show = faltantes.copy()
            faltantes_show["#ID"] = faltantes_show["id"].apply(lambda x: f"#{x:03d}")
            faltantes_show = faltantes_show[["#ID", "guest_name", "main_guest"]].rename(columns={
                "guest_name": "Nome",
                "main_guest": "Convidado de",
            })
            st.dataframe(faltantes_show, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Baixar lista de faltantes (.xlsx)",
                data=to_excel_bytes(faltantes),
                file_name="faltantes_festa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.success("🎉 Todo mundo que confirmou já chegou!")

# ==========================================
# 6. TROCAR FOTO DA FESTA
# ==========================================
elif mode == "🖼️ Mudar Foto da Festa":
    st.title("🖼️ Mudar Foto da Festa")
    st.caption(
        "Escolha uma nova imagem para o fundo do formulário. Funciona tanto "
        "escolhendo da galeria do celular quanto do explorador de arquivos "
        "do computador — o campo abaixo já abre a opção certa automaticamente "
        "dependendo do aparelho."
    )

    # Mostra a imagem atual (se existir) para referência antes de trocar.
    padroes_atuais = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    arquivos_atuais = []
    if os.path.isdir(FUNDO_FESTA_DIR):
        for padrao in padroes_atuais:
            arquivos_atuais.extend(glob.glob(os.path.join(FUNDO_FESTA_DIR, padrao)))

    if arquivos_atuais:
        st.markdown("**Foto atual:**")
        st.image(sorted(arquivos_atuais)[0], use_container_width=True)
    else:
        st.info("Nenhuma foto de fundo definida ainda.")

    st.markdown("---")

    nova_foto = st.file_uploader(
        "Escolher nova foto da festa",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=False,
        help="No celular, isso abre a opção de escolher da galeria ou tirar foto. No computador, abre o explorador de arquivos do Windows/Mac.",
    )

    if nova_foto is not None:
        st.markdown("**Pré-visualização:**")
        st.image(nova_foto, use_container_width=True)

        if st.button("✅ Usar esta foto como novo fundo", type="primary", use_container_width=True):
            os.makedirs(FUNDO_FESTA_DIR, exist_ok=True)

            # Remove qualquer imagem antiga da pasta (só pode ter UMA por
            # vez, conforme a regra do get_form_background_css).
            for arquivo_antigo in arquivos_atuais:
                try:
                    os.remove(arquivo_antigo)
                except OSError:
                    pass

            ext = os.path.splitext(nova_foto.name)[1].lower() or ".png"
            destino = os.path.join(FUNDO_FESTA_DIR, f"fundo{ext}")
            with open(destino, "wb") as f:
                f.write(nova_foto.getbuffer())

            st.success("✅ Foto da festa atualizada com sucesso!")
            st.rerun()

# ==========================================
# 7. CONFIGURAÇÕES
# ==========================================
elif mode == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    st.caption("Ajuste as configurações gerais do aplicativo, incluindo textos e tamanho das fontes.")

    tab_textos, tab_fontes = st.tabs(["📝 Textos da Tela de Convidado", "🔤 Tamanhos da Fonte"])

    with tab_textos:
        st.subheader("📝 Personalização de Textos")
        st.caption("Altere os textos exibidos na tela pública do convidado.")
        
        with st.form("form_textos"):
            # Valores atuais (ou default)
            t_title = get_setting("guest_title", "Lista VIP")
            t_subtitle = get_setting("guest_subtitle", "Cole os nomes e receba os números!")
            t_btn_submit = get_setting("guest_btn_submit", "Incluir")
            t_success_title = get_setting("guest_success_title", "✅ INCLUSÃO CONFIRMADA!")
            t_btn_another = get_setting("guest_btn_another", "➕ Adicionar")
            t_question = get_setting("guest_question", "Cole os nomes. *")

            new_title = st.text_input("Título Principal", value=t_title)
            new_subtitle = st.text_input("Subtítulo", value=t_subtitle)
            new_btn_submit = st.text_input("Texto do Botão 'Confirmar Presença'", value=t_btn_submit)
            
            st.markdown("---")
            st.subheader("📝 Cabeçalho das Listas VIP")
            t_header1 = get_setting("list_header1", "*LISTA VIP BOTTECO MUSIC*")
            t_header2 = get_setting("list_header2", "*Gardila / Marcelo / Jonas*")
            new_header1 = st.text_input("Linha 1 do Cabeçalho", value=t_header1)
            new_header2 = st.text_input("Linha 2 do Cabeçalho", value=t_header2)
            new_success_title = st.text_input("Título de Sucesso", value=t_success_title)
            new_btn_another = st.text_input("Texto do Botão 'Nova Confirmação'", value=t_btn_another)
            new_question = st.text_input("Texto da Pergunta 'Cole os nomes.'", value=t_question)

            if st.form_submit_button("Salvar Textos"):
                set_setting("guest_title", new_title)
                set_setting("guest_subtitle", new_subtitle)
                set_setting("guest_btn_submit", new_btn_submit)
                set_setting("list_header1", new_header1)
                set_setting("list_header2", new_header2)
                set_setting("guest_success_title", new_success_title)
                set_setting("guest_btn_another", new_btn_another)
                set_setting("guest_question", new_question)
                st.success("✅ Textos atualizados com sucesso!")
                st.rerun()

    with tab_fontes:
        st.subheader("🔤 Tamanhos da Fonte")
        opcao_fonte = st.radio(
            "O que você quer ajustar?",
            [
                "🔐 Fonte da Área Restrita",
                "🎟️ Fonte do Convidado (Confirmar Presença)",
            ],
            key="radio_font"
        )

        st.markdown("---")

        if opcao_fonte == "🔐 Fonte da Área Restrita":
            st.subheader("🔐 Fonte da Área Restrita")
            st.caption(
                "Controla o tamanho do texto da barra lateral e todas as telas administrativas."
            )
            novo_tamanho = st.slider(
                "Tamanho da fonte (px):",
                min_value=10, max_value=32,
                value=_admin_font_size,
                step=1,
                key="slider_admin_font",
            )
            if novo_tamanho != _admin_font_size:
                set_setting(ADMIN_FONT_SIZE_KEY, novo_tamanho)
                st.rerun()
            st.success(f"✅ Fonte atual: {_admin_font_size}px")

        else:
            st.subheader("🎟️ Fonte do Convidado (Confirmar Presença)")
            st.caption(
                "Controla o tamanho do texto da tela pública."
            )
            novo_tamanho = st.slider(
                "Tamanho da fonte (px):",
                min_value=10, max_value=32,
                value=_guest_font_size,
                step=1,
                key="slider_guest_font",
            )
            if novo_tamanho != _guest_font_size:
                set_setting(GUEST_FONT_SIZE_KEY, novo_tamanho)
                st.rerun()
            st.success(f"✅ Fonte atual: {_guest_font_size}px")
