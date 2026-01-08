import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.path_utils import get_provenenances_to_plaides_data_mapping
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
    if prediction in provenenances_to_plaides_data_mapping["city_name"].values:
        return prediction
    else:
        if prediction in normaliziation_dictionary.keys():
          return normaliziation_dictionary[prediction]
        try:
            assert prediction in normaliziation_dictionary, f"not all values have been normalized. please normalize the city {prediction} and then proceed."
        except AssertionError:
            non_noamalized_values.add(prediction)

        return prediction


def get_prediction_dataframe(path: str)->pd.DataFrame:
    predictions_dataframe = pd.read_csv(path, encoding="utf-8")
    return predictions_dataframe

def get_exact_location_accuracy(df: pd.DataFrame):
    print("EVALUATING EXACT LOCATION ACCURACY:")
    gold = df["city_true"]
    pred = df["predicted_city_gemini_2.5"]

    accuracy = (gold == pred).mean()
    print(f"Accuracy: {accuracy:.4f}")
    return accuracy
def plot_prediction_heatmap(df, save_path="heatmap.png"):
    confusion = pd.crosstab(
        df["city_true"],
        df["predicted_city_gemini_2.5"]
    )
    confusion.to_csv("confusion_matrix.csv")

    plt.figure(figsize=(12, 8))
    sns.heatmap(confusion, annot=True, fmt="d", cmap="Blues")

    plt.title("Prediction Heatmap (True vs Predicted Cities)")
    plt.xlabel("Predicted City")
    plt.ylabel("True City")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Save to disk
    plt.savefig(save_path, dpi=300)

    print(f"Heatmap saved to: {save_path}")

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
    print(f"EVALUATING RESULTS FOR GEMINI-2.5-FLASH FOR: {millenium} MILLENIUM")

    prediction_df_path = r"C:\Users\shaha\PycharmProjects\oracc_preprocessing\tests\running tests only on GNs masked\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en.csv"
    predictions_dataframe = get_prediction_dataframe(path=prediction_df_path)
    predictions_dataframe["predicted_city_gemini_2.5"] = predictions_dataframe.apply(normalize_prediction, axis=1)
    print("NON NORMALIZED VALUES:")
    print(non_noamalized_values)

    get_exact_location_accuracy(df=predictions_dataframe)
    plot_prediction_heatmap(predictions_dataframe, save_path=f"heatmap_confusion_matrix_{millenium}_millenium-for_masked_data.png")
    for k in range(20, 105, 10):
        get_accuracy_at_k(df=predictions_dataframe, k=k)

    get_mean_median_error_distance(predictions_dataframe)
