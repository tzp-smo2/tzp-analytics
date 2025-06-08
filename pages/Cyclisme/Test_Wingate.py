import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Analyse All-Out 30s : SmO2 + Puissance – Corrigé Fatigue Index")

    data_file = st.file_uploader("Charger votre fichier .xlsx", type=["xlsx"])
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

        st.subheader("Définition des zones d'effort")
        t1 = st.slider("Début de T2 (s)", 1, 15, 3)
        t2 = st.slider("Début de T3 (s)", t1 + 1, 25, 10)

        smo2_rec = df[df["Temps"] > 30]
        sm_max = smo2_rec["SmO2"].max()
        try:
            max_time = float(smo2_rec[smo2_rec["SmO2"] == sm_max]["Temps"].values[0])
        except:
            max_time = 31.0

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df["Temps"], df["SmO2"], label="SmO2", color='blue')
        ax2 = ax1.twinx()
        ax2.plot(df["Temps"], df["Puissance"], label="Puissance", color='red', linestyle='--')

        ax1.axvspan(0, t1, color='lightgreen', alpha=0.3, label='T1')
        ax1.axvspan(t1, t2, color='khaki', alpha=0.3, label='T2')
        ax1.axvspan(t2, 30, color='lightcoral', alpha=0.3, label='T3')
        ax1.axvspan(30, max_time, color='lightblue', alpha=0.3, label='T4 (recovery)')
        ax1.plot(max_time, sm_max, 'o', color='blue', label="SmO2 max")

        ax1.set_xlabel("Temps (s)")
        ax1.set_ylabel("SmO2 (%)")
        ax2.set_ylabel("Puissance (W)")

        fig.tight_layout()
        st.pyplot(fig)

        st.subheader("📊 Résultats")

        p_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]["Puissance"]
        sm_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]["SmO2"]

        p_0_10 = df[(df["Temps"] >= 0) & (df["Temps"] < 10)]["Puissance"]
        p_10_20 = df[(df["Temps"] >= 10) & (df["Temps"] < 20)]["Puissance"]
        p_20_30 = df[(df["Temps"] >= 20) & (df["Temps"] <= 30)]["Puissance"]

        p_max_0_10 = p_0_10.max()
        p_min_0_30 = p_30s.min()
        fatigue_index = 100 * (p_max_0_10 - p_min_0_30) / p_max_0_10 if p_max_0_10 > 0 else None

        resultats = {
            "Puissance max (0-10s) (W)": p_max_0_10,
            "Puissance moyenne (0-10s) (W)": p_0_10.mean(),
            "Puissance max (10-20s) (W)": p_10_20.max(),
            "Puissance moyenne (10-20s) (W)": p_10_20.mean(),
            "Puissance max (20-30s) (W)": p_20_30.max(),
            "Puissance moyenne (20-30s) (W)": p_20_30.mean(),
            "Puissance max (W)": p_30s.max(),
            "Puissance moyenne (W)": p_30s.mean(),
            "Puissance min (W)": p_min_0_30,
            "SmO₂ min (%)": sm_30s.min(),
            "SmO₂ max après 30s (%)": sm_max,
            "Temps du SmO₂ max (s)": max_time,
            "Indice de fatigue (%)": fatigue_index
        }

        result_df = pd.DataFrame.from_dict(resultats, orient='index', columns=["Valeur"])
        st.dataframe(result_df)

        csv = result_df.to_csv().encode('utf-8')
        st.download_button("💾 Télécharger les résultats (CSV)", data=csv, file_name="wingate_resultats.csv", mime="text/csv")
