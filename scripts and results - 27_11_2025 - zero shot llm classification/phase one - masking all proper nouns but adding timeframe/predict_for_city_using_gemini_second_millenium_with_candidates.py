import os
import random
import re
import pandas as pd
from google.genai import types
from google import genai

# API_KEYS = [
# "AIzaSyCkU8senwdp7odrf6kn1SbbhL32Jp1XpBQ",
#             "AIzaSyCbXUA36cXaLFRyWI6lcOLInzCqWahZwHs",
#             "AIzaSyDFwaFnt7Uq_gYTCnibR08TReHy5OuWO3s",
#             "AIzaSyBKeJV44YBkshwqoCsNo9YjQ2EbIXOFkuo",
#             "AIzaSyA3umd5F6nyvCT21jA2MDqr69Zn98BvQkk",
#             "AIzaSyAQEtf4trA0CcU1vnrry3OOvRcmhsrvnHI"]

API_KEYS= [
    "AIzaSyAu5a0Vs1agvPwI_k7oYWClHNLyql3j_GE"
]

class CallGemini:
    @staticmethod
    def get_client():
        api_key = random.choice(API_KEYS)
        return genai.Client(api_key=api_key)

    @staticmethod
    def classify_city(user_text: str):
        system_text = f"""
         You are an expert in Akkadian regional dialects and scribal practices, with special focus on city-to-city variation in vocabulary, orthography, formulae, and scribal conventions.
         Your task is to identify which ancient location this text was likely written in, from the list CANDIDATE_LOCATIONS below.

         
        Input Format:
        WRITING_TIMEFRAME- the estimated writing timeframe of the text.
        TEXT - the Akkadian text to analyze. Proper names may be masked (examples: DN, PN, GN).

        Instructions:
        1. Initial Scan: Carefully read the text. Understand what is written. 
        2. Analyze indicative features: Deeply and carefully understand and analyze the text, the content, the subject matters and the writing timeframe.
        3. note any features that plausibly indicate a geographic origin (e.g. content, morphology, lexicon, spelling conventions, dialectal forms, grammatical peculiarities, formulaic expressions, orthographic practices, references to local institutions or deities, etc.).
        4. Evaluate Candidates: Compare the observed features against the specific locations in the CANDIDATES list.
        5. Output Reasoning: Before providing the final answer, you must write a short explanation of your choice.
        6. Final Output: Provide your choice of location in XML format like this: <CITY_NAME_CLASSIFICATION>city_name</CITY_NAME_CLASSIFICATION.      
        
        ====CANDIDATE_LOCATIONS===
        Lachish, Ashkelon, Megiddo, Tell Yokneam, Akko, Shechem, Gath, Gezer, Jerusalem,
        Hazor, Ginti-Kirmil, Taanach, Tell el-Hesi,
        Alalakh, Tyre, Byblos, Beirut, Qaṭna, Sidon, 
        Ugarit, Qadesh, Tunip,
        Emar, Mari, Terqa, El-Qitar,
        Assur, Nineveh, Tell Leilan, Tell Rimah, Kār-Tukultī-Ninurta, 
        Tell Abu Marya, Nimrud, Tell 'Ali, Tell Barri, Šibaniba, Tell Brak, 
        Tell Chuera, Tell Fekheriye, Giricano, Šūru, Tell Taban, Tell Sabi Abyad, 
        Dur-Katlimmu, Dur-Sharrukin,
        Nippur, Larsa, Kish, Sippar, Babylon, Borsippa, Ur, Uruk, Haradum,
        Hattusa, Kanesh, Mardin, Yoncali, Tigris Tunnel, Kulišhinaš,
        Me-Turran, Urmia, Luristan, Tell Bazmusian, Nuzi, Akhetaten
        """

        client = CallGemini.get_client()  # get a client with a random key

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_text,
            ),
        )

        return resp.text if hasattr(resp, "text") else str(resp)

def load_train_and_test(source_data_path: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataframe = pd.read_csv(source_data_path, encoding="utf-8")
    random_seed = 42
    train_df = dataframe.sample(frac=0.7, random_state=random_seed)
    test_df = dataframe.drop(train_df.index).reset_index(drop=True)
    return train_df, test_df


def load_predictions_file(output_path: str = None) -> tuple[pd.DataFrame, set]:
    existing_results = None
    processed_ids = None
    if os.path.exists(output_path):
        existing_results = pd.read_csv(output_path, encoding="utf-8")
        processed_ids = set(existing_results["textid"].astype(str))
        print(f"🔁 Resuming from previous run — {len(processed_ids)} texts already processed.")
    else:
        existing_results = pd.DataFrame(columns=[
            "project", "textid", "city_true", "writing_start_year", "writing_end_year", "gemini_response",
            "translation",
            "normalized text", "lemmatized_text", "transliterated_text", "user_message_gemini_2.5_fast",
            "predicted_city_gemini_2.5",
            "input_text_source"
        ])
        processed_ids = set()
        existing_results.to_csv(output_path, index=False, encoding="utf-8")
        print("🆕 Starting new prediction run.")
    return existing_results, processed_ids


def choose_best_available_text_field(row: pd.Series) -> str:
    normalized_text = row["normalized text"]

    if not re.fullmatch(r'[\sUNK]+', normalized_text):
        return "normalized text"
    return "transliterated_text"


def parse_and_normalize_city_predicted_name(full_prediction_string: str) -> str:
    match = re.search(r"<CITY_NAME_CLASSIFICATION>(.*?)</CITY_NAME_CLASSIFICATION>", full_prediction_string)
    match = match.group(1).strip() if match else "COULD_NOT_PARSE"
    if match == "Akhetaten":
        match = "el-Amarna"
    return match


def predict_unpredicted_rows(test_df: pd.DataFrame, processed_ids: set, output_path: str):
    test_df = test_df[~test_df["textid"].astype(str).isin(processed_ids)].reset_index(drop=True)
    print(f"➡️ Remaining texts to process: {len(test_df)}")

    for idx, row in test_df.iterrows():
        textid = str(row["textid"])
        project = str(row["project"])
        city_true = row.get("city")
        start_year = row.get("writing_start_year")
        end_year = row.get("writing_end_year")

        best_available = choose_best_available_text_field(row=row)
        text = row.get(best_available)

        try:
            print(f"🔮 Processing {idx + 1}/{len(test_df)} — ID: {textid}")

            user_message = f"<WRITING_TIMEFRAME>{start_year} - {end_year}</WRITING_TIMEFRAME>  <TEXT> {text} </TEXT>"
            gemini_response = CallGemini.classify_city(user_text=user_message)
            parsed_city = parse_and_normalize_city_predicted_name(full_prediction_string=gemini_response)
            print(
                f"TEXT: {project} - {textid}, GOLD IS: {city_true}, PREDICTED: {parsed_city}, is_equal: {city_true == parsed_city}")
            new_row = pd.DataFrame([{
                "project": project,
                "textid": textid,
                "city_true": city_true,
                "writing_start_year": start_year,
                "writing_end_year": end_year,
                "gemini_response": gemini_response,
                "translation": row.get("translation"),
                "normalized text": row.get("normalized text"),
                "lemmatized_text": row.get("lemmatized_text"),
                "transliterated_text": row.get("transliterated_text"),
                "user_message_gemini_2.5_fast": user_message,
                "predicted_city_gemini_2.5": parsed_city,
                "input_text_source": best_available
            }])
            new_row.to_csv(output_path, mode="a", header=False, index=False, encoding="utf-8")

        except Exception as e:
            print(f"❌ Error processing textid={textid}: {e}")
            continue

    print(f"\n✅ Completed all available test samples. Results saved to {output_path}")


if __name__ == '__main__':
    source_data_path = r"C:\Users\shaha\PycharmProjects\oracc_preprocessing\tests\scripts and results - 6_11_2025\second_millenium_df.csv"
    train_data, test_data = load_train_and_test(source_data_path=source_data_path)

    output_path = "gemini_predictions_second_millenium_with_candidates_list.csv"
    existing_results, processed_ids = load_predictions_file(output_path=output_path)

    predict_unpredicted_rows(test_df=test_data, processed_ids=processed_ids, output_path=output_path)