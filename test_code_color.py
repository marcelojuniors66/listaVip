import streamlit as st

st.markdown("""
<style>
    .mycard p, .mycard span {
        color: red !important;
    }
    .mycard [data-testid="stCodeBlock"],
    .mycard [data-testid="stCodeBlock"] code,
    .mycard [data-testid="stCodeBlock"] span,
    .mycard [data-testid="stCodeBlock"] p,
    .mycard [data-testid="stCodeBlock"] div,
    .mycard [data-testid="stCodeBlock"] pre,
    .mycard [data-testid="stCodeBlock"] * {
        color: blue !important;
    }
</style>
<div class="mycard">
""", unsafe_allow_html=True)

st.code("001 - Marcelo\n002 - Ela\n003 - Nos", language="text")

st.markdown("</div>", unsafe_allow_html=True)
