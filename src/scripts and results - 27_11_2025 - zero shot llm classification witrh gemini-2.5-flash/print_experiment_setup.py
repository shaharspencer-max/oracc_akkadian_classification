import pandas as pd

cities = """
Babylon, Uruk, Persepolis, Susa, Ur, Suez, Daskyleion, 
Naqsh-I Rustam, Assur, Burmarina, Nimrud, Dur-Katlimmu, 
Guzana, Huzirina, Balāwāt, Marqasu, Zincirli, Tell Billa, Til Barsip, 
Tušhan, Sippar, Kutha, Borsippa, Nippur, Nineveh, Kish, Dilbat, 
Dur-Sharrukin, Larsa, Kilizu, Tell Barri, Tarbisu, Tell Satu Qala, 
Kurkh, Tell Abu Marya, Tell Ajaja, Tell Fakhariyah, 
Tell al-Hawa, Tigris Tunnel, Tell Rimah, Kizkapanlı, Byblos, Pāra, Tell Abta, Sabaʾa, Antakya, 
Dohuk, Kenk Boǧazı, Harran/Carrhae, Marad, Luristan, Dur-Kurigalzu, Me-Turran, Zalu-Ab, Selaʾ,
Brissa, Tayma, Padakku, Nahr el-Kelb, Kissik, Isin, Arslan Tash, Tell Tayinat, Mila Mergi, 
Tell Baradan, Qalʾeh-i Imam, Tang-i Var, Ashdod, Melid, Turlu Höyük, Carchemish, Tunip, Samaria,
Larnaka, Najafabad, Jerwan, Samarra, Tikrit, Judi Dagh, Wadi Bastura Tunnel, Bavian, Negub Tunnel,
el-Ghab, Kalmākarra, Ben Shemen, Der, Arbela, Takrit, Beisan, Sur Jureh, Ana, Dawali,
Judeideh, Zawiyeh, Hamath, Damascus, Hindanu, Muṣaṣir, Arrapha, Lahiru, Akkad, Larak, 
Isana, Elam,Urartu, Arpadda, Simyra, Manṣuate, Isana"""
def display_experiment_setup():
    print("## MODEL USED: gemini-2.5-flash\n")
    print("## SYSTEM PROMPT:")
    system_prompt = f"""You are an expert in Akkadian regional dialects and scribal practices, with special focus on city-to-city variation in vocabulary, orthography, formulae, and scribal conventions.
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

--- end of system prompt
        """
    print(system_prompt)
    print("\n")

    print("DATA MILLENIUM: first millenium")
    df = pd.read_csv(
        r"phase 3 - finegraining proper noun masking/gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en.csv")
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
