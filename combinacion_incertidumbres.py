# --- Google Colab Script ---
# Bloque 1
import pandas as pd
import numpy as np

# Cargar archivo Excel
archivo = "incertidumbre_total_con_componentes.xlsx"
df = pd.read_excel(archivo, sheet_name="Sheet1")

# Bloque 2
# Asegurar nombres de columnas
df.columns = df.columns.str.strip()

# Filtrar registros válidos con incertidumbre y valor de carbono
df_valid = df[~df["U_combinada_%"].isna() & ~df["Media"].isna()].copy()

# Bloque 3
# Convertir incertidumbre combinada a proporción
df_valid["U_prop"] = df_valid["U_combinada_%"] / 100
df_valid["Valor_tC_ha"] = df_valid["Media"]

# Bloque 4
# Función para calcular incertidumbre total combinada por cuenca
def incertidumbre_combinada(grupo):
    numerador = np.sqrt(np.sum((grupo["U_prop"]**2) * (grupo["Valor_tC_ha"]**2)))
    denominador = np.sum(grupo["Valor_tC_ha"])
    return (numerador / denominador) * 100  # en porcentaje

# Bloque 5
# Aplicar por cuenca
resultado = df_valid.groupby("Cuenca").apply(incertidumbre_combinada).reset_index()
resultado.columns = ["Cuenca", "U_total_comb_%"]

# Bloque 6
# Guardar resultados
resultado.to_excel("U_total_comb_por_cuenca.xlsx", index=False)
print("Archivo guardado como 'U_total_comb_por_cuenca.xlsx'")
