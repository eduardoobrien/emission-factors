import pandas as pd

# 1. Cargar archivos
df_principal = pd.read_excel("D:/resultado_union_um_4977_join.xlsx")
df_densidad = pd.read_excel("D:/especies_con_densidad.xlsx")
# Hoja3 si aplica: sheet_name="Hoja3"

# 2. Asegurar que los nombres científicos estén limpios
df_principal["Nombre_cientifico"] = df_principal["Nombre_cientifico"].str.strip().str.lower()
df_densidad["Nombre_cientifico"] = df_densidad["Nombre_cientifico"].str.strip().str.lower()

# 3. Hacer merge (LEFT JOIN)
df_merge = df_principal.merge(
    df_densidad[["Nombre_cientifico", "Densidad_madera_g_cm3"]],
    on="Nombre_cientifico",
    how="left"
)

# 4. Guardar archivo final
df_merge.to_excel("D:/resultado_con_densidad3.xlsx", index=False)

print("✅ Listo. Archivo guardado como resultado_con_densidad3.xlsx")
