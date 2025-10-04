import xarray as xr
import requests
import os
import pandas as pd
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURACIÓN ---
EARTHDATA_USERNAME = "e_lis"
EARTHDATA_PASSWORD = "Nasa57elisa_"
FILE_WITH_URLS = r"C:\Users\ramir\github_repos\Nasa_SAC\Will-It-Rain-On-My-Parade-BARKED\subset_M2I1NXASM_5.12.4_20251004_082430_.txt"

# --- ¡NUEVO! REDUCCIÓN DE RESOLUCIÓN ---
# Un factor de 4 reduce los datos 16 veces (4x4). Un factor de 5 los reduce 25 veces.
# Empieza con 4 o 5. Un valor más bajo = más detalle pero archivos más grandes.
DOWNSAMPLE_FACTOR = 4
# ----------------------------------------

# Variables para extraer
variables_temperatura = ['T2M', 'TS', 'TQV', 'PS', 'U10M', 'V10M', 'lon', 'lat', 'time']
variables_lluvia = ['TQV', 'T2M', 'PS', 'U10M', 'V10M', 'TQI', 'TQL', 'lon', 'lat', 'time']
VARS_TO_KEEP = variables_temperatura

# Hilos y guardado
MAX_WORKERS = 6
SAVE_EVERY = 50
OUTPUT_FOLDER = "output_data_global" # Carpeta para los datos globales
LOGIN_URL = "https://urs.earthdata.nasa.gov"

# Rango de años a procesar
start_year = 1980
end_year = 1985

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- FUNCIONES ---

def create_authenticated_session():
    """Crea una única sesión autenticada para ser usada por todos los hilos."""
    session = requests.Session()
    session.auth = (EARTHDATA_USERNAME, EARTHDATA_PASSWORD)
    try:
        r = session.get(LOGIN_URL, timeout=30)
        r.raise_for_status()
        print("🔑 Sesión autenticada correctamente.", flush=True)
        return session
    except Exception as e:
        print(f"❌ Error fatal al autenticar la sesión: {e}", flush=True)
        return None

def download_and_process_data(url, session):
    """Descarga, reduce la resolución de un archivo .nc4 y lo procesa a DataFrame."""
    local_filename = f"temp_{uuid.uuid4().hex}.nc4"
    try:
        response = session.get(url, timeout=120, stream=True, allow_redirects=True)
        response.raise_for_status()
        with open(local_filename, "wb") as f:
            f.write(response.content)

        with xr.open_dataset(local_filename) as ds:
            lat_name = 'lat' if 'lat' in ds.coords else 'latitude'
            lon_name = 'lon' if 'lon' in ds.coords else 'longitude'
            
            vars_to_load = [v for v in VARS_TO_KEEP if v in ds.variables]
            if not vars_to_load:
                return None

            # --- CAMBIO PRINCIPAL: REDUCIR RESOLUCIÓN EN LUGAR DE CORTAR ---
            ds_coarse = ds[vars_to_load].coarsen({lat_name: DOWNSAMPLE_FACTOR, lon_name: DOWNSAMPLE_FACTOR}, boundary='trim').mean()
            # -----------------------------------------------------------------
            
            df = ds_coarse.to_dataframe().reset_index()
            
            df['time'] = pd.to_datetime(df['time'])
            df = df[df['time'].dt.year.between(start_year, end_year)]
            if df.empty:
                return None
            return df

    except Exception:
        return None
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)

# --- SCRIPT PRINCIPAL --- (El resto del script es similar al anterior)
def main():
    if not os.path.exists(FILE_WITH_URLS):
        print(f"❌ No se encontró el archivo: {FILE_WITH_URLS}", flush=True)
        return

    with open(FILE_WITH_URLS, "r") as file:
        urls = [line.strip() for line in file if line.strip().endswith(('.nc', '.nc4'))]

    print(f"✅ {len(urls)} URLs encontradas.", flush=True)
    print(f"🎯 Variables: {VARS_TO_KEEP}", flush=True)
    print(f"🌍 Procesando datos globales con factor de reducción: {DOWNSAMPLE_FACTOR}x")
    print(f"⏱  Escaneando años {start_year} a {end_year}\n", flush=True)

    session = create_authenticated_session()
    if not session:
        return

    all_dataframes = {year: [] for year in range(start_year, end_year + 1)}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_and_process_data, url, session): url for url in urls}
        for i, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            try:
                df = future.result()
                if df is not None:
                    for year, group in df.groupby(df['time'].dt.year):
                        if year in all_dataframes:
                            all_dataframes[year].append(group)
                    print(f"[{i}/{len(urls)}] ✅ {os.path.basename(url)} procesado", flush=True)
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Error inesperado: {e}", flush=True)

            for year, groups in all_dataframes.items():
                if len(groups) >= SAVE_EVERY:
                    year_folder = os.path.join(OUTPUT_FOLDER, str(year))
                    os.makedirs(year_folder, exist_ok=True)
                    temp_df = pd.concat(groups, ignore_index=True)
                    part_num = len(os.listdir(year_folder)) + 1
                    temp_file = os.path.join(year_folder, f"partial_data_{part_num}.csv")
                    temp_df.to_csv(temp_file, index=False)
                    print(f"💾 Guardado parcial ({year}): {temp_file}", flush=True)
                    all_dataframes[year].clear()

    for year, groups in all_dataframes.items():
        if groups:
            year_folder = os.path.join(OUTPUT_FOLDER, str(year))
            os.makedirs(year_folder, exist_ok=True)
            final_df = pd.concat(groups, ignore_index=True)
            final_file = os.path.join(year_folder, f"merra2_data_{year}.csv")
            final_df.to_csv(final_file, index=False)
            print(f"💾 Guardado final ({year}): {final_file}", flush=True)

    session.close()
    elapsed = time.time() - start_time
    print(f"\n✅ Proceso completado en {elapsed/60:.2f} minutos.", flush=True)

if __name__ == "__main__":
    main()
