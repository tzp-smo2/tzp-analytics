import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Analyse dynamique SmO2 et Puissance")

    data_file = st.file_uploader("Importer un fichier Excel de test (.xlsx)", type=["xlsx"])
    if data_file:
        df = pd.read_excel(data_file)
        df = df.rename(columns={
            "Time[s]": "Temps",
            "SmO2[%]": "SmO2",
            "Power -  2[W]": "Puissance"
        })

        df["Temps"] = pd.to_numeric(df["Temps"], errors="coerce")
        df["SmO2"] = pd.to_numeric(df["SmO2"], errors="coerce")
        df["Puissance"] = pd.to_numeric(df["Puissance"], errors="coerce")
        df = df.dropna(subset=["Temps", "SmO2", "Puissance"])

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df["Temps"], df["SmO2"], color='blue', label="SmO2")
        ax1.set_xlabel("Temps (s)")
        ax1.set_ylabel("SmO2 (%)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(df["Temps"], df["Puissance"], color='red', linestyle='--', label="Puissance")
        ax2.set_ylabel("Puissance (W)", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        fig.tight_layout()
        st.pyplot(fig)
