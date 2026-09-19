# Bloque 1
import pandas as pd
import numpy as np
from scipy import stats

# 📂 Leer archivo Excel
df = pd.read_excel("resumen_biomasa_carbono_depositos.xlsx", sheet_name="Hoja1")

# Bloque 2
# 🔍 Columnas de biomasa (t/ha) y carbono (tC/ha) — SIN los totales
cols_biomasa = ["AGB_t_ha", "BGB_t_ha", "DTC_t_ha", "DMC_t_ha", "FLB_t_ha"]
cols_carbono = ["AGB_tC_ha", "BGB_tC_ha", "DTC_tC_ha", "DMC_tC_ha", "FLB_tC_ha"]
# Bloque 3
def resumen_incertidumbre(grupo, columnas):
    resultados = []
    for col in columnas:
        data = pd.to_numeric(grupo[col], errors="coerce").dropna()
        n = len(data)
        if n > 1:
            media = data.mean()
            varianza = data.var(ddof=1)          # Varianza muestral
            ds = np.sqrt(varianza)               # Desv. estándar
            ee = ds / np.sqrt(n)                 # Error estándar
            tcrit = stats.t.ppf(1 - 0.05/2, n-1) # t de Student 95%
            half_width = tcrit * ee              # semi-amplitud del IC
            ic_inf = media - half_width
            ic_sup = media + half_width
            u_pct = (half_width / media) * 100 if media != 0 else np.nan
            resultados.append([col, n, media, varianza, ds, ee, tcrit, ic_inf, ic_sup, half_width, u_pct])
        else:
            resultados.append([col, n, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])

    return pd.DataFrame(resultados, columns=[
        "Variable","n","Media","Varianza","DS","EE","t_crit","IC_inf","IC_sup","Half_width","U_%"
    ])

# Bloque 4
# 🔸 Calcular por cuenca y tipo (biomasa / carbono)
resumen_final = []
for cuenca, grupo in df.groupby("Cuenca"):
    res_bio = resumen_incertidumbre(grupo, cols_biomasa); res_bio["Tipo"]="Biomasa"; res_bio["Cuenca"]=cuenca
    res_car = resumen_incertidumbre(grupo, cols_carbono); res_car["Tipo"]="Carbono"; res_car["Cuenca"]=cuenca
    resumen_final.append(pd.concat([res_bio, res_car], ignore_index=True))

resumen_final = pd.concat(resumen_final, ignore_index=True)
# Bloque 5
# 💾 Guardar: solo depósitos individuales (sin Totales)
resumen_final.to_excel("resumen_incertidumbres_por_cuenca_sin_totales.xlsx", index=False)
print("✅ Archivo generado: resumen_incertidumbres_por_cuenca_sin_totales.xlsx")
