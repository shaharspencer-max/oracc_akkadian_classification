
"""
Data Loading Module
Handles loading and merging of city data from First Millennium and Pleiades sources.
"""
import pandas as pd
import warnings
from . import config

def load_city_data():
    """
    Loads city data, applies region mapping, and merges with Pleiades metadata.
    Returns a DataFrame with columns: [city, region, lat, lon, pleiades_id, text_count]
    """
    print("Loading data from CSVs...")
    
    # 1. Load First Millennium Data (Source of Truth for City List)
    try:
        df_texts = pd.read_csv(config.FIRST_MIL_CSV)
    except FileNotFoundError:
        print(f"Error: First Millennium CSV not found at {config.FIRST_MIL_CSV}")
        return pd.DataFrame()

    unique_cities = df_texts['city'].dropna().unique()
    
    # 2. Load Pleiades Metadata
    try:
        df_pleiades = pd.read_csv(config.PLEIADES_CSV).fillna('')
    except FileNotFoundError:
        print(f"Error: Pleiades CSV not found at {config.PLEIADES_CSV}")
        return pd.DataFrame()

    pleiades_lookup = {}
    for _, row in df_pleiades.iterrows():
        c = row['city_name']
        # Handle string coords if necessary, but assuming float based on inspection
        pleiades_lookup[c] = {
            'lat': row['lat'],
            'lon': row['lon'],
            'pid': str(row['plaides_id'])
        }

    # 3. Merge and Clean
    clean_data = []
    
    for city in unique_cities:
        # Determine Region
        region = config.REGION_MAP.get(city)
        if not region:
            continue # Skip unmapped cities (ensure strictly 106)
            
        lat, lon, pid = None, None, None
        
        # Check Manual Overrides
        if city in config.MANUAL_DATA:
            m = config.MANUAL_DATA[city]
            lat, lon, pid = m['lat'], m['lon'], m['pid']
        # Check Pleiades Lookup
        elif city in pleiades_lookup:
            p = pleiades_lookup[city]
            try:
                lat = float(p['lat'])
                lon = float(p['lon'])
                pid = p['pid']
                if not pid.isdigit(): pid = '0'
            except (ValueError, TypeError):
                pass
        
        if lat is not None and lon is not None:
             clean_data.append({
                'city': city,
                'region': region,
                'lat': lat,
                'lon': lon,
                'pleiades_id': pid,
                'text_count': len(df_texts[df_texts['city'] == city])
            })
    
    df_result = pd.DataFrame(clean_data)
    print(f"Data Loaded: {len(df_result)} cities.")
    return df_result
