
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.title("Analyse All-Out 30s : SmO₂ + Puissance – Durées, Fatigue et T½ Réoxygénation")

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

        # T½ réoxygénation
        sm_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]["SmO2"]
        sm_min = sm_30s.min()
        seuil_moitié = sm_min + (sm_max - sm_min) / 2

        try:
            t_recovery = df[(df["Temps"] > 30) & (df["SmO2"] >= seuil_moitié)]["Temps"].iloc[0]
            t_half = round(t_recovery - 30, 2)
            t_half_abs = t_recovery
        except:
            t_half = None
            t_half_abs = None

        # Affichage graphique
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df["Temps"], df["SmO2"], label="SmO₂ (%)", color='blue')
        ax2 = ax1.twinx()
        ax2.plot(df["Temps"], df["Puissance"], label="Puissance (W)", color='red', linestyle='--')

        ax1.axvspan(0, t1, color='lightgreen', alpha=0.3, label='Zone T1 (vert)')
        ax1.axvspan(t1, t2, color='khaki', alpha=0.3, label='Zone T2 (jaune)')
        ax1.axvspan(t2, 30, color='lightcoral', alpha=0.3, label='Zone T3 (rouge)')
        ax1.axvspan(30, max_time, color='lightblue', alpha=0.3, label='Zone T4 (récup.)')

        ax1.plot(max_time, sm_max, 'o', color='blue', label=f"SmO₂ max ({sm_max:.1f}%)")
        ax1.plot(df["Temps"][sm_30s.idxmin()], sm_min, 'o', color='black', label=f"SmO₂ min ({sm_min:.1f}%)")

        if t_half_abs is not None:
            ax1.plot(t_half_abs, seuil_moitié, 'o', color='purple', label=f"T½ réox ({t_half:.2f}s)")

        ax1.set_xlabel("Temps (s)")
        ax1.set_ylabel("SmO₂ (%)")
        ax2.set_ylabel("Puissance (W)")

        # Ajouter les légendes combinées
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

        fig.tight_layout()
        st.pyplot(fig)

        # Calculs
        st.subheader("📊 Résultats")

        df_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]
        p_30s = df_30s["Puissance"]

        p_0_10 = df_30s[df_30s["Temps"] < 10]["Puissance"]
        p_10_20 = df_30s[(df_30s["Temps"] >= 10) & (df_30s["Temps"] < 20)]["Puissance"]
        p_20_30 = df_30s[(df_30s["Temps"] >= 20)]["Puissance"]

        # Calcul Pmax et Pmin après Pmax
        idx_pmax = p_30s.idxmax()
        p_max = p_30s.max()
        p_apres_pmax = df[(df.index >= idx_pmax) & (df["Temps"] <= 30)]["Puissance"]
        p_min_apres_pmax = p_apres_pmax.min()

        if p_max > 0 and p_min_apres_pmax > 0:
            fatigue_index = round(100 * (p_max - p_min_apres_pmax) / p_max, 1)
        else:
            fatigue_index = None

        # Durées des zones
        duree_t1 = round(t1, 1)
        duree_t2 = round(t2 - t1, 1)
        duree_t3 = round(30 - t2, 1)
        duree_t4 = round(max_time - 30, 1)

        resultats = [
            ["Puissance max", "0–10s", p_0_10.max()],
            ["Puissance max", "10–20s", p_10_20.max()],
            ["Puissance max", "20–30s", p_20_30.max()],
            ["Puissance max", "0–30s", p_max],

            ["Puissance moyenne", "0–10s", p_0_10.mean()],
            ["Puissance moyenne", "10–20s", p_10_20.mean()],
            ["Puissance moyenne", "20–30s", p_20_30.mean()],
            ["Puissance moyenne", "0–30s", p_30s.mean()],

            ["Puissance min après Pmax", "0–30s", p_min_apres_pmax],

            ["SmO₂ min", "0–30s", sm_min],
            ["SmO₂ max", "post-30s", sm_max],
            ["Temps SmO₂ max", "post-30s", max_time],

            ["Durée zone verte (T1)", "s", duree_t1],
            ["Durée zone jaune (T2)", "s", duree_t2],
            ["Durée zone rouge (T3)", "s", duree_t3],
            ["Durée récupération (T4)", "s", duree_t4],

            ["T½ réoxygénation", "s", t_half],
            ["Indice de fatigue", "%", fatigue_index]
        ]

        result_df = pd.DataFrame(resultats, columns=["Type", "Intervalle", "Valeur"])
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Télécharger les résultats (CSV)", data=csv, file_name="wingate_resultats.csv", mime="text/csv")

if __name__ == "__main__":
    main()
