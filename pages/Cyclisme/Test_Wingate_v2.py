
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Analyse All-Out 30s : SmO₂ + Puissance – Indice corrigé et affichage structuré")

    data_file = st.file_uploader("📂 Charger votre fichier .xlsx", type=["xlsx"])
    if data_file:
        # Chargement et renommage des colonnes
        df = pd.read_excel(data_file)
        df = df.rename(columns={
            "Time[s]": "Temps",
            "SmO2[%]": "SmO2",
            "Power -  2[W]": "Puissance"
        })

        # Nettoyage des données
        df["Temps"] = pd.to_numeric(df["Temps"], errors="coerce")
        df["SmO2"] = pd.to_numeric(df["SmO2"], errors="coerce")
        df["Puissance"] = pd.to_numeric(df["Puissance"], errors="coerce")
        df = df.dropna(subset=["Temps", "SmO2", "Puissance"])

        # Sélection manuelle des zones
        st.subheader("🎯 Définition des zones d'effort")
        t1 = st.slider("Début de T2 (s)", 1, 15, 3)
        t2 = st.slider("Début de T3 (s)", t1 + 1, 25, 10)

        # Recherche du SmO2 max post-effort
        smo2_rec = df[df["Temps"] > 30]
        sm_max = smo2_rec["SmO2"].max()
        try:
            max_time = float(smo2_rec[smo2_rec["SmO2"] == sm_max]["Temps"].values[0])
        except:
            max_time = 31.0

        # Affichage graphique
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df["Temps"], df["SmO2"], label="SmO2", color='blue')
        ax2 = ax1.twinx()
        ax2.plot(df["Temps"], df["Puissance"], label="Puissance", color='red', linestyle='--')

        ax1.axvspan(0, t1, color='lightgreen', alpha=0.3, label='T1')
        ax1.axvspan(t1, t2, color='khaki', alpha=0.3, label='T2')
        ax1.axvspan(t2, 30, color='lightcoral', alpha=0.3, label='T3')
        ax1.axvspan(30, max_time, color='lightblue', alpha=0.3, label='T4 (récupération)')
        ax1.plot(max_time, sm_max, 'o', color='blue', label="SmO2 max")

        ax1.set_xlabel("Temps (s)")
        ax1.set_ylabel("SmO2 (%)")
        ax2.set_ylabel("Puissance (W)")
        fig.tight_layout()
        st.pyplot(fig)

        # Calculs
        st.subheader("📊 Résultats")

        p_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]["Puissance"]
        sm_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]["SmO2"]

        p_0_10 = df[(df["Temps"] >= 0) & (df["Temps"] < 10)]["Puissance"]
        p_10_20 = df[(df["Temps"] >= 10) & (df["Temps"] < 20)]["Puissance"]
        p_20_30 = df[(df["Temps"] >= 20) & (df["Temps"] <= 30)]["Puissance"]

        p_max_0_10 = p_0_10.max()
        p_min_0_30 = p_30s.min()

        if p_max_0_10 > 0 and p_min_0_30 > 0:
            fatigue_index = round(100 * (p_max_0_10 - p_min_0_30) / p_max_0_10, 1)
        else:
            fatigue_index = None

        resultats = [
            ["Puissance max", "0–10s", p_max_0_10],
            ["Puissance max", "10–20s", p_10_20.max()],
            ["Puissance max", "20–30s", p_20_30.max()],
            ["Puissance max", "0–30s", p_30s.max()],

            ["Puissance moyenne", "0–10s", p_0_10.mean()],
            ["Puissance moyenne", "10–20s", p_10_20.mean()],
            ["Puissance moyenne", "20–30s", p_20_30.mean()],
            ["Puissance moyenne", "0–30s", p_30s.mean()],

            ["Puissance min", "0–30s", p_min_0_30],

            ["SmO2 min", "0–30s", sm_30s.min()],
            ["SmO2 max", "post-30s", sm_max],
            ["Temps SmO₂ max", "post-30s", max_time],

            ["Indice de fatigue", "%", fatigue_index]
        ]

        result_df = pd.DataFrame(resultats, columns=["Type", "Intervalle", "Valeur"])
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Télécharger les résultats (CSV)", data=csv, file_name="wingate_resultats.csv", mime="text/csv")

if __name__ == "__main__":
    main()
