# --- Google Colab / Python ---
import pandas as pd
import numpy as np

# 1. Leer archivo Excel
# Cargar "resultado_con_AGB_ucayali.xlsx" al entorno de Colab
df = pd.read_excel("resultado_con_AGB_4977.xlsx", sheet_name="Sheet1")

# 2. Asegurar tipos y crear columnas auxiliares
# Nombre científico siempre como string en minúsculas
df["Nombre_cientifico"] = df["Nombre_cientifico"].astype(str).str.strip().str.lower()

# Extraer género (primera palabra del nombre científico)
df["genero"] = df["Nombre_cientifico"].str.split().str[0]

# Calcular D2H = DAP1^2 * Altura_fuste
df["D2H"] = df["DAP1"]**2 * df["Altura_fuste"]

# Asegurar que densidad y estrés sean numéricos
df["Densidad_madera_g_cm3"] = pd.to_numeric(df["Densidad_madera_g_cm3"], errors="coerce")
df["estres_ambiental"] = pd.to_numeric(df["estres_ambiental"], errors="coerce")
df["DAP1"] = pd.to_numeric(df["DAP1"], errors="coerce")
df["Altura_fuste"] = pd.to_numeric(df["Altura_fuste"], errors="coerce")

# Manejo de la columna de grado de descomposición (puede tener o no espacio al final)
if "decomposition_degree" in df.columns:
    col_dec = "decomposition_degree"
elif "decomposition_degree " in df.columns:
    col_dec = "decomposition_degree "
else:
    col_dec = None
    print("⚠ No se encontró la columna 'decomposition_degree' (revisa el nombre exacto).")

# 3. Inicializar columnas de biomasa
# Usamos 0 como valor por defecto cuando la ecuación no aplica
df["AGB_tree_kg"] = 0.0      # Árboles/arbustos/suculentas/helechos/hemiepífitas vivos
df["AGB_palm_kg"] = 0.0      # Palmeras vivas
df["AGB_liana_kg"] = 0.0     # Lianas vivas
df["AGB_dead_kg"] = 0.0      # Árboles muertos en pie
df["AGB_tocon_kg"] = 0.0     # Tocones (biomasa estimada a partir de volumen y densidad)

# -------------------------------------------------------------------
# 4. Máscaras útiles
# -------------------------------------------------------------------

# Estados
alive = df["tree_status"] == 1
tocon = df["tree_status"] == 4
# Muerto en pie: cualquier tree_status distinto de 1 (vivo) y 4 (tocon)
dead_standing = (df["tree_status"] != 1) & (df["tree_status"] != 4)

# Hábitos de crecimiento
is_tree_like = df["growth_habit"].isin([1, 2, 6, 7, 8])   # árbol, arbusto, suculenta, helecho, hemiepífita
is_palm = df["growth_habit"] == 4
is_liana = df["growth_habit"] == 5

# Familia palmeras
is_arecaceae = df["tree_species_family_scientific_name"] == "ARECACEAE"

# Datos válidos para logaritmos
valid_density = df["Densidad_madera_g_cm3"] > 0
valid_dap = df["DAP1"] > 0
valid_d2h = df["D2H"] > 0
valid_height = df["Altura_fuste"] > 0

# -------------------------------------------------------------------
# 5. Árboles/arbustos/suculentas/helechos/hemiepífitas VIVOS (Chave 2014)
#    AGB_tree_kg
# -------------------------------------------------------------------

mask_tree_alive = alive & is_tree_like & valid_density & valid_dap

df.loc[mask_tree_alive, "AGB_tree_kg"] = np.exp(
    -1.803
    - 0.976 * df.loc[mask_tree_alive, "estres_ambiental"]
    + 0.976 * np.log(df.loc[mask_tree_alive, "Densidad_madera_g_cm3"])
    + 2.673 * np.log(df.loc[mask_tree_alive, "DAP1"])
    - 0.0299 * (np.log(df.loc[mask_tree_alive, "DAP1"]) ** 2)
)

# -------------------------------------------------------------------
# 6. Palmeras VIVAS (AGB_palm_kg) según género
# -------------------------------------------------------------------

mask_palm_alive = alive & is_palm & is_arecaceae

# Creamos un vinculo para no repetir tanto código
generos_palma = {
    "astrocaryum": "astrocaryum",
    "attalea": "attalea",
    "euterpe": "euterpe",
    "iriartea": "iriartea",
    "mauritia": "mauritia",
    "mauritiella": "mauritiella",
    "oenocarpus": "oenocarpus",
    "socratea": "socratea",
}

# 6.1 Astrocaryum: AGB = 21.302 * H
mask_astrocaryum = mask_palm_alive & (df["genero"] == "astrocaryum") & valid_height
df.loc[mask_astrocaryum, "AGB_palm_kg"] = 21.302 * df.loc[mask_astrocaryum, "Altura_fuste"]

# 6.2 Attalea: ln(AGB) = 3.2579 + 1.1249 * ln(H + 1)
mask_attalea = mask_palm_alive & (df["genero"] == "attalea")
mask_attalea_valid = mask_attalea & (df["Altura_fuste"] > -1)
df.loc[mask_attalea_valid, "AGB_palm_kg"] = np.exp(
    3.2579 + 1.1249 * np.log(df.loc[mask_attalea_valid, "Altura_fuste"] + 1.0)
)

# 6.3 Euterpe: AGB = -108.81 + 13.589 * H
mask_euterpe = mask_palm_alive & (df["genero"] == "euterpe") & valid_height
agb_euterpe = -108.81 + 13.589 * df.loc[mask_euterpe, "Altura_fuste"]
# Evitar valores negativos
df.loc[mask_euterpe, "AGB_palm_kg"] = np.where(agb_euterpe > 0, agb_euterpe, 0.0)

# 6.4 Iriartea: ln(AGB) = -3.483 + 0.94371 * ln(D2H)
mask_iriartea = mask_palm_alive & (df["genero"] == "iriartea") & valid_d2h
df.loc[mask_iriartea, "AGB_palm_kg"] = np.exp(
    -3.483 + 0.94371 * np.log(df.loc[mask_iriartea, "D2H"])
)

# 6.5 Mauritia: ln(AGB) = 2.4647 + 1.3777 * ln(H)
mask_mauritia = mask_palm_alive & (df["genero"] == "mauritia") & valid_height
df.loc[mask_mauritia, "AGB_palm_kg"] = np.exp(
    2.4647 + 1.3777 * np.log(df.loc[mask_mauritia, "Altura_fuste"])
)

# 6.6 Mauritiella: AGB = 2.8662 * H
mask_mauritiella = mask_palm_alive & (df["genero"] == "mauritiella") & valid_height
df.loc[mask_mauritiella, "AGB_palm_kg"] = 2.8662 * df.loc[mask_mauritiella, "Altura_fuste"]

# 6.7 Oenocarpus: ln(AGB) = 4.5496 + 0.1387 * H
mask_oenocarpus = mask_palm_alive & (df["genero"] == "oenocarpus") & valid_height
df.loc[mask_oenocarpus, "AGB_palm_kg"] = np.exp(
    4.5496 + 0.1387 * df.loc[mask_oenocarpus, "Altura_fuste"]
)

# 6.8 Socratea: ln(AGB) = -3.7965 + 1.0029 * ln(D2H)
mask_socratea = mask_palm_alive & (df["genero"] == "socratea") & valid_d2h
df.loc[mask_socratea, "AGB_palm_kg"] = np.exp(
    -3.7965 + 1.0029 * np.log(df.loc[mask_socratea, "D2H"])
)

# 6.9 Otras palmeras (incluyendo "nn")
# ln(AGB) = -3.3488 + 2.7483 * ln(D)
generos_especificos = list(generos_palma.keys())
mask_palm_others = (
    mask_palm_alive
    & valid_dap
    & (
        (~df["genero"].isin(generos_especificos))
        | (df["Nombre_cientifico"] == "nn")
    )
)

df.loc[mask_palm_others, "AGB_palm_kg"] = np.exp(
    -3.3488 + 2.7483 * np.log(df.loc[mask_palm_others, "DAP1"])
)

# -------------------------------------------------------------------
# 7. Lianas VIVAS (AGB_liana_kg)
#    AGB = exp[-1.484 + 2.657 * ln(DAP1)]
# -------------------------------------------------------------------

mask_liana_alive = alive & is_liana & valid_dap

df.loc[mask_liana_alive, "AGB_liana_kg"] = np.exp(
    -1.484 + 2.657 * np.log(df.loc[mask_liana_alive, "DAP1"])
)

# -------------------------------------------------------------------
# 8. Individuos muertos en pie (AGB_dead_kg)
#    AGBest = exp(-2.024 - 0.896*E + 0.920*log(ρ) + 2.795*log(DAP1) - 0.0461*[log(DAP1)]^2)
# -------------------------------------------------------------------

# Muerto en pie = cualquier tree_status distinto de 1 (vivo) y 4 (tocon)
dead_standing = (df["tree_status"] != 1) & (df["tree_status"] != 4)

# Árbol-like muertos en pie (árbol, arbusto, suculenta, helecho, hemiepífita)
mask_dead_tree = dead_standing & is_tree_like & valid_density & valid_dap

df.loc[mask_dead_tree, "AGB_dead_kg"] = np.exp(
    -2.024
    - 0.896 * df.loc[mask_dead_tree, "estres_ambiental"]
    + 0.920 * np.log(df.loc[mask_dead_tree, "Densidad_madera_g_cm3"])
    + 2.795 * np.log(df.loc[mask_dead_tree, "DAP1"])
    - 0.0461 * (np.log(df.loc[mask_dead_tree, "DAP1"]) ** 2)
)

# **Palmeras** muertas en pie (growth_habit = 4)
mask_dead_palm = dead_standing & is_palm & valid_density & valid_dap

df.loc[mask_dead_palm, "AGB_dead_kg"] = np.exp(
    -2.024
    - 0.896 * df.loc[mask_dead_palm, "estres_ambiental"]
    + 0.920 * np.log(df.loc[mask_dead_palm, "Densidad_madera_g_cm3"])
    + 2.795 * np.log(df.loc[mask_dead_palm, "DAP1"])
    - 0.0461 * (np.log(df.loc[mask_dead_palm, "DAP1"]) ** 2)
)
# -------------------------------------------------------------------
# 9. Tocones (AGB_tocon_kg)
#    V = A * L;  A = π * r^2;  D_m = DAP1/100, r = D_m/2
#    ρ (kg/m3) = ρ (g/cm3) * 1000
#    Biomasa = V * ρ * factor_descomposición
# -------------------------------------------------------------------

if col_dec is not None:
    # Mapeo de grado de descomposición a factor
    factor_map = {1: 0.55, 2: 0.41, 3: 0.23}
    df["decomposition_factor"] = df[col_dec].map(factor_map).fillna(0.0)

    mask_tocon_valid = (
        tocon
        & valid_dap
        & valid_height
        & valid_density
        & (df["decomposition_factor"] > 0)
    )

    # Diámetro en metros
    D_m = df.loc[mask_tocon_valid, "DAP1"] / 100.0
    r_m = D_m / 2.0

    # Área basal en m2
    A_m2 = np.pi * (r_m ** 2)

    # Longitud L = altura del tocón (Altura_fuste) en m
    L_m = df.loc[mask_tocon_valid, "Altura_fuste"]

    # Volumen en m3
    V_m3 = A_m2 * L_m

    # Densidad en kg/m3
    rho_kg_m3 = df.loc[mask_tocon_valid, "Densidad_madera_g_cm3"] * 1000.0

    # Biomasa del tocón en kg
    agb_tocon = V_m3 * rho_kg_m3 * df.loc[mask_tocon_valid, "decomposition_factor"]

    df.loc[mask_tocon_valid, "AGB_tocon_kg"] = agb_tocon
else:
    df["decomposition_factor"] = 0.0
    print("No se calculó AGB_tocon_kg por falta de columna de grado de descomposición.")

# -------------------------------------------------------------------
# 10. Biomasa total por individuo
# -------------------------------------------------------------------

df["AGB_total_kg"] = (
    df["AGB_tree_kg"]
    + df["AGB_palm_kg"]
    + df["AGB_liana_kg"]
    + df["AGB_dead_kg"]
    + df["AGB_tocon_kg"]
)

# -------------------------------------------------------------------
# 11. Guardar resultado
# -------------------------------------------------------------------

output_file = "resultado_con_AGB_4977_biomasa.xlsx"
df.to_excel(output_file, sheet_name="Sheet1", index=False)

print(f"Listo ✅ Archivo guardado como: {output_file}")
