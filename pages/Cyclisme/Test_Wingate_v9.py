
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.title("Analyse All-Out 30s : Puissance + SmO₂ – Intégration physiologique et mécanique")

    data_file = st.file_uploader("📂 Charger votre fichier .xlsx", type=["xlsx"])
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

        st.subheader("🎯 Zones d'effort")
        t1 = st.slider("Début de T2 (s)", 1, 15, 3)
        t2 = st.slider("Début de T3 (s)", t1 + 1, 25, 10)

        smo2_rec = df[df["Temps"] > 30]
        sm_max = smo2_rec["SmO2"].max()
        try:
            max_time = float(smo2_rec[smo2_rec["SmO2"] == sm_max]["Temps"].values[0])
        except:
            max_time = 31.0

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

        df_reox = df[(df["Temps"] >= 30) & (df["Temps"] <= 45)]
        if len(df_reox) >= 2:
            coeffs = np.polyfit(df_reox["Temps"], df_reox["SmO2"], 1)
            pente_reox = round(coeffs[0], 2)
            reox_fit = np.poly1d(coeffs)
            x_fit = np.linspace(30, 45, 100)
            y_fit = reox_fit(x_fit)
        else:
            pente_reox = None
            x_fit, y_fit = [], []

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(df["Temps"], df["SmO2"], label="SmO₂ (%)", color='blue')
        ax2 = ax1.twinx()
        ax2.plot(df["Temps"], df["Puissance"], label="Puissance (W)", color='red', linestyle='--')

        ax1.axvspan(0, t1, color='lightgreen', alpha=0.3, label='Zone T1')
        ax1.axvspan(t1, t2, color='khaki', alpha=0.3, label='Zone T2')
        ax1.axvspan(t2, 30, color='lightcoral', alpha=0.3, label='Zone T3')
        ax1.axvspan(30, max_time, color='lightblue', alpha=0.3, label='Zone T4')

        ax1.plot(max_time, sm_max, 'o', color='blue', label=f"SmO₂ max ({sm_max:.1f}%)")
        ax1.plot(df["Temps"][sm_30s.idxmin()], sm_min, 'o', color='black', label=f"SmO₂ min ({sm_min:.1f}%)")
        if t_half_abs is not None:
            ax1.plot(t_half_abs, seuil_moitié, 'o', color='purple', label=f"T½ réox ({t_half:.2f}s)")
        if len(x_fit) > 0:
            ax1.plot(x_fit, y_fit, '--', color='green', label="Pente réox (30–45s)")

        ax1.set_xlabel("Temps (s)")
        ax1.set_ylabel("SmO₂ (%)")
        ax2.set_ylabel("Puissance (W)")
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
        fig.tight_layout()
        st.pyplot(fig)

        st.subheader("📊 Résultats")

        df_30s = df[(df["Temps"] >= 0) & (df["Temps"] <= 30)]
        p_30s = df_30s["Puissance"]
        p_0_10 = df_30s[df_30s["Temps"] < 10]["Puissance"]
        p_10_20 = df_30s[(df_30s["Temps"] >= 10) & (df_30s["Temps"] < 20)]["Puissance"]
        p_20_30 = df_30s[(df_30s["Temps"] >= 20)]["Puissance"]

        idx_pmax = p_30s.idxmax()
        p_max = p_30s.max()
        p_apres_pmax = df[(df.index >= idx_pmax) & (df["Temps"] <= 30)]["Puissance"]
        p_min_apres_pmax = p_apres_pmax.min()

        if p_max > 0 and p_min_apres_pmax > 0:
            fatigue_index = round(100 * (p_max - p_min_apres_pmax) / p_max, 1)
        else:
            fatigue_index = None

        amplitude_puissance = p_max - p_min_apres_pmax
        amplitude_smo2 = sm_max - sm_min
        ratio_smo2_puissance = round(amplitude_smo2 / amplitude_puissance, 3) if amplitude_puissance > 0 else None

        bloc_meca = [
            ["Puissance max (0–30s)", p_max],
            ["Puissance min après Pmax", p_min_apres_pmax],
            ["Amplitude puissance", amplitude_puissance],
            ["Puissance moyenne (0–30s)", p_30s.mean()]
        ]
        bloc_smo2 = [
            ["SmO₂ min", sm_min],
            ["SmO₂ max", sm_max],
            ["Amplitude SmO₂", amplitude_smo2],
            ["T½ réoxygénation (s)", t_half],
            ["Pente réox (30–45s) (%/s)", pente_reox]
        ]
        bloc_synthese = [
            ["Indice de fatigue (%)", fatigue_index],
            ["Ratio amplitude SmO₂ / puissance", ratio_smo2_puissance]
        ]

        st.markdown("### ⚙️ Données mécaniques (puissance)")
        st.dataframe(pd.DataFrame(bloc_meca, columns=["Variable", "Valeur"]))

        st.markdown("### 🧬 Données physiologiques (SmO₂)")
        st.dataframe(pd.DataFrame(bloc_smo2, columns=["Variable", "Valeur"]))

        st.markdown("### 🔀 Indicateurs croisés")
        st.dataframe(pd.DataFrame(bloc_synthese, columns=["Variable", "Valeur"]))

if __name__ == "__main__":
    main()
