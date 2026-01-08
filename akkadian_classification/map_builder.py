
"""
Map Builder Module
Handles the generation of the interactive Folium map.
"""
import folium
from folium.plugins import Search
import pandas as pd
from . import config

def build_map(df, output_path=None):
    """
    Generates a Folium map from the city DataFrame.
    Returns the map object. Saves to file if output_path is provided.
    """
    print("Building Map...")
    
    # Center map (Baghdad approx)
    m = folium.Map(location=[34, 44], zoom_start=6, tiles='CartoDB positron')
    
    # Add Markers
    for _, row in df.iterrows():
        color = config.COLOR_MAP.get(row['region'], 'gray')
        
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
        
    _add_legend(m)
    _add_search_panel(m, df)
    
    if output_path:
        print(f"Saving map to {output_path}...")
        m.save(output_path)
        
    return m

def _add_legend(m):
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index:9999; font-size:14px; background-color:white; padding: 10px; border: 2px solid grey; border-radius:5px;">
    <b>Regions</b><br>
    '''
    for region, color in config.COLOR_MAP.items():
        legend_html += f'<i style="background:{color};width:12px;height:12px;display:inline-block;"></i> {region}<br>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

def _add_search_panel(m, df):
    # Construct HTML for side panel
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
        color = config.COLOR_MAP.get(region, 'black')
        region_df = df[df['region'] == region].sort_values('city')
        list_html += f'<div class="region-block"><b style="color:{color}">{region} ({len(region_df)})</b><ul style="padding-left:15px;margin-top:5px;">'
        
        for _, row in region_df.iterrows():
            list_html += f'<li style="cursor:pointer;color:#333;" onmouseover="this.style.color=\'blue\'" onmouseout="this.style.color=\'#333\'" onclick="zoomToCity({row["lat"]}, {row["lon"]})">{row["city"]}</li>'
        list_html += '</ul></div>'
        
    list_html += '</div></div>'
    
    # Add Scripts
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
