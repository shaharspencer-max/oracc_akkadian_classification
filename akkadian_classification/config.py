
"""
Configuration for Akkadian Classification Package
Contains global constants, file paths, and region definitions.
"""
import os

# =========================
# FILE PATHS
# =========================
# Use raw strings for Windows paths
PROJECT_ROOT = r"C:\Users\shaha\PycharmProjects\thesis"
SOURCE_DATA_DIR = os.path.join(PROJECT_ROOT, r"oracc_akkadian_classification\src\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 4 - fixing sender location and recreating train+test")
METADATA_DIR = os.path.join(PROJECT_ROOT, r"oracc_preprocessing\data\metadata_preprocessing")

FIRST_MIL_CSV = os.path.join(SOURCE_DATA_DIR, "first_millennium_oracc_tablets_gn__and_en_masked_with_mapped_city_filters.csv")
PLEIADES_CSV = os.path.join(METADATA_DIR, "provenances_to_plaides_data_mapping.csv")

# =========================
# UTILITIES
# =========================
COLOR_MAP = {
    'Babylonia (North)': '#3cb44b',      # Green
    'Babylonia (South)': '#bfef45',      # Lime
    'Assyria': '#ffe119',                # Yellow
    'Assyria (Periphery)': '#9A6324',    # Brown
    'Upper Mesopotamia': '#f58231',      # Orange
    'Middle Euphrates': '#800000',       # Maroon
    'Syria': '#42d4f4',                  # Cyan
    'Syria (Periphery)': '#469990',      # Teal
    'Levant': '#4363d8',                 # Blue
    'Anatolia': '#000075',               # Navy
    'Eastern Mesopotamia': '#e6194b',    # Red
    'Iran/Elam': '#911eb4',              # Purple
    'Arabia': '#f032e6',                 # Magenta
}

# =========================
# REGION MAPPING (106 Cities)
# =========================
REGION_MAP = {
    # Babylonia (North)
    'Akkad': 'Babylonia (North)', 'Babylon': 'Babylonia (North)', 'Sippar': 'Babylonia (North)', 
    'Kish': 'Babylonia (North)', 'Borsippa': 'Babylonia (North)', 'Kutha': 'Babylonia (North)', 
    'Dilbat': 'Babylonia (North)', 'Dur-Kurigalzu': 'Babylonia (North)', 'Marad': 'Babylonia (North)',
    
    # Babylonia (South)
    'Uruk': 'Babylonia (South)', 'Ur': 'Babylonia (South)', 'Nippur': 'Babylonia (South)', 
    'Larsa': 'Babylonia (South)', 'Isin': 'Babylonia (South)', 'Kissik': 'Babylonia (South)',
    'Larak': 'Babylonia (South)', 
    
    # Eastern Mesopotamia (Diyala)
    'Der': 'Eastern Mesopotamia', 'Me-Turran': 'Eastern Mesopotamia',
    'Tell Baradan': 'Eastern Mesopotamia',
    'Lahiru': 'Eastern Mesopotamia', # Moved from Assyria
    'Tell Satu Qala': 'Eastern Mesopotamia',
    
    # Assyria (Core)
    'Assur': 'Assyria', 'Nineveh': 'Assyria', 'Nimrud': 'Assyria', 
    'Dur-Sharrukin': 'Assyria', 'Arbela': 'Assyria', 'Kilizu': 'Assyria', 
    'Tarbisu': 'Assyria', 'Balāwāt': 'Assyria', 'Arrapha': 'Assyria',
    'Jerwan': 'Assyria', 'Bavian': 'Assyria', 'Negub Tunnel': 'Assyria',
    'Wadi Bastura Tunnel': 'Assyria', 'Tell Billa': 'Assyria',
    
    # Assyria (Periphery)
    'Judi Dagh': 'Assyria (Periphery)', 'Dohuk': 'Assyria (Periphery)',
    'Muṣaṣir': 'Assyria (Periphery)', 
    'Mila Mergi': 'Assyria (Periphery)',
    
    # Upper Mesopotamia (Jazira)
    'Dur-Katlimmu': 'Upper Mesopotamia', 'Guzana': 'Upper Mesopotamia', 
    'Huzirina': 'Upper Mesopotamia', 'Harran/Carrhae': 'Upper Mesopotamia', 
    'Tušhan': 'Upper Mesopotamia', 'Tell Barri': 'Upper Mesopotamia', 
    'Kurkh': 'Upper Mesopotamia', 
    'Tell Abu Marya': 'Upper Mesopotamia', 'Tell Ajaja': 'Upper Mesopotamia', 
    'Tell Fakhariyah': 'Upper Mesopotamia', 'Tell al-Hawa': 'Upper Mesopotamia', 
    'Tigris Tunnel': 'Upper Mesopotamia', 'Tell Rimah': 'Upper Mesopotamia', 
    'Tell Abta': 'Upper Mesopotamia', 'Naṣibina': 'Upper Mesopotamia', 'Raṣappa': 'Upper Mesopotamia',
    'Pāra': 'Upper Mesopotamia', 'Sabaʾa': 'Upper Mesopotamia',
    'Samarra': 'Upper Mesopotamia', 'Tikrit': 'Upper Mesopotamia',
    
    # Middle Euphrates
    'Hindanu': 'Middle Euphrates', 'Ana': 'Middle Euphrates', 'Sur Jureh': 'Middle Euphrates',
    'Judeideh': 'Middle Euphrates', 'Dawali': 'Middle Euphrates', 'Zawiyeh': 'Middle Euphrates',
    
    # Syria
    'Til Barsip': 'Syria', 'Carchemish': 'Syria', 'Arslan Tash': 'Syria',
    'Tell Tayinat': 'Syria', 'Turlu Höyük': 'Syria', 'Burmarina': 'Syria',
    'Marqasu': 'Syria', 'Zincirli': 'Syria', 'Tunip': 'Syria', 'Arpadda': 'Syria',
    'Hamath': 'Syria', 'Manṣuate': 'Syria', 'Damascus': 'Syria',
    'Antakya': 'Syria', 'el-Ghab': 'Syria',
    
    # Syria (Periphery)
    'Kizkapanlı': 'Syria (Periphery)', 'Kenk Boǧazı': 'Syria (Periphery)',
    
    # Levant
    'Byblos': 'Levant', 'Samaria': 'Levant', 'Ashdod': 'Levant', 'Larnaka': 'Levant', 
    'Nahr el-Kelb': 'Levant', 'Brissa': 'Levant', 'Selaʾ': 'Levant', 'Ben Shemen': 'Levant',
    'Simyra': 'Levant',
    
    # Iran/Elam
    'Persepolis': 'Iran/Elam', 'Susa': 'Iran/Elam', 'Naqsh-I Rustam': 'Iran/Elam', 
    'Luristan': 'Iran/Elam', 'Zalu-Ab': 'Iran/Elam', 'Elam': 'Iran/Elam',
    'Qalʾeh-i Imam': 'Iran/Elam', 'Tang-i Var': 'Iran/Elam', 'Kalmākarra': 'Iran/Elam', 
    'Najafabad': 'Iran/Elam',
    
    # Anatolia
    'Daskyleion': 'Anatolia', 'Melid': 'Anatolia',
    'Urartu': 'Anatolia',
    
    # Arabia
    'Tayma': 'Arabia', 'Padakku': 'Arabia'
}

# =========================
# MANUAL DATA OVERRIDES
# =========================
MANUAL_DATA = {
    'Larak': {'lat': 32.31275, 'lon': 45.661, 'pid': '893998'}, # Corrections
}
