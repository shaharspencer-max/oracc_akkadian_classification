"""Geographic region mappings for Akkadian cities.

Based on Assyriological expertise with 106 cities mapped to 9 regions.
Data validated against Pleiades Gazetteer geographic coordinates.
"""

# Manual Region Map - Cities from first millennium dataframe with valid Pleiades IDs only (106 cities)
REGION_MAP = {
    # Babylonia (North)
    'Akkad': 'Babylonia (North)',
    'Babylon': 'Babylonia (North)',
    'Sippar': 'Babylonia (North)',
    'Kish': 'Babylonia (North)',
    'Borsippa': 'Babylonia (North)',
    'Kutha': 'Babylonia (North)',
    'Dilbat': 'Babylonia (North)',
    'Dur-Kurigalzu': 'Babylonia (North)',
    'Marad': 'Babylonia (North)',
    
    # Babylonia (South)
    'Uruk': 'Babylonia (South)',
    'Ur': 'Babylonia (South)',
    'Nippur': 'Babylonia (South)',
    'Larsa': 'Babylonia (South)',
    'Isin': 'Babylonia (South)',
    'Kissik': 'Babylonia (South)',
    'Der': 'Babylonia (South)',
    'Me-Turran': 'Babylonia (South)',
    'Larak': 'Babylonia (South)',
    
    # Assyria (Heartland)
    'Assur': 'Assyria (Heartland)',
    'Nineveh': 'Assyria (Heartland)',
    'Nimrud': 'Assyria (Heartland)',
    'Dur-Sharrukin': 'Assyria (Heartland)',
    'Arbela': 'Assyria (Heartland)',
    'Kilizu': 'Assyria (Heartland)',
    'Tarbisu': 'Assyria (Heartland)',
    'Balāwāt': 'Assyria (Heartland)',
    'Arrapha': 'Assyria (Heartland)',
    
    # Assyria (Provinces)
    'Jerwan': 'Assyria (Provinces)',
    'Bavian': 'Assyria (Provinces)',
    'Negub Tunnel': 'Assyria (Provinces)',
    'Judi Dagh': 'Assyria (Provinces)',
    'Wadi Bastura Tunnel': 'Assyria (Provinces)',
    'Dohuk': 'Assyria (Provinces)',
    'Tell Billa': 'Assyria (Provinces)',
    'Lahiru': 'Assyria (Provinces)',
    'Muṣaṣir': 'Assyria (Provinces)',
    
    # Upper Mesopotamia
    'Dur-Katlimmu': 'Upper Mesopotamia',
    'Guzana': 'Upper Mesopotamia',
    'Huzirina': 'Upper Mesopotamia',
    'Harran/Carrhae': 'Upper Mesopotamia',
    'Tušhan': 'Upper Mesopotamia',
    'Tell Barri': 'Upper Mesopotamia',
    'Tell Satu Qala': 'Upper Mesopotamia',
    'Kurkh': 'Upper Mesopotamia',
    'Tell Abu Marya': 'Upper Mesopotamia',
    'Tell Ajaja': 'Upper Mesopotamia',
    'Tell Fakhariyah': 'Upper Mesopotamia',
    'Tell al-Hawa': 'Upper Mesopotamia',
    'Tigris Tunnel': 'Upper Mesopotamia',
    'Tell Rimah': 'Upper Mesopotamia',
    'Tell Abta': 'Upper Mesopotamia',
    'Naṣibina': 'Upper Mesopotamia',
    'Raṣappa': 'Upper Mesopotamia',
    'Hindanu': 'Upper Mesopotamia',
    
    # Syria
    'Til Barsip': 'Syria',
    'Carchemish': 'Syria',
    'Arslan Tash': 'Syria',
    'Tell Tayinat': 'Syria',
    'Turlu Höyük': 'Syria',
    'Burmarina': 'Syria',
    'Marqasu': 'Syria',
    'Zincirli': 'Syria',
    'Tunip': 'Syria',
    'Arpadda': 'Syria',
    'Hamath': 'Syria',
    'Simyra': 'Syria',
    'Manṣuate': 'Syria',
    'Damascus': 'Syria',
    
    # Levant
    'Byblos': 'Levant',
    'Samaria': 'Levant',
    'Ashdod': 'Levant',
    'Larnaka': 'Levant',
    'Nahr el-Kelb': 'Levant',
    'Brissa': 'Levant',
    'Selaʾ': 'Levant',
    'Ben Shemen': 'Levant',
    'Antakya': 'Levant',
    'Judeideh': 'Levant',
    'Sur Jureh': 'Levant',
    'el-Ghab': 'Levant',
    
    # Iran/Elam
    'Persepolis': 'Iran/Elam',
    'Susa': 'Iran/Elam',
    'Naqsh-I Rustam': 'Iran/Elam',
    'Luristan': 'Iran/Elam',
    'Zalu-Ab': 'Iran/Elam',
    'Elam': 'Iran/Elam',
    'Qalʾeh-i Imam': 'Iran/Elam',
    'Tang-i Var': 'Iran/Elam',
    'Kalmākarra': 'Iran/Elam',
    'Najafabad': 'Iran/Elam',
    
    # Anatolia
    'Daskyleion': 'Anatolia',
    'Melid': 'Anatolia',
    'Kizkapanlı': 'Anatolia',
    'Kenk Boǧazı': 'Anatolia',
    'Urartu': 'Anatolia',
    
    # Other
    'Tayma': 'Other',
    'Padakku': 'Other',
    'Pāra': 'Other',
    'Sabaʾa': 'Other',
    'Mila Mergi': 'Other',
    'Tell Baradan': 'Other',
    'Samarra': 'Other',
    'Tikrit': 'Other',
    'Ana': 'Other',
    'Dawali': 'Other',
    'Zawiyeh': 'Other'
}


# Reverse mapping: region -> list of cities
REGIONS = {
    'Babylonia (North)': [
        'Akkad', 'Babylon', 'Sippar', 'Kish', 'Borsippa', 'Kutha',
        'Dilbat', 'Dur-Kurigalzu', 'Marad'
    ],
    'Babylonia (South)': [
        'Uruk', 'Ur', 'Nippur', 'Larsa', 'Isin', 'Kissik',
        'Der', 'Me-Turran', 'Larak'
    ],
    'Assyria (Heartland)': [
        'Assur', 'Nineveh', 'Nimrud', 'Dur-Sharrukin', 'Arbela', 'Kilizu',
        'Tarbisu', 'Balāwāt', 'Arrapha'
    ],
    'Assyria (Provinces)': [
        'Jerwan', 'Bavian', 'Negub Tunnel', 'Judi Dagh', 'Wadi Bastura Tunnel',
        'Dohuk', 'Tell Billa', 'Lahiru', 'Muṣaṣir'
    ],
    'Upper Mesopotamia': [
        'Dur-Katlimmu', 'Guzana', 'Huzirina', 'Harran/Carrhae', 'Tušhan',
        'Tell Barri', 'Tell Satu Qala', 'Kurkh', 'Tell Abu Marya', 'Tell Ajaja',
        'Tell Fakhariyah', 'Tell al-Hawa', 'Tigris Tunnel', 'Tell Rimah',
        'Tell Abta', 'Naṣibina', 'Raṣappa', 'Hindanu'
    ],
    'Syria': [
        'Til Barsip', 'Carchemish', 'Arslan Tash', 'Tell Tayinat', 'Turlu Höyük',
        'Burmarina', 'Marqasu', 'Zincirli', 'Tunip', 'Arpadda',
        'Hamath', 'Simyra', 'Manṣuate', 'Damascus'
    ],
    'Levant': [
        'Byblos', 'Samaria', 'Ashdod', 'Larnaka', 'Nahr el-Kelb', 'Brissa',
        'Selaʾ', 'Ben Shemen', 'Antakya', 'Judeideh', 'Sur Jureh', 'el-Ghab'
    ],
    'Iran/Elam': [
        'Persepolis', 'Susa', 'Naqsh-I Rustam', 'Luristan', 'Zalu-Ab', 'Elam',
        'Qalʾeh-i Imam', 'Tang-i Var', 'Kalmākarra', 'Najafabad'
    ],
    'Anatolia': [
        'Daskyleion', 'Melid', 'Kizkapanlı', 'Kenk Boǧazı', 'Urartu'
    ],
    'Other': [
        'Tayma', 'Padakku', 'Pāra', 'Sabaʾa', 'Mila Mergi', 'Tell Baradan',
        'Samarra', 'Tikrit', 'Ana', 'Dawali', 'Zawiyeh'
    ]
}


def get_region(city: str) -> str:
    """Get the region for a given city.
    
    Args:
        city: City name
    
    Returns:
        Region name or 'Unknown' if city not in map
    """
    return REGION_MAP.get(city, 'Unknown')


def get_cities_in_region(region: str) -> list[str]:
    """Get all cities in a given region.
    
    Args:
        region: Region name
    
    Returns:
        List of city names in the region
    """
    return REGIONS.get(region, [])
