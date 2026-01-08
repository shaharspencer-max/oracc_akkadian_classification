
"""
Test Region Groupings (REFACTORED - FINAL 106)
- Validation of Manual Region Assignments
- Map Generation with Search and Zoom
- Strict dataset coverage (106 cities with valid Pleiades IDs)
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import Search
import warnings
import os
import webbrowser

warnings.filterwarnings("ignore")

# ==========================================
# CONFIGURATION
# ==========================================

FIRST_MIL_CSV = r"C:\Users\shaha\PycharmProjects\thesis\oracc_akkadian_classification\src\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 4 - fixing sender location and recreating train+test\first_millennium_oracc_tablets_gn__and_en_masked_with_mapped_city_filters.csv"
PLEIADES_CSV = r"C:\Users\shaha\PycharmProjects\thesis\oracc_preprocessing\data\metadata_preprocessing\provenances_to_plaides_data_mapping.csv"
OUTPUT_HTML = r"region_groupings_map.html"

# Color Palette (Distinct 13 regions)
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

# Full Region Map (106 Cities)
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
    
    # Assyria (Core)
    'Assur': 'Assyria', 'Nineveh': 'Assyria', 'Nimrud': 'Assyria', 
    'Dur-Sharrukin': 'Assyria', 'Arbela': 'Assyria', 'Kilizu': 'Assyria', 
    'Tarbisu': 'Assyria', 'Balāwāt': 'Assyria', 'Arrapha': 'Assyria',
    'Jerwan': 'Assyria', 'Bavian': 'Assyria', 'Negub Tunnel': 'Assyria',
    'Wadi Bastura Tunnel': 'Assyria', 'Tell Billa': 'Assyria',
    
    # Assyria (Periphery)
    'Judi Dagh': 'Assyria (Periphery)', 'Dohuk': 'Assyria (Periphery)',
    'Lahiru': 'Assyria (Periphery)', 'Muṣaṣir': 'Assyria (Periphery)', 
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
    'Tell Satu Qala': 'Middle Euphrates',
    
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

# Manual Data Overrides (Only for Larak, as requested)
MANUAL_DATA = {
    'Larak': {'lat': 32.31275, 'lon': 45.661, 'pid': '893998'}, # User corrected
}

# ==========================================
# PROCESSING
# ==========================================

def load_data():
    print("Loading data...")
    # 1. Get List of Cities from Texts
    df_texts = pd.read_csv(FIRST_MIL_CSV)
    unique_cities = df_texts['city'].dropna().unique()
    print(f"Found {len(unique_cities)} unique cities in first millennium texts.")
    
    # 2. Get Pleiades Metadata
    df_pleiades = pd.read_csv(PLEIADES_CSV).fillna('')
    pleiades_lookup = {}
    for _, row in df_pleiades.iterrows():
        c = row['city_name']
        pleiades_lookup[c] = {
            'lat': row['lat'],
            'lon': row['lon'],
            'pid': str(row['plaides_id'])
        }
        
    # 3. Merge
    clean_data = []
    
    for city in unique_cities:
        # Determine Region
        region = REGION_MAP.get(city)
        if not region:
            # Skip if not in our defined 106 list
            continue
            
        lat, lon, pid = None, None, None
        
        # Check Manual Overrides first
        if city in MANUAL_DATA:
            m = MANUAL_DATA[city]
            lat, lon, pid = m['lat'], m['lon'], m['pid']
        # Check Pleiades lookup
        elif city in pleiades_lookup:
            p = pleiades_lookup[city]
            # Verify validity
            try:
                lat = float(p['lat'])
                lon = float(p['lon'])
                pid = p['pid']
                if not pid.isdigit(): pid = '0'
            except:
                pass # Invalid data in CSV
        
        if lat is not None and lon is not None:
            clean_data.append({
                'city': city,
                'region': region,
                'lat': lat,
                'lon': lon,
                'pleiades_id': pid,
                'text_count': len(df_texts[df_texts['city'] == city])
            })
        else:
            print(f"[ERROR] Could not find coordinates for included city '{city}'")

    print(f"Prepared data for {len(clean_data)} cities (Target: 106).")
    return pd.DataFrame(clean_data)

def generate_map(df):
    print("Generating map...")
    
    m = folium.Map(location=[34, 44], zoom_start=6, tiles='CartoDB positron')
    
    # Add Markers
    for _, row in df.iterrows():
        color = COLOR_MAP.get(row['region'], 'gray')
        
        pid = row['pleiades_id']
        pid_link = ""
        if pid and pid != '0':
            pid_link = f'<br><a href="https://pleiades.stoa.org/places/{pid}" target="_blank">Pleiades: {pid}</a>'
            
        popup_html = f"""
        <div style="font-family: Arial; min-width: 150px;">
            <h4>{row['city']}</h4>
            <b>Region:</b> {row['region']}<br>
            {pid_link}
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['city']} ({row['region']})"
        ).add_to(m)
        
    # Legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; font-size:14px; background-color:white; padding: 10px; border: 2px solid grey; border-radius:5px;">
    <b>Regions</b><br>
    '''
    for region, color in COLOR_MAP.items():
        legend_html += f'<i style="background:{color};width:12px;height:12px;display:inline-block;"></i> {region}<br>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Search Panel
    add_search_panel(m, df)
    
    return m

def add_search_panel(m, df):
    list_html = '''
    <div id="cityPanel" style="position:fixed;top:10px;right:10px;background:white;padding:15px;border:1px solid grey;z-index:9999;max-height:80vh;overflow-y:auto;width:280px;font-size:12px;box-shadow:0 0 10px rgba(0,0,0,0.2);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <b style="font-size:14px;">Cities by Region</b>
            <button onclick="document.getElementById('cityPanel').style.display='none'" style="border:none;background:none;cursor:pointer;font-size:16px;">×</button>
        </div>
        <input type="text" id="citySearch" onkeyup="filterCities()" placeholder="Search..." style="width:90%;padding:5px;margin-bottom:10px;border:1px solid #ccc;border-radius:4px;">
        <div id="cityListContent">
    '''
    
    regions = sorted(df['region'].unique())
    for region in regions:
        color = COLOR_MAP.get(region, 'black')
        region_df = df[df['region'] == region].sort_values('city')
        list_html += f'<div class="region-block"><b style="color:{color}">{region} ({len(region_df)})</b><ul style="padding-left:15px;margin-top:5px;">'
        
        for _, row in region_df.iterrows():
            list_html += f'<li style="cursor:pointer;color:#333;" onmouseover="this.style.color=\'blue\'" onmouseout="this.style.color=\'#333\'" onclick="zoomToCity({row["lat"]}, {row["lon"]})">{row["city"]}</li>'
        list_html += '</ul></div>'
        
    list_html += '</div></div>'
    
    script = '''
    <script>
    var mapObject;
    function findMap() {
        for (var key in window) {
            if (key.startsWith('map_')) {
                mapObject = window[key];
                return;
            }
        }
    }
    function zoomToCity(lat, lon) {
        if (!mapObject) findMap();
        if (mapObject) {
            mapObject.closePopup();
            mapObject.flyTo([lat, lon], 10);
        }
    }
    function filterCities() {
        var input, filter, container, regionBlocks, ul, li, i, j, txtValue;
        input = document.getElementById("citySearch");
        filter = input.value.toUpperCase();
        container = document.getElementById("cityListContent");
        regionBlocks = container.getElementsByClassName("region-block");
        
        for (i = 0; i < regionBlocks.length; i++) {
            var hasVisibleCity = false;
            ul = regionBlocks[i].getElementsByTagName("ul")[0];
            li = ul.getElementsByTagName("li");
            for (j = 0; j < li.length; j++) {
                txtValue = li[j].textContent || li[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    li[j].style.display = "";
                    hasVisibleCity = true;
                } else {
                    li[j].style.display = "none";
                }
            }
            if (hasVisibleCity) {
                regionBlocks[i].style.display = "";
            } else {
                regionBlocks[i].style.display = "none";
            }
        }
    }
    setTimeout(findMap, 1000);
    </script>
    '''
    
    toggle_btn = '<button onclick="document.getElementById(\'cityPanel\').style.display=\'block\'" style="position:fixed;top:10px;right:10px;z-index:9998;padding:8px 12px;background:#007bff;color:white;border:none;border-radius:4px;cursor:pointer;">Show List</button>'

    m.get_root().html.add_child(folium.Element(list_html + script))
    m.get_root().html.add_child(folium.Element(toggle_btn))

def main():
    print("====================================")
    print("REGION MAP GENERATOR (FINAL 106)")
    print("====================================")
    
    df = load_data()
    m = generate_map(df)
    m.save(OUTPUT_HTML)
    
    print("\nSUMMARY:")
    count = len(df)
    print(f"Total Cities Mapped: {count}")
    if count == 106:
        print("[SUCCESS] Exact count of 106 reached.")
    else:
        print(f"[WARNING] Count is {count}, expected 106.")
        
    print(df['region'].value_counts())

if __name__ == "__main__":
    main()
