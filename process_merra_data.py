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

# Variables para extraer
variables_temperatura = ['T2M', 'TS', 'TQV', 'PS', 'U10M', 'V10M', 'lon', 'lat', 'time']
variables_lluvia = ['TQV', 'T2M', 'PS', 'U10M', 'V10M', 'TQI', 'TQL', 'lon', 'lat', 'time']
VARS_TO_KEEP = variables_temperatura  # o variables_lluvia

# Hilos y guardado
MAX_WORKERS = 6
SAVE_EVERY = 200
OUTPUT_FOLDER = "output_data"
LOGIN_URL = "https://urs.earthdata.nasa.gov"

# Rango de años a procesar
start_year = 1980
end_year = 1985

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.environ["NETRC"] = os.path.expanduser("~/.netrc")

# --- FUNCIONES ---

def create_authenticated_session():
    """Crea sesión autenticada con Earthdata."""
    session = requests.Session()
    session.auth = (EARTHDATA_USERNAME, EARTHDATA_PASSWORD)
    try:
        r = session.get(LOGIN_URL, timeout=20)
        r.raise_for_status()
        return session
    except Exception as e:
        print(f"❌ Error autenticando sesión: {e}", flush=True)
        return None

def download_and_process_data(url):
    """Descarga y procesa un archivo .nc4 a DataFrame."""
    local_filename = f"temp_{uuid.uuid4().hex}.nc4"
    session = create_authenticated_session()
    if not session:
        return None

    try:
        response = session.get(url, timeout=120, stream=True, allow_redirects=True)
        response.raise_for_status()
        with open(local_filename, "wb") as f:
            f.write(response.content)

        with xr.open_dataset(local_filename) as ds:
            # Coordenadas correctas
            lat_name = 'lat' if 'lat' in ds.coords else 'latitude'
            lon_name = 'lon' if 'lon' in ds.coords else 'longitude'

            vars_to_load = [v for v in VARS_TO_KEEP if v in ds.variables]
            if not vars_to_load:
                print(f"⚠️ {os.path.basename(url)} no contiene las variables deseadas.", flush=True)
                return None

            ds_point = ds[vars_to_load].sel({lat_name: 19.43, lon_name: -99.13}, method='nearest')
            df = ds_point.to_dataframe().reset_index()
            df = df.drop(columns=[lat_name, lon_name], errors='ignore')

            # Filtrar solo años dentro del rango
            df['time'] = pd.to_datetime(df['time'])
            df = df[df['time'].dt.year.between(start_year, end_year)]
            if df.empty:
                return None
            return df

    except Exception as e:
        print(f"❌ Error con {url}: {e}", flush=True)
        return None
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)
        session.close()

# --- SCRIPT PRINCIPAL ---

def main():
    if not os.path.exists(FILE_WITH_URLS):
        print(f"❌ No se encontró el archivo: {FILE_WITH_URLS}", flush=True)
        return

    with open(FILE_WITH_URLS, "r") as file:
        urls = [line.strip() for line in file if line.strip().endswith(('.nc', '.nc4'))]

    print(f"✅ {len(urls)} URLs encontradas.", flush=True)
    print(f"🎯 Variables: {VARS_TO_KEEP}", flush=True)
    print(f"⏱ Escaneando años {start_year} a {end_year}\n", flush=True)

    all_dataframes = {year: [] for year in range(start_year, end_year+1)}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_and_process_data, url): url for url in urls}
        for i, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            try:
                df = future.result()
                if df is not None:
                    for year, group in df.groupby(df['time'].dt.year):
                        all_dataframes[year].append(group)
                    print(f"[{i}/{len(urls)}] ✅ {os.path.basename(url)} procesado", flush=True)
                else:
                    print(f"[{i}/{len(urls)}] ⚠️ {os.path.basename(url)} vacío", flush=True)
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Error inesperado: {e}", flush=True)

            # Guardado parcial por año
            for year, groups in all_dataframes.items():
                if len(groups) >= SAVE_EVERY:
                    year_folder = os.path.join(OUTPUT_FOLDER, str(year))
                    os.makedirs(year_folder, exist_ok=True)
                    temp_df = pd.concat(groups, ignore_index=True)
                    temp_file = os.path.join(year_folder, f"partial_data_{i}_{year}.csv")
                    temp_df.to_csv(temp_file, index=False)
                    print(f"💾 Guardado parcial ({year}): {temp_file}", flush=True)
                    all_dataframes[year].clear()

    # Guardado final por año
    for year, groups in all_dataframes.items():
        if groups:
            year_folder = os.path.join(OUTPUT_FOLDER, str(year))
            os.makedirs(year_folder, exist_ok=True)
            final_df = pd.concat(groups, ignore_index=True)
            final_file = os.path.join(year_folder, f"merra2_data_{year}.csv")
            final_df.to_csv(final_file, index=False)
            print(f"💾 Guardado final ({year}): {final_file}", flush=True)

    elapsed = time.time() - start_time
    print(f"\n✅ Proceso completado en {elapsed/60:.2f} minutos.", flush=True)

if __name__ == "__main__":
    main()
