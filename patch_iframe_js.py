with open('app.py', 'r') as f:
    content = f.read()

old_str = """                <script>
                function copyToClipboard() {{
                    const text = {formatted_text_json};
                    navigator.clipboard.writeText(text).then(() => {{
                        const btn = document.getElementById('copy-btn');
                        btn.innerText = '✅ Copiado!';
                        setTimeout(() => {{ btn.innerText = '📋 Copiar Lista completa!'; }}, 2000);
                    }});
                }}
                </script>
                <style>
                body {{ margin: 0; padding: 0; background: transparent; }}
                #copy-btn {{
                    width: 100%;
                    padding: 0.5rem 1rem;
                    background-color: transparent;
                    color: #FAFAFA;
                    border: 1px solid rgba(250, 250, 250, 0.2);
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    line-height: 1.6;
                    cursor: pointer;
                    font-family: "Source Sans Pro", sans-serif;
                    transition: border-color 0.2s, color 0.2s;
                }}
                @media (prefers-color-scheme: light) {{
                    #copy-btn {{
                        color: #31333F;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                    }}
                }}
                #copy-btn:hover {{
                    border-color: #ff4b4b;
                    color: #ff4b4b;
                }}
                </style>"""

new_str = """                <script>
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
                </style>"""

if old_str in content:
    content = content.replace(old_str, new_str)
    with open('app.py', 'w') as f:
        f.write(content)
    print("Replaced exact string!")
else:
    print("Exact string not found. Trying regex fallback.")
