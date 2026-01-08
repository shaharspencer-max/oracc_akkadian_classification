import os
import re
import random
import threading
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.genai import types
from google import genai

# --- Configuration ---
cities = """
Babylon, Uruk, Persepolis, Susa, Ur, Suez, Daskyleion, Naqsh-I Rustam, Assur, Burmarina, Nimrud, Dur-Katlimmu, Guzana, Huzirina, Balāwāt, Marqasu, Zincirli, Tell Billa, Til Barsip, Tušhan, Sippar, Kutha, Borsippa, Nippur, Nineveh, Kish, Dilbat, Dur-Sharrukin, Larsa, Kilizu, Tell Barri, Tarbisu, Tell Satu Qala, Kurkh, Tell Abu Marya, Tell Ajaja, Tell Fakhariyah, Tell al-Hawa, Tigris Tunnel, Tell Rimah, Kizkapanlı, Byblos, Pāra, Tell Abta, Sabaʾa, Antakya, Dohuk, Kenk Boǧazı, Harran/Carrhae, Marad, Luristan, Dur-Kurigalzu, Me-Turran, Zalu-Ab, Selaʾ, Brissa, Tayma, Padakku, Nahr el-Kelb, Cutha, Kissik, Isin, Arslan Tash, Tell Tayinat, Mila Mergi, Tell Baradan, Qalʾeh-i Imam, Tang-i Var, Ashdod, Melid, Turlu Höyük, Carchemish, Tunip, Samaria, Larnaka, Najafabad, Jerwan, Samarra, Tikrit, Judi Dagh, Wadi Bastura Tunnel, Bavian, Negub Tunnel, el-Ghab, Kalmākarra, Ben Shemen, Der, Arbela, Takrit, Beisan, Sur Jureh, Ana, Dawali, Judeideh, Zawiyeh"""
#
# AIzaSyDFwaFnt7Uq_gYTCnibR08TReHy5OuWO3s BLOCKED NEED TO GET NEW ONE

API_KEYS = [
    "AIzaSyCkU8senwdp7odrf6kn1SbbhL32Jp1XpBQ",
    "AIzaSyCbXUA36cXaLFRyWI6lcOLInzCqWahZwHs",
    # "AIzaSyDFwaFnt7Uq_gYTCnibR08TReHy5OuWO3s",
    "AIzaSyBKeJV44YBkshwqoCsNo9YjQ2EbIXOFkuo",
    "AIzaSyA3umd5F6nyvCT21jA2MDqr69Zn98BvQkk",
    "AIzaSyAQEtf4trA0CcU1vnrry3OOvRcmhsrvnHI",
    "AIzaSyAu5a0Vs1agvPwI_k7oYWClHNLyql3j_GE",
"AIzaSyC2eokQCXyVWkyHCpQ4d1fjic91BvDkh6o",
          "AIzaSyBLrLtt5Fr2utl2c8rd8gITu6W0444K56g"
]


# This lock ensures only one thread writes to the CSV at a time
csv_write_lock = threading.Lock()


class CallGemini:
    @staticmethod
    def classify_city(user_text: str, api_key: str):
        system_text = (f"""
        You are an expert in Akkadian regional dialects and scribal practices, with special focus on city-to-city variation in vocabulary, orthography, formulae, and scribal conventions.
        Your task is to identify which ancient location this text was likely written in, from the list CANDIDATE_LOCATIONS below.

        Constraint: Your answer must be one of the locations in CANDIDATE_LOCATIONS.

        Input Format:
        TEXT - the Akkadian text to analyze. The text was written in the first millennium BCE. Some types of proper names are masked (GN - geographical name,SN- state name,TN - Temple Name, WN - Water Name, QN - Quarter Name, ON  - Geographical Name (variant) DN - Divine Name,RN - Royal Name, EN - ethnic name. )

        Instructions:
        1. Initial Scan: Carefully read the text. Understand what is written. 
        2. Analyze indicative features: Deeply and carefully understand and analyze the text, the content, the subject matters, the grammar, onomastics, etc. 
        3. note any features that plausibly indicate a geographic origin (e.g. content,  morphology, lexicon, spelling conventions, dialectal forms, names, grammatical peculiarities, formulaic expressions, orthographic practices, references to local institutions or deities, etc.).
        4. Evaluate Candidates: Compare the observed features against the specific locations in the CANDIDATE_LOCATIONS list.
        5. Output Reasoning: Before providing the final answer, you must write a short explanation of your choice.
        6. Final Output: Provide your choice of location in XML format like this: <CITY_NAME_CLASSIFICATION>city_name</CITY_NAME_CLASSIFICATION.      

        ====CANDIDATE_LOCATIONS=== 
        {cities}
          """
                       )

        # Instantiate client with the specific key passed to this thread
        client = genai.Client(api_key=api_key)

        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_text,
                    temperature=0.1
                ),
            )
            return resp.text if hasattr(resp, "text") else str(resp)
        except Exception as e:
            # Return error string so we can log it but keep going
            print(f"API_ERROR: {str(e)}")
            return f"API_ERROR: {str(e)}"


def load_train_and_test(source_data_path: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    dataframe = pd.read_csv(source_data_path, encoding="utf-8")
    random_seed = 42
    train_df = dataframe.sample(frac=0.7, random_state=random_seed)
    test_df = dataframe.drop(train_df.index).reset_index(drop=True)
    return train_df, test_df


def load_predictions_file(output_path: str = None) -> tuple[pd.DataFrame, set]:
    processed_ids = set()
    if os.path.exists(output_path):
        existing_results = pd.read_csv(output_path, encoding="utf-8")
        # Ensure we treat IDs as strings for consistent comparison
        processed_ids = set(existing_results["textid"].astype(str))
        print(f"🔁 Resuming from previous run — {len(processed_ids)} texts already processed.")
    else:
        # Create empty file with headers
        existing_results = pd.DataFrame(columns=[
            "project", "textid", "city_true", "writing_start_year", "writing_end_year", "gemini_response",
            "translation",
            "normalized text", "lemmatized_text", "transliterated_text", "user_message_gemini_2.5_fast",
            "predicted_city_gemini_2.5",
            "input_text_source"
        ])
        existing_results.to_csv(output_path, index=False, encoding="utf-8")
        print("🆕 Starting new prediction run.")
    return None, processed_ids


def choose_best_available_text_field(row: pd.Series) -> str:
    # Handle NaN gracefully
    normalized_text = str(row.get("normalized text", ""))

    if normalized_text and not re.fullmatch(r'[\sUNK]+', normalized_text) and normalized_text.lower() != 'nan':
        return "normalized text"
    return "transliterated_text"


def parse_and_normalize_city_predicted_name(full_prediction_string: str) -> str:
    if "API_ERROR" in full_prediction_string:
        return "API_ERROR"
    match = re.search(r"<CITY_NAME_CLASSIFICATION>(.*?)</CITY_NAME_CLASSIFICATION>", full_prediction_string)
    match = match.group(1).strip() if match else "COULD_NOT_PARSE"
    return match


# --- WORKER FUNCTION ---
def process_single_row(row, assigned_key, output_path):
    """
    This function runs inside a thread.
    """
    textid = str(row["textid"])
    project = str(row["project"])
    city_true = row.get("city")
    start_year = row.get("writing_start_year")
    end_year = row.get("writing_end_year")

    best_available = choose_best_available_text_field(row=row)
    if best_available == "transliterated_text":
        print(f"⏭️ Skipping ID {textid} (Transliterated only)")
        return
    text = row.get(best_available)

    try:
        user_message = f"<TEXT> {text} </TEXT>"

        # --- RETRY LOGIC ---
        # 1. Create a list of keys to try, starting with the assigned one
        # 2. If assigned fails, we shuffle the rest to avoid all threads hitting the same backup key at once
        other_keys = [k for k in API_KEYS if k != assigned_key]
        random.shuffle(other_keys)
        keys_to_try = [assigned_key] + other_keys

        final_response = None
        parsed_city = "API_ERROR"

        for key in keys_to_try:
            gemini_response = CallGemini.classify_city(user_text=user_message, api_key=key)
            parsed_city = parse_and_normalize_city_predicted_name(full_prediction_string=gemini_response)

            if parsed_city != "API_ERROR":
                final_response = gemini_response
                break  # Success! Exit the key loop
            else:
                print(f"⚠️ Key {key[:10]}... failed for ID {textid}. Trying next key...")

        # --- CHECK IF ALL FAILED ---
        if parsed_city == "API_ERROR":
            print(f"❌ ALL keys failed for ID {textid}. Skipping save so it can be retried next run.")
            return  # Exit function, do not write to file

        print(f"THREAD-DONE: ID {textid} | True: {city_true} | Pred: {parsed_city}")

        # Prepare DataFrame row
        new_row = pd.DataFrame([{
            "project": project,
            "textid": textid,
            "city_true": city_true,
            "writing_start_year": start_year,
            "writing_end_year": end_year,
            "gemini_response": final_response,
            "translation": row.get("translation"),
            "normalized text": row.get("normalized text"),
            "lemmatized_text": row.get("lemmatized_text"),
            "transliterated_text": row.get("transliterated_text"),
            "user_message_gemini_2.5_fast": user_message,
            "predicted_city_gemini_2.5": parsed_city,
            "input_text_source": best_available
        }])

        # --- CRITICAL SECTION: WRITE TO FILE ---
        # We lock here so threads don't write over each other
        with csv_write_lock:
            new_row.to_csv(output_path, mode="a", header=False, index=False, encoding="utf-8")
        time.sleep(5)

    except Exception as e:
        print(f"❌ Error processing textid={textid}: {e}")


def run_threaded_predictions(test_df: pd.DataFrame, processed_ids: set, output_path: str):
    # Filter out already processed rows
    test_df = test_df[~test_df["textid"].astype(str).isin(processed_ids)].reset_index(drop=True)
    total_rows = len(test_df)
    print(f"➡️ Remaining texts to process: {total_rows}")

    # Set number of threads equal to number of keys to maximize throughput without hitting single-key limits too hard
    # You can increase max_workers, but 1 key per thread is usually safest logic.
    max_threads = len(API_KEYS)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        for idx, row in test_df.iterrows():
            # Round-robin assignment of keys
            assigned_key = API_KEYS[idx % len(API_KEYS)]

            # Submit task to thread pool
            futures.append(executor.submit(process_single_row, row, assigned_key, output_path))

        # Optional: Wait for all to complete (context manager handles this, but this lets us catch thread crashes)
        for future in as_completed(futures):
            try:
                future.result()  # raises exceptions if they occurred in the thread
            except Exception as exc:
                print(f"Thread generated an exception: {exc}")

    print(f"\n✅ Completed all available test samples.")


if __name__ == '__main__':
    # Update this path to your actual file location
    source_data_path = r"C:\Users\shaha\PycharmProjects\oracc_preprocessing\tests\running tests only on GNs masked\first_millennium_oracc_tablets_gn__and_en_masked.csv"

    # Ensure source file exists before running
    if os.path.exists(source_data_path):
        train_data, test_data = load_train_and_test(source_data_path=source_data_path)

        output_path = "../../../oracc_akkadian_classification/scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash/phase 3 - finegraining proper noun masking/gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en.csv"
        _, processed_ids = load_predictions_file(output_path=output_path)

        run_threaded_predictions(test_df=test_data, processed_ids=processed_ids, output_path=output_path)
    else:
        print(f"❌ Source file not found: {source_data_path}")