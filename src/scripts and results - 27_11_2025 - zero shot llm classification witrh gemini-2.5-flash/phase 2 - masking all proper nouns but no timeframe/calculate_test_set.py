import re
import pandas as pd


def choose_best_available_text_field(row: pd.Series) -> str:
    # Handle NaN gracefully
    normalized_text = str(row.get("normalized text", ""))

    if normalized_text and not re.fullmatch(r'[\sUNK]+', normalized_text) and normalized_text.lower() != 'nan':
        return "normalized text"
    return "transliterated_text"

df = pd.read_csv(
    r"/scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash/gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_genre.csv")


df_2 = pd.read_csv(
    r"/scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash/phase 3 - finegraining proper noun masking/tablets_full_merged_with_sender_city_and_genre.csv")

df_2["best_available"] = df_2.apply(choose_best_available_text_field, axis=1)

z=0