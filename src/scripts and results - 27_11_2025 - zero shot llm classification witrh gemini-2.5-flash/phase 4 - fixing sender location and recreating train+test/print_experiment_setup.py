import pandas as pd
from predict_for_first_mill_after_cleaning_unmapped_cities import system_text
def display_experiment_setup():
    print("## MODEL USED: gemini-2.5-flash\n")
    print("## SYSTEM PROMPT:")
    system_prompt =system_text
    print(system_prompt)
    print("\n")

    print("DATA MILLENIUM: first millenium")
    df = pd.read_csv(
        r"C:\Users\shaha\PycharmProjects\oracc_akkadian_classification\scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash\phase 4 - fixing sender location and recreating train+test\gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters.csv")
    print(f"TEST DATA POINTS EVALUATED: {len(df)}")

    print("\n")
    print("MASKED ENTITIES: ")
    print( """"GN",  # Geographical Name
"SN",  # State/City Name
"TN",  # Temple Name
"WN",  # Water Name
"QN",  # Quarter Name
"ON",  # Geographical Name (variant)
"DN",  # Divine Name (Patron gods give away the city)
"RN",  # Royal Name
"EN  # Ethnicity name""")
