import streamlit as st
import streamlit.components.v1 as components

components.html("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        try {
            const parentColor = window.parent.getComputedStyle(window.parent.document.body).color;
            const parentBg = window.parent.getComputedStyle(window.parent.document.body).backgroundColor;
            const btn = document.getElementById('mybtn');
            btn.style.color = parentColor;
            btn.style.borderColor = parentColor;
            btn.innerText = 'Color: ' + parentColor + ' | ' + parentBg;
        } catch (e) {
            document.getElementById('mybtn').innerText = 'Error: ' + e.message;
        }
    });
    </script>
    <button id="mybtn" style="background: transparent; border: 1px solid black; padding: 10px;">Test Button</button>
""")
