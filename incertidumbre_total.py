# --- Google Colab Script para calcular incertidumbre total combinada IPCC ---
# Bloque 1
import pandas as pd
import numpy as np

# 📌 Subir archivo manualmente si no está en entorno Colab
# from google.colab import files
# uploaded = files.upload()

# 📂 Cargar archivo
archivo = "resumen_incertidumbres_por_cuenca_sin_totales.xlsx"
df = pd.read_excel(archivo, sheet_name="Sheet1")

# Bloque 2
# 📊 Definir incertidumbres adicionales según IPCC (valores como proporciones)
# AGB: ±10% modelo + ±10% densidad + ±5% fracción carbono
# BGB: ±25% expansión + ±5% fracción carbono
# DTC, FLB, DMC: solo ±5% fracción carbono
incertidumbres_adicionales = {
    "AGB_tC_ha": [0.10, 0.10, 0.05],
    "BGB_tC_ha": [0.25, 0.05],
    "DTC_tC_ha": [0.05],
    "FLB_tC_ha": [0.05],
    "DMC_tC_ha": [0.05]
}
# Bloque 3
# 🧮 Función que aplica el método cuadrático del IPCC (combinación de incertidumbres)
def combinar_incertidumbres(mu, adicionales):
    componentes = [mu / 100.0] + adicionales  # pasar % a proporción
    return np.sqrt(np.sum(np.square(componentes))) * 100  # volver a porcentaje

# Bloque 4
# 🧩 Aplicar combinación fila por fila si la variable está en el diccionario
df["U_combinada_%"] = df.apply(
    lambda fila: combinar_incertidumbres(fila["U_%"], incertidumbres_adicionales[fila["Variable"]])
    if fila["Variable"] in incertidumbres_adicionales else np.nan,
    axis=1
)

# Bloque 5
# 💾 Guardar resultados
salida = "incertidumbre_total_con_componentes.xlsx"
df.to_excel(salida, index=False)
print("✅ Archivo generado:", salida)
