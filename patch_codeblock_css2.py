with open('app.py', 'r') as f:
    content = f.read()

old_css = """    /* Corrige a cor da caixa de texto (código) após a inclusão */
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"],
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] code,
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] span,
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] pre {
        color: #31333F !important;
    }
    
    @media (prefers-color-scheme: dark) {
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"],
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] code,
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] span,
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] pre {
            color: #FAFAFA !important;
        }
    }"""

new_css = """    /* Corrige a cor da caixa de texto (código) após a inclusão */
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"],
    div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] * {
        color: #31333F !important;
        text-shadow: none !important;
    }
    
    @media (prefers-color-scheme: dark) {
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"],
        div[class*="st-key-guest_page_card"] [data-testid="stCodeBlock"] * {
            color: #FAFAFA !important;
        }
    }"""

if old_css in content:
    content = content.replace(old_css, new_css)
    with open('app.py', 'w') as f:
        f.write(content)
    print("Replaced CSS")
else:
    print("CSS not found")
