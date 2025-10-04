
import pandas as pd

# Load the dataset from the filtered sample
try:
    df = pd.read_csv('filtered_sample.csv')

    # Define the new, clearer column names, removing the 'koi_' prefix
    new_column_names = {
        'kepid': 'KepID',
        'kepoi_name': 'KOIName',
        'koi_disposition': 'Disposition',
        'koi_pdisposition': 'KeplerDisposition',
        'koi_score': 'DispositionScore',
        'koi_fpflag_nt': 'NotTransitLikeFlag',
        'koi_fpflag_ss': 'StellarEclipseFlag',
        'koi_fpflag_co': 'CentroidOffsetFlag',
        'koi_fpflag_ec': 'EphemerisMatchFlag',
        'koi_period': 'OrbitalPeriod_days',
        'koi_period_err1': 'OrbitalPeriod_err1',
        'koi_period_err2': 'OrbitalPeriod_err2',
        'koi_time0bk': 'TransitEpoch_BJD',
        'koi_time0bk_err1': 'TransitEpoch_err1',
        'koi_time0bk_err2': 'TransitEpoch_err2',
        'koi_impact': 'ImpactParameter',
        'koi_impact_err1': 'ImpactParameter_err1',
        'koi_impact_err2': 'ImpactParameter_err2',
        'koi_duration': 'TransitDuration_hrs',
        'koi_duration_err1': 'TransitDuration_err1',
        'koi_duration_err2': 'TransitDuration_err2',
        'koi_depth': 'TransitDepth_ppm',
        'koi_depth_err1': 'TransitDepth_err1',
        'koi_depth_err2': 'TransitDepth_err2',
        'koi_prad': 'PlanetaryRadius_EarthRadii',
        'koi_prad_err1': 'PlanetaryRadius_err1',
        'koi_prad_err2': 'PlanetaryRadius_err2',
        'koi_teq': 'EquilibriumTemp_K',
        'koi_insol': 'InsolationFlux_EarthFlux',
        'koi_insol_err1': 'InsolationFlux_err1',
        'koi_insol_err2': 'InsolationFlux_err2',
        'koi_model_snr': 'TransitSNR',
        'koi_tce_plnt_num': 'TCEPlanetNumber',
        'koi_steff': 'StellarTemp_K',
        'koi_steff_err1': 'StellarTemp_err1',
        'koi_steff_err2': 'StellarTemp_err2',
        'koi_slogg': 'StellarLogG',
        'koi_slogg_err1': 'StellarLogG_err1',
        'koi_slogg_err2': 'StellarLogG_err2',
        'koi_srad': 'StellarRadius_SolarRadii',
        'koi_srad_err1': 'StellarRadius_err1',
        'koi_srad_err2': 'StellarRadius_err2',
        'ra': 'RA_deg',
        'dec': 'Dec_deg',
        'koi_kepmag': 'KeplerMagnitude'
    }

    # Rename the columns
    df.rename(columns=new_column_names, inplace=True)

    # Fill all null (NaN) values with 0
    df.fillna(0, inplace=True)

    # Save the preprocessed data to a new CSV file
    df.to_csv('preprocessed_sample.csv', index=False)

    print("Successfully created 'preprocessed_sample.csv' with new column names and null values replaced by 0.")

except FileNotFoundError:
    print("Error: 'filtered_sample.csv' not found. Please ensure the file exists.")
except Exception as e:
    print(f"An error occurred: {e}")
