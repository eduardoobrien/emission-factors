# ==========================================
# Índice de Estrés Ambiental (E) desde coordenadas UTM 18S/19S
# Entrada : estresambiental_um.xlsx (Hoja1) con columnas: codigo_um, Zona_UTM, X_UTM, Y_UTM
# Salida  : estresambiental_um_con_E.xlsx (misma tabla + columna E)
# ==========================================

# install.packages(c("BIOMASS","readxl","writexl","dplyr","sf","terra","geodata","R.utils"))
suppressPackageStartupMessages({
  library(BIOMASS)
  library(readxl)
  library(writexl)
  library(dplyr)
  library(sf)
  library(terra)
  library(geodata)
  library(R.utils)
})

in_file  <- in_file <- "D:/estresambiental_um.xlsx"

out_file <- out_file <- "D:/estresambiental_um_con_E.xlsx"

# 1) Leer
tb <- read_excel(in_file, sheet = "Hoja1")
names(tb) <- trimws(names(tb))

req <- c("codigo_um","Zona_UTM","X_UTM","Y_UTM")
stopifnot(all(req %in% names(tb)))

# 2) Filtrar filas válidas
tb2 <- tb %>%
  filter(!is.na(Zona_UTM), Zona_UTM %in% c(18,19),
         is.finite(as.numeric(X_UTM)), is.finite(as.numeric(Y_UTM))) %>%
  mutate(Zona_UTM = as.integer(Zona_UTM))

# 3) Convertir UTM -> WGS84 por zona
to_geo <- function(dat, zone){
  if (nrow(dat)==0) return(NULL)
  st_as_sf(dat, coords = c("X_UTM","Y_UTM"),
           crs = paste0("+proj=utm +zone=", zone, " +south +datum=WGS84")) |>
    st_transform(4326)
}

g18 <- to_geo(filter(tb2, Zona_UTM==18), 18)
g19 <- to_geo(filter(tb2, Zona_UTM==19), 19)
g   <- dplyr::bind_rows(g18, g19)

# 4) Coordenadas lon/lat y chequeo de rango (Perú aprox.)
xy <- sf::st_coordinates(g)
g$lon <- xy[,1]; g$lat <- xy[,2]
g$coord_ok <- is.finite(g$lon) & is.finite(g$lat) &
              g$lon >= -85 & g$lon <= -65 &
              g$lat >= -20 & g$lat <= 5

# 5) Preparación para descargar/cargar rasters (Lima aprox.)
invisible(try(BIOMASS::computeE(matrix(c(-77.05,-12.05), ncol=2)), silent=TRUE))

# 6) Vectorizado
computeE_vector <- function(df_geo){
  coords <- as.matrix(df_geo[,c("lon","lat")])
  as.numeric(BIOMASS::computeE(coords))
}
E_vals <- tryCatch({
  # Solo para coord_ok TRUE; el resto serán NA
  idx_ok <- which(g$coord_ok)
  vals <- rep(NA_real_, nrow(g))
  if (length(idx_ok) > 0) {
    vals[idx_ok] <- computeE_vector(g[idx_ok,])
  }
  vals
}, error = function(e){
  # Fallback: fila por fila con timeout
  message("Vectorizado falló (", e$message, "). Uso modo seguro fila-por-fila.")
  safe_one <- function(lon, lat){
    if (!is.finite(lon) || !is.finite(lat)) return(NA_real_)
    m <- matrix(c(lon,lat), ncol=2)
    out <- tryCatch(R.utils::withTimeout(as.numeric(BIOMASS::computeE(m)), timeout=25, onTimeout="error"),
                    error = function(e) NA_real_)
    out
  }
  v <- rep(NA_real_, nrow(g))
  for (i in seq_len(nrow(g))) {
    if (g$coord_ok[i]) v[i] <- safe_one(g$lon[i], g$lat[i])
    if (i %% 200 == 0) message("  ...", i, " / ", nrow(g))
  }
  v
})

g$E <- E_vals

# 7) Unir a la tabla original por codigo_um (1 E por UM)
mini <- g |>
  sf::st_drop_geometry() |>
  select(codigo_um, E) |>
  group_by(codigo_um) |>
  summarise(E = dplyr::coalesce(E[which(!is.na(E))[1]], NA_real_), .groups="drop")

out <- tb |>
  left_join(mini, by="codigo_um")

# 8) Exportar
writexl::write_xlsx(out, path = out_file)
message("Listo. Archivo escrito: ", out_file)

library(readxl); library(dplyr)

res <- read_excel("D:/estresambiental_um_con_E.xlsx")
