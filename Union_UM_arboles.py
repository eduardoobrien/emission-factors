# ===============================================================
# UNIÓN DE UNIDADES DE MUESTREO Y ÁRBOLES
# Versión adaptable para Google Colab
# Autor: Eduardo O’Brien
#
# Descripción:
# Une la tabla de unidades de muestreo con la tabla de árboles
# según la columna del código "codigo_um".
# Conserva únicamente los árboles que tienen coincidencia
# con las unidades de muestreo seleccionadas.
# ===============================================================

# ---------------------------------------------------------------
# 1) Importar librerías y subir archivos
# ---------------------------------------------------------------

from google.colab import files
import pandas as pd

print("📂 Sube los dos archivos Excel:")
print("   1. Archivo de unidades de muestreo")
print("   2. Archivo de árboles")

uploaded = files.upload()

if len(uploaded) != 2:
    raise ValueError(
        f"❌ Se esperaban 2 archivos Excel, pero se cargaron {len(uploaded)}."
    )

archivos = list(uploaded.keys())

print("\nArchivos cargados:")
for i, archivo in enumerate(archivos, start=1):
    print(f"{i}. {archivo}")

# ---------------------------------------------------------------
# 2) Seleccionar los archivos
# ---------------------------------------------------------------

archivo_um = archivos[0]
archivo_arboles = archivos[1]

# ---------------------------------------------------------------
# 3) Configurar los nombres de las hojas
# ---------------------------------------------------------------

# Ajusta estos nombres según las hojas de los archivos utilizados.
hoja_um = "um_putumayo_join"
hoja_arboles = "tree"

# ---------------------------------------------------------------
# 4) Leer las hojas específicas
# ---------------------------------------------------------------

df_um = pd.read_excel(archivo_um, sheet_name=hoja_um)
df_arboles = pd.read_excel(archivo_arboles, sheet_name=hoja_arboles)

print(
    f"\n✅ Cargado '{archivo_um}' ({hoja_um}) "
    f"con {len(df_um)} filas."
)

print(
    f"✅ Cargado '{archivo_arboles}' ({hoja_arboles}) "
    f"con {len(df_arboles)} filas."
)

# ---------------------------------------------------------------
# 5) Verificar existencia de la columna 'codigo_um'
# ---------------------------------------------------------------

if "codigo_um" not in df_um.columns:
    raise ValueError(
        "❌ La columna 'codigo_um' no se encontró "
        "en el archivo de unidades de muestreo."
    )

if "codigo_um" not in df_arboles.columns:
    raise ValueError(
        "❌ La columna 'codigo_um' no se encontró "
        "en el archivo de árboles."
    )

# ---------------------------------------------------------------
# 6) Unir las tablas según 'codigo_um'
# ---------------------------------------------------------------

# Solo conservar árboles que tengan coincidencia
# con las unidades de muestreo seleccionadas.

df_merged = df_arboles.merge(
    df_um,
    on="codigo_um",
    how="inner"
)

print(
    f"\n✅ Unión completada. "
    f"Total de filas resultantes: {len(df_merged)}"
)

# ---------------------------------------------------------------
# 7) Guardar resultado
# ---------------------------------------------------------------

nombre_salida = f"resultado_union_{hoja_um}.xlsx"

df_merged.to_excel(nombre_salida, index=False)

print(f"💾 Archivo guardado como: {nombre_salida}")

# ---------------------------------------------------------------
# 8) Descargar resultado
# ---------------------------------------------------------------

files.download(nombre_salida)
