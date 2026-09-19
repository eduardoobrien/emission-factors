# ============================
# Densidad de madera con BIOMASS (robusto)
# ============================

# install.packages(c("BIOMASS","readxl","writexl","dplyr","stringr","tidyr"))
suppressPackageStartupMessages({
  library(BIOMASS)
  library(readxl)
  library(writexl)
  library(dplyr)
  library(stringr)
  library(tidyr)
})

# --- 1) CONFIGURACIÓN
input_file  <- "D:/especies_cientifico_3_cuencas.xlsx"
# Ruta a tu Excel
input_sheet <- "Hoja3"                                
# Nombre de la hoja
species_col <- "Nombre_cientifico"                    # Columna con el binomio ("Genus species")

# --- 2) LECTURA ---
tb <- read_excel(input_file, sheet = input_sheet)

stopifnot(species_col %in% names(tb))
message("Filas leídas: ", nrow(tb))

# --- 3) LIMPIEZA DEL NOMBRE CIENTÍFICO ---
# Quita autores, "cf.", "aff.", "sp.", "spp.", subespecies/variedades, guiones, múlt. espacios, etc.
norm_binom <- function(x) {
  x <- as.character(x)
  x <- stringr::str_squish(x)
  x <- stringr::str_replace_all(x, "\\s+", " ")
  x <- stringr::str_to_lower(x)
  
  # elimina cf., aff., sp., spp. aislados o con puntuación
  x <- stringr::str_replace_all(x, "\\b(cf\\.|aff\\.|sp\\.|spp\\.)\\b", "")
  
  # elimina 'x' de híbridos intercalada como "Genus x species"
  x <- stringr::str_replace_all(x, "\\bx\\b", " ")
  
  # elimina subespecies/variedades/formas luego del epíteto específico
  # (palabras como subsp., var., f., forma, ssp.) y lo que siga
  x <- stringr::str_replace(x, "\\b(subsp\\.|ssp\\.|var\\.|forma|f\\.)\\b.*$", "")
  
  # elimina autores y cosas entre paréntesis al final
  x <- stringr::str_replace(x, "\\([^\\)]*\\)$", "")
  x <- stringr::str_replace(x, "\\b[A-Za-zà-ÿ\\-]+(,)?\\s*\\d{0,4}$", "")  # autor + año al final
  
  # limpia dobles espacios y recorta
  x <- stringr::str_squish(x)
  
  # capitaliza a "Genus species"
  x <- stringr::str_to_sentence(x)
  
  x
}

tb <- tb %>%
  mutate(
    .binom_raw = !!rlang::sym(species_col),
    .binom = norm_binom(.binom_raw)
  ) %>%
  # separar en género y especie
  separate(.binom, into = c("Genus",".SpeciesRest"), sep = " ", remove = FALSE,
           fill = "right", extra = "drop") %>%
  mutate(
    Species = ifelse(is.na(.SpeciesRest), "", str_extract(.SpeciesRest, "^[A-Za-z-]+")),
    Genus = str_replace_na(Genus, "")
  ) %>%
  select(-.SpeciesRest)

# --- 4) CHEQUEOS RÁPIDOS ---
sin_genus <- sum(is.na(tb$Genus) | tb$Genus == "")
solo_genus <- sum(tb$Species == "" | is.na(tb$Species))
message("Filas sin Genus: ", sin_genus)
message("Filas solo con Género (sin epíteto): ", solo_genus, " (se intentará imputar por género)")

# --- 5) DENSIDAD ---
wd_res <- tryCatch({
  BIOMASS::getWoodDensity(
    genus   = tb$Genus,
    species = tb$Species,
    stand   = NULL,
    region  = "World"   # <- clave para evitar el error de región
  )
}, error = function(e) {
  stop(paste("Error en getWoodDensity:", e$message))
})

# Detectar el nombre de la columna para la densidad de la madera
wd_col <- intersect(names(wd_res), c("wd", "wood_density", "dens", "meanWD", "rho"))
if (length(wd_col) == 0) stop("No se encontró ninguna columna de densidad en los resultados de getWoodDensity()")

# --- 6) UNIR Y EXPORTAR ---
tb_out <- tb %>%
  mutate(
    Densidad_madera_g_cm3 = wd_res[[wd_col[1]]],
    Fuente_densidad       = dplyr::coalesce(wd_res$level, NA_character_)
  )

na_count <- sum(is.na(tb_out$Densidad_madera_g_cm3))
message("Filas con NA en Densidad_madera_g_cm3: ", na_count)

out_path <- "D:/especies_con_densidad.xlsx"

writexl::write_xlsx(list(Hoja3 = tb_out), path = out_path)
message("Archivo escrito: ", out_path)
