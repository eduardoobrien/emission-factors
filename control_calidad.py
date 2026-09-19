# ===============================================================
# 🧠 CONTROL DE CALIDAD DE DATOS
# Versión Google Colab (2025)
# Descripción: Este script automatiza la revisión de datos del INFFS
# valores inválidos y consistencia taxonómica de datos forestales.
# ===============================================================

# Paso 1️⃣: Instalación de librerías necesarias
!pip install pandas openpyxl

# Paso 2️⃣: Importación de librerías
import pandas as pd
from google.colab import files

print("=== CONTROL DE CALIDAD DE DATOS DE CAMPO ===\n")

# Paso 3️⃣: Cargar archivo principal
print("🔼 Sube el archivo principal:tabla arboles")
uploaded = files.upload()
file_name = list(uploaded.keys())[0]
df = pd.read_excel(file_name)

print(f"✅ Archivo cargado: {file_name}")
print(f"Total de registros: {len(df)}\n")

# -------------------------------------------------------------------
# PASO 4️⃣: Definir y verificar columnas requeridas
# -------------------------------------------------------------------
columnas_requeridas = {
    "Distancia_X": "Distancia X (0–10 m)",
    "Distancia_Y": "Distancia Y (0–25 m)",
    "Lado": "Lado (D/I)",
    "Nombre_cientifico": "Nombre científico",
    "DAP1": "DAP1 (10–200 cm)",
    "DAP2": "DAP2 (10–200 cm)",
    "Altura_fuste": "Altura de fuste (0–40 m)",
    "Altura_total": "Altura total (0–50 m)"
}

print("🧩 Verificando columnas...")
for col in columnas_requeridas.keys():
    if col not in df.columns:
        raise ValueError(f"⚠️ Falta la columna obligatoria: '{col}'")

print("✅ Todas las columnas requeridas están presentes.\n")

# Convertir a numéricas las columnas cuantitativas
cols_numericas = ["Distancia_X", "Distancia_Y", "DAP1", "DAP2", "Altura_fuste", "Altura_total"]
for c in cols_numericas:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# -------------------------------------------------------------------
# Paso 5: Reglas de control de calidad
errores = []

# Función auxiliar: agrega error o aviso
def registrar(df_cond, mensaje):
    # Asegura que la porción del DataFrame no esté vacía antes de procesarla.
    if not df_cond.empty:
        # Selecciona únicamente las columnas que existen en df_cond antes de convertirlas a diccionario.
        cols_to_include = [col for col in df_cond.columns if col in df_cond.columns]
        # Incluir el índice original en el diccionario de errores.
        error_dicts = df_cond[cols_to_include].assign(error=mensaje).to_dict('records')
        for i, error_dict in zip(df_cond.index, error_dicts):
            error_dict['original_index'] = i
        errores.extend(error_dicts)

# --- 1. Distancia X (Distancia_X): 0 a 10 ---
columna_j = "Distancia_X"
mask_j = df[columna_j].notna()
registrar(df[mask_j & ~df[columna_j].between(0, 10)], 'Distancia X fuera de rango (0–10 m)')
registrar(df[~mask_j], 'Distancia X faltante')

# --- 2. Distancia Y (Distancia_Y): 0 a 25 ---
columna_y = "Distancia_Y"
mask_y = df[columna_y].notna()
registrar(df[mask_y & ~df[columna_y].between(0, 25)], 'Distancia Y fuera de rango (0–25 m)')
registrar(df[~mask_y], 'Distancia Y faltante')

# --- 3. Lado (Lado): solo "D" o "I" ---
columna_l = "Lado"
mask_l = df[columna_l].notna()
registrar(df[mask_l & ~df[columna_l].isin(["D", "I"])], 'Lado inválido (solo D o I)')
registrar(df[~mask_l], 'Lado faltante')

# --- 4. Nombre científico (Nombre_cientifico): tabla maestra ---
print("🔼 Sube el archivo de la tabla maestra (Excel con nombres científicos)")
uploaded_master = files.upload()
master_file = list(uploaded_master.keys())[0]
df_master = pd.read_excel(master_file)

# CAMBIA 'nombre_columna_maestra' por el nombre correcto en tu tabla maestra
columna_m = "Nombre_cientifico"
columna_maestra = "Nombre_cientifico" # Define the correct column name in the master table

# Asegura que la columna exista en df_master antes de acceder a ella
if columna_maestra in df_master.columns:
    nombres_validos = df_master[columna_maestra].dropna().astype(str).str.strip().str.lower().unique()

    # Limpia y normaliza la columna “Nombre_cientifico” en el DataFrame principal
    df[columna_m] = df[columna_m].astype(str).str.strip().str.lower()

    # Comprueba si hay nombres no válidos
    mask_m = df[columna_m].notna() & (df[columna_m] != 'nn') 
# Excluye valores NN y cadenas “nn”
    registrar(df[mask_m & ~df[columna_m].isin(nombres_validos)], 'Nombre científico no válido')
    registrar(df[~mask_m], 'Nombre científico faltante')

    # Opcional: Imprimir algunos valores únicos para su inspección
    print("\nEjemplos de nombres científicos en el archivo principal:")
    print(df[columna_m].value_counts().head())

    print("\nEjemplos de nombres científicos en la tabla maestra:")
    print(df_master[columna_maestra].dropna().astype(str).str.strip().str.lower().value_counts().head())

else:
    print(f"⚠️ La columna '{columna_maestra}' no se encontró en el archivo maestro.")

# --- 5. DAP1 (DAP1): 10 a 200 ---
columna_s = "DAP1"
mask_s = df[columna_s].notna()
registrar(df[mask_s & ~df[columna_s].between(10, 200)], 'DAP1 fuera de rango (10–200 cm)')
registrar(df[~mask_s], 'DAP1 faltante')

# --- 6. DAP2 (DAP2): 10 a 200 (solo valida si hay dato) ---
columna_t = "DAP2"
mask_t = df[columna_t].notna()  # Solo los que tienen valor
registrar(df[mask_t & ~df[columna_t].between(10, 200)], 'DAP2 fuera de rango (10–200 cm)')
# No registra error si está faltante

# --- 7. Altura de fuste (Altura_fuste): 0 a 40 ---
columna_u = "Altura_fuste"
mask_u = df[columna_u].notna()
registrar(df[mask_u & ~df[columna_u].between(0, 40)], 'Altura de fuste fuera de rango (0–40 m)')
registrar(df[~mask_u], 'Altura de fuste faltante')

# --- 8. Altura total (Altura_total): 0 a 50 ---
columna_v = "Altura_total"
mask_v = df[columna_v].notna()
registrar(df[mask_v & ~df[columna_v].between(0, 50)], 'Altura total fuera de rango (0–50 m)')
registrar(df[~mask_v], 'Altura total faltante')

# --- 9. Consistencia entre Altura_fuste y Altura_total ---
mask_alturas = df["Altura_fuste"].notna() & df["Altura_total"].notna()
registrar(
    df[mask_alturas & (df["Altura_fuste"] > df["Altura_total"])],
    'Inconsistencia: Altura de fuste mayor que Altura total (debe ser menor o igual)'
)

# Paso 6:  --- Mostrar resultados ---
df_errores = pd.DataFrame(errores)

# Crear una copia base con "sin error"
df_resultado = df.copy()
df_resultado["error"] = "sin error"

if not df_errores.empty:
    # Agrupar los errores por el índice original
    df_errores_agrupado = (
        df_errores.groupby("original_index")["error"]
        .apply(lambda x: "; ".join(sorted(set(x))))  # Une errores únicos en una sola celda
        .reset_index()
    )

    # Combinar los errores con el DataFrame original
    df_resultado = df_resultado.merge(
        df_errores_agrupado,
        left_index=True,
        right_on="original_index",
        how="left",
        suffixes=("", "_detected")
    )

    # Actualizar la columna "error"
    df_resultado["error"] = df_resultado["error_detected"].fillna("sin error")

    # Eliminar columnas auxiliares
    df_resultado.drop(columns=["original_index", "error_detected"], inplace=True, errors="ignore")

# Paso 7:   --- Resumen ---
print(f"🔎 Total de registros: {len(df_resultado)}")
print(f"⚠️ Registros con error: {(df_resultado['error'] != 'sin error').sum()}")
print(f"✅ Registros sin error: {(df_resultado['error'] == 'sin error').sum()}\n")

# Mostrar vista previa
display(df_resultado.head())
# --- Guardar resultados ---
df_resultado.to_excel("errores_control_calidad.xlsx", index=False)
files.download("errores_control_calidad.xlsx")

print("💾 Archivo 'errores_control_calidad.xlsx' generado correctamente sin filas duplicadas.")
