import xarray as xr
import requests
import os
import time

# --- CONFIGURACIÓN ---
# 1. Pega aquí tu token de NASA Earthdata
NASA_TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJhYWFjNjMiLCJleHAiOjE3NjQ3NTI5MzUsImlhdCI6MTc1OTU2ODkzNSwiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5hc2EuZ292IiwiaWRlbnRpdHlfcHJvdmlkZXIiOiJlZGxfb3BzIiwiYWNyIjoiZWRsIiwiYXNzdXJhbmNlX2xldmVsIjozfQ.Iwnkv0fc4NftmAXuySrrQ0aZ52j_-FUEozBiE2fwhqwjJk6iKlozugfHMFr9gjkEiyb6f1-PVbt4ZnQlcDsrbMBpWGN1Oe3jwPqk2YrNJaPnZNvu8rhL7wtKPyF7ODj6y_YxogCJeCSZUqmdWYl9sRIWcqLQ_odaEBbOGAj3GIEI9HPEcuuZmNDc-1Y7K2Xxn3tH4bv6YFlxiPdbHydGvEIfnA4pME5O-RxpCaz4A5oyuO3lfVwEFszGPsn2ZlROAb6M8IJfeA4JmYMrl-SRVYlT94qI77UD1scwErhHYGq4EmgJli7woPiANCumsV88TPFq1JplvN2m-TMF8hawcg"

# 2. Escribe la ruta COMPLETA y CORRECTA de tu archivo .txt
#    Usa diagonales normales '/' en lugar de invertidas '\'.
#    Por ejemplo: 'C:/Users/ramir/Downloads/subset_M2I1NXASM_5.12.4_20251004_082430_.txt'
FILE_WITH_URLS = "C:/users/ramir/github_repos/Nasa_SAC/Will-It-Rain-On-My-Parade-BARKED/subset_M2I1NXASM_5.12.4_20251004_082430_.txt"
# --------------------

# Cabecera de autorización que se usará para todas las solicitudes
headers = {
    "Authorization": f"Bearer {NASA_TOKEN}"
}

# Verificar si el archivo de URLs existe antes de empezar
if not os.path.exists(FILE_WITH_URLS):
    print(f"❌ ERROR: No se encontró el archivo de URLs en la ruta especificada:")
    print(f"   '{FILE_WITH_URLS}'")
    print("   Por favor, revisa la variable FILE_WITH_URLS en el script.")
else:
    print(f"Archivo de URLs encontrado en: {FILE_WITH_URLS}")
    print("Iniciando el proceso de lectura de datos...\n")

    # Abrir el archivo de texto y leer las URLs una por una
    with open(FILE_WITH_URLS, 'r') as file:
        # Usamos enumerate para contar las líneas
        for i, line in enumerate(file, 1):
            url = line.strip() # .strip() quita espacios en blanco o saltos de línea

            # Omitir líneas vacías o que no parezcan URLs de datos
            if not url or not url.endswith(('.nc', '.nc4')):
                print(f"--- Línea {i}: Omitiendo (no es un archivo NetCDF) -> '{url[:50]}...'")
                continue

            print(f"--- Procesando Línea {i}: {os.path.basename(url)} ---")
            local_filename = "temp_data.nc4" # Usaremos un archivo temporal

            try:
                # Paso 1: Descargar el archivo
                response = requests.get(url, headers=headers, timeout=30, stream=True)
                response.raise_for_status() # Lanza un error si falla la autenticación

                with open(local_filename, 'wb') as f:
                    f.write(response.content)

                # Paso 2: Abrir el archivo local
                print("   Descarga exitosa. Abriendo con xarray...")
                with xr.open_dataset(local_filename) as ds:
                    print("      Parámetros leídos correctamente. Variables disponibles:")
                    # Imprime las variables (la información clave del archivo)
                    print(f"      {list(ds.variables.keys())}")

            except requests.exceptions.HTTPError as http_err:
                print(f"   ❌ ERROR de autenticación para esta URL. Código: {http_err.response.status_code}")
                print("      Deteniendo el script. Revisa tu TOKEN.")
                break # Detiene el bucle si el token falla
            except Exception as e:
                print(f"   ❌ Ocurrió un error inesperado con esta URL: {e}")
            finally:
                # Limpieza del archivo temporal
                if os.path.exists(local_filename):
                    os.remove(local_filename)
                
                # Pequeña pausa para no saturar el servidor
                time.sleep(0.1)

    print("\n--- Proceso completado ---")