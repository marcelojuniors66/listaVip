with open('app.py', 'r') as f:
    content = f.read()

content = content.replace('st.code(list_text, language="text")', 'st.code(list_text, language="plaintext")')

with open('app.py', 'w') as f:
    f.write(content)
print("Language changed to plaintext")
