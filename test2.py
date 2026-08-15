import streamlit as st
import streamlit.components.v1 as components

components.html("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        try {
            const parentColor = window.parent.getComputedStyle(window.parent.document.body).color;
            document.body.style.color = parentColor;
            document.getElementById('mybtn').style.color = parentColor;
        } catch (e) {}
    });
    </script>
    <button id="mybtn">Test Button</button>
""")
