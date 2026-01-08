import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.path_utils import get_provenenances_to_plaides_data_mapping
from math import radians, sin, cos, sqrt, atan2


normaliziation_dictionary = {
'Kalhu (Nimrud)': "Nimrud",
'Nimrud (Kalhu)': "Nimrud",
    "Kalhu": "Nimrud",
    "Aššur": "Assur",
    "Kalah (Nimrud)": "Nimrud",
    "Unknown": "Unknown",
    "Ashur": "Assur",
    "Washukanni": "Tell Fekheriye", # todo no idea,
    "Alashiya": "Alashiya", #todo no idea,
    "Akhetaten": "el-Amarna",
    "Raṣappa": "Raṣappa", #todo no idea,
    "Sam'al (Zincirli)": "Zincirli",
    "Harran": "Harran/Carrhae",
    "Sultantepe (Huzirina)": "Huzirina",
    "COULD_NOT_PARSE": "Unknown",
    "UNKNOWN": "Unknown",
    "Akka": "Akko",
    "Amarna": "el-Amarna",
    "Amarna (Akhetaten)": "el-Amarna",
    "Dūr-Katlimmu": "Dur-Katlimmu",
    "Gubla (Byblos)": "Byblos",
    "Hattusa (Boğazköy)": "Hattusa",
    "Kar-Tukulti-Ninurta": "Kār-Tukultī-Ninurta",
    "Qadeš": "Qadesh",
    "Shechem (Šakmu)": "Shechem",
    "Tell el-Amarna": "el-Amarna",
    "Akkad (Agade)": "Akkad (Agade)",
    "Undeterminable (Insufficient Data)": "Unknown",
    "Waššukanni": "Tell Fekheriye",
"Arbela (Arbailu)": "Arbela",
    "Arbail": "Arbela",
    "Arba'il": "Arbela",
    "Arba'il (Erbil)": "Arbela",
    "Dur-Sharrukin (Khorsabad)": "Dur-Sharrukin",
    "Dur-Šarrukin": "Dur-Sharrukin",
    "Dūr-Šarrukīn": "Dur-Sharrukin",
    "Erbil": "Arbela",
    "Kalḫu": "Nimrud",
    "Kalḫu (Nimrud)": "Nimrud",
    "Khorsabad": "Dur-Sharrukin",
    "Nimrud (Kalah)": "Nimrud",
    "Ninua": "Nineveh",
    "Til-Barsip": "Til Barsip",
    "Til-barsibi": "Til Barsip"
}

provenenances_to_plaides_data_mapping = get_provenenances_to_plaides_data_mapping()



non_noamalized_values = set()


def normalize_prediction(prediction_row: pd.Series):
    prediction = prediction_row["predicted_city_gemini_2.5"]

    # 1. Check if it's already a valid Pleiades city
    if prediction in provenenances_to_plaides_data_mapping["city_name"].values:
        return prediction

    # 2. Check if it's in your normalization dictionary
    if prediction in normaliziation_dictionary.keys():
        return normaliziation_dictionary[prediction]

    # 3. Fallback: Return "Unknown" instead of None
    # This forces the heatmap to create a column for "Unknown"
    return "Unknown"

def get_prediction_dataframe(path: str)->pd.DataFrame:
    predictions_dataframe = pd.read_csv(path, encoding="utf-8")
    return predictions_dataframe

def get_exact_location_accuracy(df: pd.DataFrame):
    print("-----exact location accuracy------")
    gold = df["city_true"]
    pred = df["predicted_city_gemini_2.5"]

    accuracy = (gold == pred).mean()
    print(f"Accuracy: {accuracy:.4f}")
    return accuracy


def plot_prediction_heatmap(df, save_path="heatmap.png", top_k=20, title=None):
    # 1. Identify the top K cities by frequency in the Gold Standard
    if df.empty:
        print(f"Skipping heatmap for empty dataframe (save_path={save_path})")
        return

    top_cities = df["city_true"].value_counts().nlargest(top_k).index.tolist()

    # 2. Filter the dataframe
    df_filtered = df[df["city_true"].isin(top_cities)]

    if df_filtered.empty:
        print(f"No data found for top {top_k} cities in this subset.")
        return

    # --- CHANGES START HERE ---

    # Create Cross-tabulation with normalization
    # normalize='index' ensures that each row (True City) sums to 1
    confusion = pd.crosstab(
        df_filtered["city_true"],
        df_filtered["predicted_city_gemini_2.5"],
        normalize='index'
    )

    # Convert fractions (0.85) to percentages (85.0)
    confusion = confusion * 100

    # Save the percentage data to CSV (optional: if you want raw counts in CSV, move this up)
    confusion.to_csv(save_path.replace(".png", "") + ".csv")

    # 3. Dynamic size
    n_rows, n_cols = confusion.shape
    figsize_width = max(8, n_cols * 0.8)
    figsize_height = max(6, n_rows * 0.6)
    plt.figure(figsize=(figsize_width, figsize_height))

    # fmt='.1f' formats the number as a float with 1 decimal place (e.g., 45.2)
    # If you prefer no decimals, change to fmt='.0f'
    sns.heatmap(confusion, annot=True, fmt=".1f", cmap="Blues")

    # --- CHANGES END HERE ---

    # Use custom title if provided, else default
    if title:
        plt.title(title + " (Values in %)")
    else:
        plt.title(f"Confusion Matrix (Top {top_k} Most Frequent Cities) - %")

    plt.xlabel("Predicted City")
    plt.ylabel("True City")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved plot: {save_path}")
def haversine(lat1, lon1, lat2, lon2):
    """
    Compute great-circle distance (km) between two coordinates.
    """
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat/2)**2
        + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_accuracy_at_k(df: pd.DataFrame, k: int):
    print(f"GETTING ACCURACY AT {k} KM")

    # Lookup dictionary: city → (lat, lon)
    coord_lookup = {
        row["city_name"]: (row["lat"], row["lon"])
        for _, row in provenenances_to_plaides_data_mapping.iterrows()
    }

    def row_is_correct(row):
        true_city = row["city_true"]
        pred_city = row["predicted_city_gemini_2.5"]

        # If either city missing → mark 0
        if true_city not in coord_lookup or pred_city not in coord_lookup:
            return 0

        lat1, lon1 = coord_lookup[true_city]
        lat2, lon2 = coord_lookup[pred_city]

        # If any coordinate missing/null → mark 0
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
            return 0

        # Compute distance
        dist = haversine(lat1, lon1, lat2, lon2)

        return 1 if dist <= k else 0

    result_col = f"accuracy_at_{k}km"
    df[result_col] = df.apply(row_is_correct, axis=1)

    score = df[result_col].mean()
    print(f"Accuracy within {k} km: {score:.4f}")

    return score

def get_mean_median_error_distance(df: pd.DataFrame):
    print("EVALUATING MEAN AND MEDIAN ERROR DISTANCE")

    # Lookup dictionary: city → (lat, lon)
    coord_lookup = {
        row["city_name"]: (row["lat"], row["lon"])
        for _, row in provenenances_to_plaides_data_mapping.iterrows()
    }

    distances = []

    for _, row in df.iterrows():
        true_city = row["city_true"]
        pred_city = row["predicted_city_gemini_2.5"]

        # Skip if either city is missing in the lookup
        if true_city not in coord_lookup or pred_city not in coord_lookup:
            continue

        lat1, lon1 = coord_lookup[true_city]
        lat2, lon2 = coord_lookup[pred_city]

        # Skip if any coordinate is missing/null
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
            continue

        # Compute distance
        dist = haversine(lat1, lon1, lat2, lon2)
        distances.append(dist)

    if not distances:
        print("No valid distances could be computed.")
        return None, None

    mean_distance = np.mean(distances)
    median_distance = np.median(distances)

    print(f"Mean Error Distance: {mean_distance:.2f} km")
    print(f"Median Error Distance: {median_distance:.2f} km")

    return mean_distance, median_distance


def plot_error_distance_cdf(df: pd.DataFrame, save_path="error_distance_cdf.png"):
    # Lookup dictionary: city → (lat, lon)
    coord_lookup = {
        row["city_name"]: (row["lat"], row["lon"])
        for _, row in provenenances_to_plaides_data_mapping.iterrows()
    }

    distances = []

    for _, row in df.iterrows():
        true_city = row["city_true"]
        pred_city = row["predicted_city_gemini_2.5"]

        # Skip if either city missing
        if true_city not in coord_lookup or pred_city not in coord_lookup:
            continue

        lat1, lon1 = coord_lookup[true_city]
        lat2, lon2 = coord_lookup[pred_city]

        # Skip if coordinates are missing
        if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
            continue

        # Compute distance
        dist = haversine(lat1, lon1, lat2, lon2)
        distances.append(dist)

    if not distances:
        print("No valid distances to plot.")
        return

    distances = np.array(distances)

    # Compute CDF
    sorted_distances = np.sort(distances)
    cdf = np.arange(1, len(sorted_distances)+1) / len(sorted_distances)

    # Plot
    plt.figure(figsize=(8, 5))
    plt.plot(sorted_distances, cdf, marker='.', linestyle='none')
    plt.xlabel("Distance Error (km)")
    plt.ylabel("Cumulative Fraction of Predictions")
    plt.title("CDF of Prediction Error Distances")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

    print(f"CDF plot saved to: {save_path}")



if __name__ == '__main__':
    millenium = 1
    print(f"RESULTS FOR GEMINI-2.5-FLASH FOR: {millenium} MILLENIUM")
    print("STEP 1: EXPLAINING EXPERIMENT SETUP")
    from print_experiment_setup import display_experiment_setup

    display_experiment_setup()
    print("FINISHED STEP 1")
    print("\n\n\n")

    print(f"STEP 2: EVALUATING BY METRICS (GLOBAL)")
    prediction_df_path=r"phase 3 - finegraining proper noun masking\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters.csv"

    # prediction_df_path = r"phase 3 - finegraining proper noun masking\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en.csv"
    predictions_dataframe = get_prediction_dataframe(path=prediction_df_path)
    predictions_dataframe["predicted_city_gemini_2.5"] = predictions_dataframe.apply(normalize_prediction, axis=1)
    metadata_dataframe = pd.read_csv(
        "phase 3 - finegraining proper noun masking/first_millennium_oracc_metadata-sender_location_and_genre.csv")
    metadata_clean = metadata_dataframe[['project', 'textid', 'genre']].drop_duplicates(subset=['project', 'textid'])

    # 2. Perform the Left Merge
    predictions_dataframe = pd.merge(
        predictions_dataframe,
        metadata_clean,
        on=['project', 'textid'],
        how='left'
    )
    predictions_dataframe.to_csv(
        prediction_df_path, index=False)

    # Global Metrics
    get_exact_location_accuracy(df=predictions_dataframe)
    print("\n\n--- getting accuracy@k (GLOBAL)----")
    for k in range(20, 105, 10):
        get_accuracy_at_k(df=predictions_dataframe, k=k)
    print("\n")
    get_mean_median_error_distance(predictions_dataframe)

    print("FINISHED STEP 2\n\n\n")

    print("STEP 3: VISUALIZING RESULTS")
    plot_prediction_heatmap(predictions_dataframe,
                            save_path=f"heatmap_confusion_matrix_{millenium}_millenium-for_masked_data.png")

    print("\n\n================================================")
    print("--- GENERATING GENRE-SPECIFIC METRICS & PLOTS ---")
    print("================================================")

    # 1. Count occurrences of each genre
    genre_counts = predictions_dataframe['genre'].value_counts()

    # 2. Filter for genres with > 30 occurrences
    target_genres = genre_counts[genre_counts > 30].index.tolist()

    print(f"Found {len(target_genres)} genres to process: {target_genres}\n")

    # 3. Iterate, calculate metrics, and plot
    for genre in target_genres:
        print(f"\n{'-' * 20}")
        print(f"PROCESSING GENRE: {genre.upper()}")
        print(f"{'-' * 20}")

        # Create a subset for this genre
        genre_df = predictions_dataframe[predictions_dataframe['genre'] == genre].copy()

        # --- A. CALCULATE METRICS FOR THIS GENRE ---
        print(f"Samples in genre: {len(genre_df)}")

        get_exact_location_accuracy(df=genre_df)

        print(f"\n... Accuracy@K for {genre} ...")
        for k in [100]:
            get_accuracy_at_k(df=genre_df, k=k)

        print("\n")
        get_mean_median_error_distance(genre_df)

        # --- B. GENERATE HEATMAP FOR THIS GENRE ---
        safe_name = str(genre).replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"first_century_dataset_heatmap_confusion_matrix_{safe_name}.png"

        plot_prediction_heatmap(
            genre_df,
            save_path=filename,
            top_k=20,
            title=f"Confusion Matrix: {genre}"
        )
        print(f"Saved plot for {genre}")