import pandas as pd

# 1. Load the DataFrames
df_translit = pd.read_csv(r"C:\Users\shaha\PycharmProjects\oracc_akkadian_classification\src\scripts_and_results _11_12_2025 _error_analysis\running_on_transliterated_texts\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters_on_transliterated_texts.csv")
df_norm = pd.read_csv(r"C:\Users\shaha\PycharmProjects\oracc_akkadian_classification\src\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 4 - fixing sender location and recreating train+test\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters.csv")

# 2. Define the columns you want to compare (The ones that NEED suffixes)
# Replace these with the actual column names from your CSVs that contain the predictions
cols_to_suffix = [
    'user_message_gemini_2.5_fast', 'predicted_city_gemini_2.5',
    'gemini_response'
]

# 3. Create a subset of the Normalized DF
# We only keep the Join Keys + The Columns we want to compare.
# We DROP the metadata (like genre, date) from this side so it doesn't get duplicated.
cols_to_keep_right = ['textid', 'project'] + [c for c in cols_to_suffix if c in df_norm.columns]
df_norm_subset = df_norm[cols_to_keep_right]

# 4. Perform the Inner Join
df_merged = pd.merge(
    df_translit,
    df_norm_subset,
    on=['textid', 'project'],
    how='inner',
    suffixes=('_translit', '_norm')
)

# 5. Check the result
print(f"Merged shape: {df_merged.shape}")
print("Columns:", df_merged.columns.tolist())


# 1. Define Boolean masks for correctness
# Check if Transliterated prediction is correct
translit_correct = df_merged['predicted_city_gemini_2.5_translit'] == df_merged['city_true']

# Check if Normalized prediction is correct
norm_correct = df_merged['predicted_city_gemini_2.5_norm'] == df_merged['city_true']

# 2. Filter for the two specific "mixed success" scenarios

# Case A: Transliterated worked, Normalized failed
df_translit_wins = df_merged[translit_correct & (~norm_correct)].copy()

# Case B: Normalized worked, Transliterated failed
df_norm_wins = df_merged[(~translit_correct) & norm_correct].copy()

# 3. Select columns for easy viewing
view_cols = [
    'textid',
    'city_true',
    'predicted_city_gemini_2.5_translit',
    'predicted_city_gemini_2.5_norm',
    'project' # Useful for context
]

# 4. Display Results
print(f"--- Summary ---")
print(f"Total Rows: {len(df_merged)}")
print(f"Transliterated Correct ONLY: {len(df_translit_wins)}")
print(f"Normalized Correct ONLY:    {len(df_norm_wins)}")

print("\n--- Transliterated SUCCEEDED / Normalized FAILED (First 5) ---")
print(df_translit_wins[view_cols].head())

print("\n--- Normalized SUCCEEDED / Transliterated FAILED (First 5) ---")
print(df_norm_wins[view_cols].head())