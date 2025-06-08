import streamlit as st
import importlib

st.set_page_config(page_title="TZP Analyse", layout="wide")

st.image("logo_tzp.png", width=80)
st.title("Training Zone Performance – Outils d'analyse")

sport = st.selectbox("Choisissez votre sport :", ["Cyclisme"])

tests = {
    "Cyclisme": {
        "Test all-out 30s (Wingate)": "pages.Cyclisme.Test_Wingate",
        "Test d'effort dynamique (SmO₂)": "pages.Cyclisme.Test_Smo2_Dynamique"
    }
}

test = st.selectbox("Choisissez le test :", list(tests[sport].keys()))

module_name = tests[sport][test]
module = importlib.import_module(module_name)
if hasattr(module, "main"):
    module.main()
else:
    st.warning("Ce test ne contient pas de fonction `main()` à exécuter.")
