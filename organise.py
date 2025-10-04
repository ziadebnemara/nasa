import numpy as np
import pandas as pd

data1 = pd.read_csv("data1_clean.csv")
data2 = pd.read_csv("data2_clean.csv")









def noise_ppm_from_tmag(tmag, noise_floor=60.0):
    """
    Rough per-hour noise approximation (ppm).
    This is a simple parametric model:
      - bright stars approach noise_floor (ppm)
      - noise increases exponentially with magnitude
    You can replace this with an empirical CDPP curve for best results.
    """
    if pd.isna(tmag):
        return 200.0  # fallback if no magnitude
    # tunable parameters (feel free to tweak)
    # noise = noise_floor * 10**(0.2*(tmag - t0))
    t0 = 10.0
    # keep it bounded
    noise = noise_floor * 10 ** (0.2 * (tmag - t0))
    noise = np.clip(noise, noise_floor, 1e5)
    return noise

def compute_snr_proxy_for_row(row):
    # 1) transit depth in ppm
    depth_ppm = row.get("pl_trandep")

    # 2) number of transits
    period_days = row.get("pl_orbper")
    n_transits = max(1.0, np.floor(27.4 / period_days))

    # 3) per-point noise estimate (ppm)
    tmag = row.get("st_tmag")
    noise_per_hour_ppm = noise_ppm_from_tmag(tmag)  # default floor
    # convert noise per hour to noise over transit duration:
    dur_hours = row.get("pl_trandurh")

    # number of effective independent points during transit:
    n_points_in_transit = max(1.0, dur_hours / 0.5)
    # noise over the transit scales ~ noise_per_hour / sqrt(n_points)
    noise_per_transit_ppm = noise_per_hour_ppm / np.sqrt(n_points_in_transit)

    # 4) proxy SNR
    snr = (depth_ppm / noise_per_transit_ppm) * np.sqrt(n_transits)
    return snr

# Apply to dataframe
def add_snr_proxy_column(df):
    df = df.copy()
    snrs = []
    for _, row in df.iterrows():
        snr_val = compute_snr_proxy_for_row(row)
        snrs.append(snr_val)
    df["snr_proxy"] = snrs
    return df

data2 = add_snr_proxy_column(data2)









data1.rename(columns={
    "koi_disposition": "disposition",
    "koi_period": "period",
    "koi_duration": "duration",
    "koi_depth": "depth",
    "koi_prad": "planet_radius",
    "koi_steff": "stellar_temperature",
    "koi_slogg": "stellar_gravity",
    "koi_srad": "stellar_radius",
    "koi_kepmag": "magnitude",
    "koi_model_snr": "snr",
    "koi_teq": "equilibrium_temp",
    # "snr_proxy_log": "snr_log"
}, inplace=True)

data2.rename(columns={
    "tfopwg_disp": "disposition",
    "pl_orbper": "period",
    "pl_trandurh": "duration",
    "pl_trandep": "depth",
    "pl_rade": "planet_radius",
    "st_teff": "stellar_temperature",
    "st_logg": "stellar_gravity",
    "st_rad": "stellar_radius",
    "st_tmag": "magnitude",
    "snr_proxy": "snr",
    "pl_eqt": "equilibrium_temp",
    # "snr_proxy_log": "snr_log"
}, inplace=True)



data3 = pd.concat([data1, data2], axis=0)

# print(data1)
# print(data2)
print(data3)

data3.to_csv("clean.csv", index=False)