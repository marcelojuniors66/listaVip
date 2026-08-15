import streamlit as st

st.markdown("""
<style>
    .mycard p, .mycard span {
        color: #f8fafc !important;
    }
    .mycard [data-testid="stCodeBlock"],
    .mycard [data-testid="stCodeBlock"] * {
        color: unset !important;
    }
</style>
<div class="mycard">
""", unsafe_allow_html=True)

st.code("001 - Marcelo\n002 - Ela\n003 - Nos", language="text")

st.markdown("</div>", unsafe_allow_html=True)
