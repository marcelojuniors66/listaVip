import streamlit as st

st.markdown("""
<style>
    .mycard p, .mycard span {
        color: red !important;
    }
    .mycard [data-testid="stCodeBlock"] span {
        color: unset !important;
    }
</style>
<div class="mycard">
""", unsafe_allow_html=True)

st.code("001 - Marcelo")

st.markdown("</div>", unsafe_allow_html=True)
