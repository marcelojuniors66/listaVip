with open('app.py', 'r') as f:
    content = f.read()

old_sidebar = """# ==========================================
LOGO_PATH = os.path.join("logo", "logo_botteco_transparent.png")
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)

st.sidebar.title("🔐 Área Restrita")"""

new_sidebar = """# ==========================================
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
        line = f"{idx}. {row.guest_name} (Convidado de {row.main_guest})"
        formatted_lines_sidebar.append(line)
    
    import json
    formatted_text_json_sidebar = json.dumps("\\n".join(formatted_lines_sidebar))
    
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

st.sidebar.title("🔐 Área Restrita")"""

if old_sidebar in content:
    content = content.replace(old_sidebar, new_sidebar)
    with open('app.py', 'w') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Not found.")
