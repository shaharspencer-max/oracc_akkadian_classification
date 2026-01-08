import pandas as pd

# Load the main dataframe
p = r"C:\Users\shaha\PycharmProjects\oracc_akkadian_classification\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 4 - fixing sender location and recreating train+test\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters.csv"
df = pd.read_csv(p, encoding='utf-8')

# Load the metadata with authoritative genre information
metadata_path = r"C:\Users\shaha\PycharmProjects\oracc_akkadian_classification\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 3 - finegraining proper noun masking\first_millennium_oracc_metadata-sender_location_and_genre.csv"
metadata_df = pd.read_csv(metadata_path, encoding='utf-8')

print(f"Original df shape: {df.shape}")
print(f"Metadata df shape: {metadata_df.shape}")

# Drop existing genre columns if they exist (including any previous genre column)
df = df.drop(columns=["genre_x", "genre_y", "genre"], errors='ignore')
print(f"After dropping genre columns, df shape: {df.shape}")

# Merge with metadata to get authoritative genre information
df_merged = df.merge(metadata_df[['project', 'textid', 'genre']], 
                     on=['project', 'textid'], 
                     how='left')

print(f"Merged df shape: {df_merged.shape}")
print(f"Merged df columns: {df_merged.columns.tolist()}")

if 'genre' in df_merged.columns:
    print(f"Rows with genre info: {df_merged['genre'].notna().sum()}")
    print(f"Rows without genre info: {df_merged['genre'].isna().sum()}")
    print(f"Genre value counts:")
    print(df_merged['genre'].value_counts().head(10))
    
    # Save the result
    df_merged.to_csv(p, index=False, encoding='utf-8')
    print(f"Successfully saved updated file with genre information from metadata!")
else:
    print("ERROR: 'genre' column still not found in merged dataframe!")
    print("Available columns:", df_merged.columns.tolist())

