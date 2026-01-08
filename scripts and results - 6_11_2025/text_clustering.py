# labana - lebanon
# Amurru - very borad and unspecific
# shay can show me where to find the coordinates for cities missing coordinates



# regarding cities withought provinience - we can try to keep the mapping of the provinience, but with some questin mark.
# how can we encode uncertainty? gabi says we show not keep them at all.
# there is a theory that most people did not go more than 1-2 days walk from their house.
# it could be interesting to do clustering that takes into account geogrpahy: ex. rivers - put distance of infinity.
# e.g. add topography of the שטח.
# פה יש שרשרת הרים שהמרחק הוא אינסוף, אף אחד לא יעבור על זה - אפשר למפות מרחק תרבותי.
# יש תחום מחקר שנקרא least cost paths analysis - זה הכל מאוד מתמטי כי זה התחיל מleast squares, בטח יש את זה במפות מודרניות. שי ישלח לי ספר שיצא לאחרונה שבדיוק מדבר על המזרח הקדום - איך לעשות חישובים של מרחק תרבותי. יש דוקטורנט שמנסה לעשות מרחק של 100 קילומטר מסביב לתל שהוא חופר.
# usvs - government agency that deals with מיפוי ולווינים
# ויש להם המון דאטא
# בחומרים של הקורס של הremote sensing יש המון דברים שמאפשרים למצוא מפות ומאפיינים טופולוגיים.
# זה בעיקר מבוסס על תמונות לווין
#
# המטרה היא בעצם לחזות את הקלאסרטים , אבל גם לתת "סוגי טעות" - יש טעויות יותר חמורות ופחות חמורות. מישהו בקלאסטר שלי זה יותר בסדר.
# שי ישלח לי קישור למקום שאוסף חומרים ואז אני יכולה להתחיל להוציא את המידע הטופוגרפי שמסביר את פני השטח ואז אני אוכל לקחת את זה בחשבון כשאני לוקחת

#  לבדוק מה עשו מבחינת gepgrpahic prediction - הכי טוב לקחת מטריקה קיימת.
# גיאוגרפיה זה משהו שאנשים מתעסקים איתו כבר הרבה שנים. כדאי לנסות לראות מה עשו - זה טוב לנו בכל מקרה.
#  אנחנו צריכים שהמודל ינסה לחזות את הx אחוז של הדאטא. ואנחנו צריכים להבין מה המטריקה שלנו - מבקשים לחזות קואורדינטות? עיר? מיקום יותר כללי? ואיך נותנים ציונים? - 0 או 1, משהו על סקאלה.
#
# צריך לראות מה יש שלא קשור רק
#
# # מבחינת המטריקה
# למזרח הקרוב הקדום

# עשו פרסומים של machine learning על מפות.
# acm sig spacial -

# הכי טוב זה למצוא עבודה מצוטטת - מטריקות גיאוגרפיות זה הכי טוב (לא בתוך הקלאסטר). אנחנו צריכים: 1. איך לתת ציון, 2. איך לבקש מהמודל שייתן לנו תשובה.

# גבי ממליץ להסתכל על מה הכי מצוטט - ושהרבה עושים את זה.




import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import haversine_distances
import folium
from folium.plugins import Search
import html
import os
import webbrowser
from tabulate import tabulate
import warnings
warnings.filterwarnings("ignore")
pd.set_option('display.notebook_repr_html', True)



def clean_datframe_from_unmapped_cities(dataframe: pd.DataFrame) -> pd.DataFrame:
    print(f"original dataframe shape: {dataframe.shape}")
    unmapped_entries = dataframe[dataframe['city'].isin(['CITY NOT MAPPED YET', 'UNMAPPED', 'Uncertain'])]
    print(f"entries to be removed (unmapped): {len(unmapped_entries)}")
    dataframe = dataframe[~dataframe['city'].isin(['CITY NOT MAPPED YET', 'UNMAPPED', 'Uncertain'])]
    print(f"\ndataframe shape after cleaning texts with no mapped city: {dataframe.shape}")
    return dataframe



def merge_dataframe_with_pleaides_coordinates(dataframe: pd.DataFrame, csv_path_with_pleidaes_data:
str=r"C:\Users\shaha\PycharmProjects\oracc_preprocessing\data\metadata_preprocessing\provenances_to_plaides_data_mapping.csv")->pd.DataFrame:
    provenance_to_plaides_coords_mapping = pd.read_csv(csv_path_with_pleidaes_data)

    dataframe = dataframe.merge(
        provenance_to_plaides_coords_mapping[['city_name', 'lat', 'lon']],
        how='left',
        left_on='city',
        right_on='city_name' )
    original_dataframe_length = len(dataframe)
    dataframe = dataframe.drop(columns=['city_name'])
    missing_coords = dataframe[dataframe['lat'].isna()]['city'].unique()
    len(missing_coords), missing_coords[:10]
    print(f"\nnumber of cities missing coordinates: {len(missing_coords)}")
    print(f"\ncities missing coordinates: {missing_coords}")
    dataframe = dataframe.dropna(subset=['lat', 'lon'])
    new_dataframe_length = len(dataframe)
    print(f"\nlost texts as result of missing coordinates: {original_dataframe_length - new_dataframe_length}")
    print(f"resulting dataframe shape: {dataframe.shape}")
    return dataframe

def get_millenium(row):
    """
    Returns the millennium label for a given year range.
    Example outputs: "First Millennium BCE", "Second Millennium CE"
    """

    writing_start_year, writing_end_year= row["writing_start_year"], row["writing_end_year"]
    if pd.isna(writing_start_year) or pd.isna(writing_end_year):
        return "Unknown"
    # Compute the average year
    average_year = (writing_start_year + writing_end_year) / 2

    if average_year < 0:  # BCE
        # Convert negative year to positive for millennium calculation
        mill = (-average_year - 1) // 1000 + 1
        return f"{int(mill)}{'st' if mill == 1 else 'nd' if mill == 2 else 'rd' if mill == 3 else 'th'} Millennium BCE"
    else:  # CE
        mill = (average_year - 1) // 1000 + 1
        return f"{int(mill)}{'st' if mill == 1 else 'nd' if mill == 2 else 'rd' if mill == 3 else 'th'} Millennium CE"


def map_millenium_to_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe["millenium"] = dataframe.apply(get_millenium, axis=1)
    print(f"\nvalues counts for millenium:")
    print(dataframe["millenium"].value_counts())
    return dataframe


def get_millenium_half(row):
    writing_start_year, writing_end_year = row["writing_start_year"], row["writing_end_year"]

    if pd.isna(writing_start_year) or pd.isna(writing_end_year):
        return -1

    avg_year = (writing_start_year + writing_end_year) / 2

    if avg_year < 0:
        year_in_millennium = (-avg_year) % 1000
    else:
        year_in_millennium = avg_year % 1000

    return 1 if year_in_millennium <= 500 else 2


def cluster_cities(cities_to_cluster_df: pd.DataFrame, max_km: float)->pd.DataFrame:
    coords = cities_to_cluster_df[['lat', 'lon']].to_numpy()
    dist_matrix = haversine_distances(np.radians(coords)) * 6371.0

    model = AgglomerativeClustering(
        n_clusters=None,
        metric='precomputed',
        linkage='complete',
        distance_threshold=max_km
    )
    labels = model.fit_predict(dist_matrix)
    cities_to_cluster_df['cluster'] = labels

    n_clusters = cities_to_cluster_df['cluster'].nunique()
    print(f"\nClusters found: {n_clusters}")
    return cities_to_cluster_df


def visualize_clusters_chrome_search_case_insensitive(
    c_df: pd.DataFrame,
    map_file: str = "clusters_map.html",
    chrome_path: str = None
):
    """
    Visualize clustered cities on a Folium map with:
    - Case-insensitive city search
    - Popups showing cluster ID and number of texts
    - Fully connected cluster lines
    """

    # Compute map center
    center_lat, center_lon = c_df['lat'].mean(), c_df['lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="cartodbpositron")

    # Color palette
    cmap = plt.cm.get_cmap('tab20', 20)
    color_palette = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    color_map = {label: color_palette[label % len(color_palette)] for label in c_df['cluster'].unique()}

    # For search plugin (GeoJSON layer)
    search_features = []

    for cluster_id, group in c_df.groupby('cluster'):
        color = color_map[cluster_id]

        # Collapse duplicate cities (count = number of texts)
        city_group = group.groupby(['city', 'lat', 'lon']).size().reset_index(name='count')

        # === CITY MARKERS ===
        for _, row in city_group.iterrows():
            popup_info = (
                f"<b>City:</b> {html.escape(str(row['city']))}<br>"
                f"<b>Cluster:</b> {cluster_id}<br>"
                f"<b>Number of texts:</b> {row['count']}"
            )

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6,
                color='black',
                fill=True,
                fill_color=color,
                fill_opacity=0.9,
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=row['city']
            ).add_to(m)

            # Add feature for case-insensitive search
            search_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row['lon'], row['lat']]},
                "properties": {
                    "city": row['city'],
                    "city_lower": row['city'].lower(),
                    "cluster": cluster_id,
                    "count": row['count']
                }
            })

        # === FULLY CONNECT CLUSTER CITIES ===
        if len(city_group) > 1:
            coords = city_group[['lat', 'lon']].to_numpy().tolist()
            for (lat1, lon1), (lat2, lon2) in itertools.combinations(coords, 2):
                folium.PolyLine(
                    [(lat1, lon1), (lat2, lon2)],
                    color=color,
                    weight=2,
                    opacity=0.4
                ).add_to(m)

        # === CLUSTER CENTROID LABEL ===
        centroid_lat, centroid_lon = group['lat'].mean(), group['lon'].mean()
        folium.map.Marker(
            [centroid_lat, centroid_lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size:10pt; color:{color}; text-align:center;">Cluster {cluster_id}</div>'
            )
        ).add_to(m)

    # === REFERENCE CIRCLE ===
    folium.Circle(
        radius=100000,
        location=[center_lat, center_lon],
        color="gray",
        weight=2,
        fill=False,
        popup="≈ 100 km"
    ).add_to(m)

    # === SEARCH LAYER (CASE-INSENSITIVE) ===
    search_layer = folium.GeoJson(
        {"type": "FeatureCollection", "features": search_features},
        name="SearchCities",
        tooltip=folium.GeoJsonTooltip(fields=["city", "cluster", "count"], aliases=["City", "Cluster", "Texts"]),
    ).add_to(m)

    Search(
        layer=search_layer,
        search_label="city_lower",
        placeholder="Search for a city...",
        collapsed=False,
    ).add_to(m)

    folium.LayerControl().add_to(m)

    # === SAVE AND OPEN MAP ===
    m.save(map_file)
    print(f"map saved as {os.path.abspath(map_file)}")

    if chrome_path:
        webbrowser.get(chrome_path).open(f"file://{os.path.abspath(map_file)}")
    else:
        webbrowser.open(f"file://{os.path.abspath(map_file)}")

def summarize_clusters(df):
    summary_df = (
        df.groupby('cluster')
        .agg(
            cities=('city', lambda x: ', '.join(sorted(set(x)))),
            text_count=('textid', 'count')
        )
        .reset_index()
        .rename(columns={'cluster': 'cluster_number'})
    )

    print("\nSummaries of clusters:\n")
    print(tabulate(summary_df, headers=["cluster", "cities in cluster", "number of texts in cluster"], tablefmt="grid"))
    return summary_df


def cluster_and_visualize_first_millenium(first_mil_df: pd.DataFrame, max_km: float):
    print(f"\n\n ## clustering and visualizing first millenium with {max_km} MAX_KM: ")
    clustered_first_millenium_dataframe = cluster_cities(cities_to_cluster_df=first_mil_df, max_km=max_km)
    summarize_clusters(clustered_first_millenium_dataframe)
    visualize_clusters_chrome_search_case_insensitive(clustered_first_millenium_dataframe, f"first_mil_{max_km}_km.html")


def cluster_and_visualize_second_millenium(second_mil_df: pd.DataFrame, max_km: float):
    print(f"\n\n ## clustering and visualizing second millenium with {max_km} MAX_KM: ")
    clustered_second_millenium_dataframe = cluster_cities(cities_to_cluster_df=second_mil_df, max_km=max_km)
    summarize_clusters(clustered_second_millenium_dataframe)
    visualize_clusters_chrome_search_case_insensitive(clustered_second_millenium_dataframe, f"second_mil_{max_km}_km.html")


if __name__ == '__main__':
    dataframe = pd.read_csv("../../data/texts dataframes\oracc_akk_tablets_6_11_2025.csv")
    print("# STEP 1: load dataframe and clean from unmapped cities")
    dataframe_cleaned_from_unmapped_cities = clean_datframe_from_unmapped_cities(dataframe=dataframe)

    print("\n\n\n # STEP 2: add pleaides coordinates to datframe (by city)")
    dataframe_with_pleiades_coordinates = merge_dataframe_with_pleaides_coordinates(dataframe=dataframe_cleaned_from_unmapped_cities)
    print("\n\n\n STEP 3: map dataframe entries to millenium")
    print("\n\n value counts of source for date: ")
    print(dataframe["writing_time_source"].value_counts())
    dataframe_with_millenium = map_millenium_to_dataframe(dataframe=dataframe_with_pleiades_coordinates)

    first_mil_df = dataframe_with_millenium.loc[dataframe_with_millenium["millenium"] == "1st Millennium BCE"]
    print("\nvalue counts for texts from the first millenium by city")
    with pd.option_context('display.max_rows', None):
        print(first_mil_df["city"].value_counts())

    second_mil_df = dataframe_with_millenium.loc[dataframe_with_millenium["millenium"] == "2nd Millennium BCE"]
    # second_mil_df.to
    print("\nvalue counts for texts from the second millenium by city")
    with pd.option_context('display.max_rows', None):
        print(second_mil_df["city"].value_counts())

    max_km_options = [100, 120, 150]
    print(f"\n\n\n # STEP 4: cluster and visualize cities by milleium, with MAX_KM of {max_km_options}")
    for max_km in max_km_options:
        cluster_and_visualize_first_millenium(first_mil_df=first_mil_df, max_km=max_km)

    for max_km in max_km_options:
        cluster_and_visualize_second_millenium(second_mil_df=second_mil_df, max_km=max_km)