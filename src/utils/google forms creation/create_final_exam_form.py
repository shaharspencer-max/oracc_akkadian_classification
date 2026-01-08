"""
Final Exam Form Generator (Advisor Feedback Implementation).
- Single Form.
- Texts: 20 texts, 50-100 words preferred.
- Display: Dual View (Transliteration + Normalization).
- Truncation: >100 words -> Truncate + [Excerpt].
- Reference Material: Generated to external file (form links to placeholder).
- Questions: Region (Req), City (Req), Confidence (Req), Factors (Req), Reasoning (Req), Ranking (Opt).
- Legend: (RN, SN, GN, DN, EN, TN, WN, QN, ON, MN, CN).
"""

import os
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXAM_FILE = r'C:\Users\shaha\PycharmProjects\thesis\oracc_akkadian_classification\src\scripts_and_results_18_12_2025_creating_evaluation_forms\advisor_package_updated\exam_1_patched.csv'
PLEIADES_CSV = r'C:\Users\shaha\PycharmProjects\thesis\oracc_preprocessing\data\metadata_preprocessing\provenances_to_plaides_data_mapping.csv'
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
REFERENCE_OUTPUT_FILE = os.path.join(BASE_DIR, 'reference_material_for_google_doc.txt')

NUM_TEXTS = 20
SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Regions - Cities from first millennium dataframe with valid Pleiades IDs only (106 cities)
# Full Region Map (106 Cities)
REGION_MAP = {
    # Babylonia (North)
    'Akkad': 'Babylonia (North)', 'Babylon': 'Babylonia (North)', 'Sippar': 'Babylonia (North)', 
    'Kish': 'Babylonia (North)', 'Borsippa': 'Babylonia (North)', 'Kutha': 'Babylonia (North)', 
    'Dilbat': 'Babylonia (North)', 'Dur-Kurigalzu': 'Babylonia (North)', 'Marad': 'Babylonia (North)',
    
    # Babylonia (South)
    'Uruk': 'Babylonia (South)', 'Ur': 'Babylonia (South)', 'Nippur': 'Babylonia (South)', 
    'Larsa': 'Babylonia (South)', 'Isin': 'Babylonia (South)', 'Kissik': 'Babylonia (South)',
    'Larak': 'Babylonia (South)', 
    
    # Eastern Mesopotamia (Diyala region)
    'Der': 'Eastern Mesopotamia', 'Me-Turran': 'Eastern Mesopotamia',
    'Tell Baradan': 'Eastern Mesopotamia',
    
    # Assyria (Core)
    'Assur': 'Assyria', 'Nineveh': 'Assyria', 'Nimrud': 'Assyria', 
    'Dur-Sharrukin': 'Assyria', 'Arbela': 'Assyria', 'Kilizu': 'Assyria', 
    'Tarbisu': 'Assyria', 'Balāwāt': 'Assyria', 'Arrapha': 'Assyria',
    'Jerwan': 'Assyria', 'Bavian': 'Assyria', 'Negub Tunnel': 'Assyria',
    'Wadi Bastura Tunnel': 'Assyria', 'Tell Billa': 'Assyria',
    
    # Assyria (Periphery)
    'Judi Dagh': 'Assyria (Periphery)', 'Dohuk': 'Assyria (Periphery)',
    'Lahiru': 'Assyria (Periphery)', 'Muṣaṣir': 'Assyria (Periphery)', 
    'Mila Mergi': 'Assyria (Periphery)',
    
    # Upper Mesopotamia (Jazira)
    'Dur-Katlimmu': 'Upper Mesopotamia', 'Guzana': 'Upper Mesopotamia', 
    'Huzirina': 'Upper Mesopotamia', 'Harran/Carrhae': 'Upper Mesopotamia', 
    'Tušhan': 'Upper Mesopotamia', 'Tell Barri': 'Upper Mesopotamia', 
    'Kurkh': 'Upper Mesopotamia', 
    'Tell Abu Marya': 'Upper Mesopotamia', 'Tell Ajaja': 'Upper Mesopotamia', 
    'Tell Fakhariyah': 'Upper Mesopotamia', 'Tell al-Hawa': 'Upper Mesopotamia', 
    'Tigris Tunnel': 'Upper Mesopotamia', 'Tell Rimah': 'Upper Mesopotamia', 
    'Tell Abta': 'Upper Mesopotamia', 'Naṣibina': 'Upper Mesopotamia', 'Raṣappa': 'Upper Mesopotamia',
    'Pāra': 'Upper Mesopotamia', 'Sabaʾa': 'Upper Mesopotamia',
    'Samarra': 'Upper Mesopotamia', 'Tikrit': 'Upper Mesopotamia',
    
    # Middle Euphrates
    'Hindanu': 'Middle Euphrates', 'Ana': 'Middle Euphrates', 'Sur Jureh': 'Middle Euphrates',
    'Judeideh': 'Middle Euphrates', 'Dawali': 'Middle Euphrates', 'Zawiyeh': 'Middle Euphrates',
    'Tell Satu Qala': 'Middle Euphrates',
    
    # Syria
    'Til Barsip': 'Syria', 'Carchemish': 'Syria', 'Arslan Tash': 'Syria',
    'Tell Tayinat': 'Syria', 'Turlu Höyük': 'Syria', 'Burmarina': 'Syria',
    'Marqasu': 'Syria', 'Zincirli': 'Syria', 'Tunip': 'Syria', 'Arpadda': 'Syria',
    'Hamath': 'Syria', 'Manṣuate': 'Syria', 'Damascus': 'Syria',
    'Antakya': 'Syria', 'el-Ghab': 'Syria',
    
    # Syria (Periphery)
    'Kizkapanlı': 'Syria (Periphery)', 'Kenk Boǧazı': 'Syria (Periphery)',
    
    # Levant
    'Byblos': 'Levant', 'Samaria': 'Levant', 'Ashdod': 'Levant', 'Larnaka': 'Levant', 
    'Nahr el-Kelb': 'Levant', 'Brissa': 'Levant', 'Selaʾ': 'Levant', 'Ben Shemen': 'Levant',
    'Simyra': 'Levant',
    
    # Iran/Elam
    'Persepolis': 'Iran/Elam', 'Susa': 'Iran/Elam', 'Naqsh-I Rustam': 'Iran/Elam', 
    'Luristan': 'Iran/Elam', 'Zalu-Ab': 'Iran/Elam', 'Elam': 'Iran/Elam',
    'Qalʾeh-i Imam': 'Iran/Elam', 'Tang-i Var': 'Iran/Elam', 'Kalmākarra': 'Iran/Elam', 
    'Najafabad': 'Iran/Elam',
    
    # Anatolia
    'Daskyleion': 'Anatolia', 'Melid': 'Anatolia',
    'Urartu': 'Anatolia',
    
    # Arabia
    'Tayma': 'Arabia', 'Padakku': 'Arabia'
}

LEGEND_TEXT = (
    "Abbreviations Legend (Reference for Text Tags):\n"
    "• RN = Royal Name\n"
    "• SN = Settlement/City Name\n"
    "• GN = Geographical Name\n"
    "• DN = Divine Name\n"
    "• EN = Ethnic Name\n"
    "• TN = Temple Name\n"
    "• WN = Water Name\n"
    "• QN = Quarter Name\n"
    "• ON = Geographical Name (variant)\n"
    "• MN = Month Name\n"
    "• CN = Constellation Name"
)

def load_pleiades_data():
    df = pd.read_csv(PLEIADES_CSV, encoding='utf-8', dtype=str).fillna('')
    location_to_pleiades = {}
    for _, row in df.iterrows():
        location = row.get('city_name', '').strip()
        pleiades_id = row.get('plaides_id', '').strip()
        if location and pleiades_id and pleiades_id not in ['?', '-', '- ', '']:
            # Ensure ID is numeric (or at least looks like an ID, not a citation)
            if str(pleiades_id).strip().isdigit():
                location_to_pleiades[location] = pleiades_id
    
    # manual_additions = {"Mashkan-shapir": "912955"}
    # for loc, pid in manual_additions.items():
    #     if loc not in location_to_pleiades:
    #         location_to_pleiades[loc] = pid
    return location_to_pleiades

def break_autolink(text):
    if not text: return text
    zwsp = '\u200B'
    text = text.replace('.', '.' + zwsp)
    text = text.replace('[', '[' + zwsp)
    text = text.replace(']', zwsp + ']')
    return text

def clean_text(text):
    if not text: return ""
    lines = str(text).splitlines()
    cleaned_lines = [' '.join(line.split()) for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)

def build_pleiades_list(location_to_pleiades):
    """Build the Pleiades reference list grouped by region."""
    lines = []
    # Use the same region order as the form
    regions_order = [
        'Babylonia (North)', 'Babylonia (South)', 
        'Assyria (Heartland)', 'Assyria (Provinces)',
        'Upper Mesopotamia', 'Syria', 'Levant', 
        'Iran/Elam', 'Anatolia', 'Other'
    ]
    region_locations = {r: [] for r in regions_order}
    
    # Group locations by region
    for location, region in REGION_MAP.items():
        if region in region_locations:
            region_locations[region].append(location)
        else:
            # Handle any unmapped regions
            region_locations.setdefault(region, []).append(location)
    
    # Build output
    for region in regions_order:
        locations = region_locations.get(region, [])
        if not locations: continue
        
        # Only add region header if there are locations with IDs
        region_lines = []
        for location in sorted(locations):
            pleiades_id = location_to_pleiades.get(location, '')
            if pleiades_id:
                url = f"https://pleiades.stoa.org/places/{pleiades_id}"
                region_lines.append(f"  • {location}: {url}")
        
        if region_lines:
            lines.append(f"\n{region}:")
            lines.extend(region_lines)
    
    # Add any regions not in priority list
    for region in sorted(region_locations.keys()):
        if region not in regions_order:
            locations = region_locations.get(region, [])
            if not locations: continue
            
            region_lines = []
            for location in sorted(locations):
                pleiades_id = location_to_pleiades.get(location, '')
                if pleiades_id:
                    url = f"https://pleiades.stoa.org/places/{pleiades_id}"
                    region_lines.append(f"  • {location}: {url}")
            
            if region_lines:
                lines.append(f"\n{region}:")
                lines.extend(region_lines)
    
    return "\n".join(lines)

class FinalExamGenerator:
    def __init__(self):
        # Auth
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try: creds.refresh(Request())
                except: creds = None
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token: token.write(creds.to_json())
        
        self.service = build('forms', 'v1', credentials=creds)
        
        # Load Raw Data
        raw_df = pd.read_csv(EXAM_FILE)
        
        # --- Use texts directly from CSV (filtering handled by exam_generator_pipeline) ---
        # The exam CSV should already contain 20 valid, Akkadian texts
        self.df = raw_df.head(NUM_TEXTS).copy()
        
        if len(self.df) < NUM_TEXTS:
            print(f"Warning: Only {len(self.df)} texts in CSV, expected {NUM_TEXTS}.")
        

        
        # 3. Aligned Truncation Logic (100 words) - both texts cut at same point
        MAX_WORDS = 100
        
        def get_aligned_word_count(translit, norm):
            """Get the word count to truncate both texts to (min of both, capped at MAX_WORDS)."""
            t_words = len(str(translit).split()) if pd.notna(translit) else 0
            n_words = len(str(norm).split()) if pd.notna(norm) else 0
            # Use the shorter of the two, but cap at MAX_WORDS
            return min(t_words, n_words, MAX_WORDS)
        
        def truncate_to_count(text, word_count):
            """Truncate text to specified word count while preserving line breaks."""
            if not isinstance(text, str): return ""
            
            # Simple approach: split by all whitespace to count, but iterate via regex to preserve valid structure?
            # Easier: Split by whitespace to find the "cut point" in terms of characters or reconstruction
            
            words = text.split()
            if len(words) <= word_count:
                return text
            
            # Reconstruct up to word_count, but preserving formatting is hard if checking simple split.
            # Alternate approach: Scan text, count whitespace-separated tokens.
            count = 0
            result = []
            import re
            
            # Split by (whitespace) but keep delimiters to preserve newlines
            tokens = re.split(r'(\s+)', text)
            
            for token in tokens:
                if not token.strip():
                    result.append(token) # Append whitespace as is
                else:
                    if count < word_count:
                        result.append(token)
                        count += 1
                    else:
                        break
            
            return "".join(result).strip() + " ... [Excerpt]"
        
        # Calculate aligned word counts for each row
        for idx in self.df.index:
            translit = self.df.at[idx, 'transliterated_text']
            norm = self.df.at[idx, 'normalized text']
            aligned_count = get_aligned_word_count(translit, norm)
            
            # Only truncate if over MAX_WORDS
            if aligned_count < MAX_WORDS:
                aligned_count = MAX_WORDS
            
            self.df.at[idx, 'transliterated_text'] = truncate_to_count(translit, aligned_count)
            self.df.at[idx, 'normalized text'] = truncate_to_count(norm, aligned_count)
        
        self.location_to_pleiades = load_pleiades_data()
        
        # Options
        grouped = {}
        regions_set = set()
        for location, region in REGION_MAP.items():
            # Only include cities that have a valid Pleiades ID in the dropdowns
            if location in self.location_to_pleiades:
                grouped.setdefault(region, []).append(location)
                regions_set.add(region)
            
        # Region Options - ordered for Assyriological sense
        priority = [
            'Babylonia (North)', 'Babylonia (South)', 
            'Assyria (Heartland)', 'Assyria (Provinces)',
            'Upper Mesopotamia', 'Syria', 'Levant', 
            'Iran/Elam', 'Anatolia', 'Other'
        ]
        self.region_options = [{"value": r} for r in priority if r in regions_set]
        for r in sorted(list(regions_set)):
            if r not in priority: self.region_options.append({"value": r})
            
        # City Options
        flat = []
        for r in priority:
            if r in grouped:
                for c in sorted(grouped[r]): flat.append(f"{r} - {c}")
        for r in sorted(grouped.keys()):
            if r not in priority:
                for c in sorted(grouped[r]): flat.append(f"{r} - {c}")
        self.options_json = [{"value": o} for o in flat]

    def create_form(self):
        print(f"Creating Final Exam Form with {len(self.df)} texts...")
        
        # 1. Generate Reference Material File
        pleiades_content = build_pleiades_list(self.location_to_pleiades)
        ref_content = f"{LEGEND_TEXT}\n\n========================================\nCANDIDATE LOCATIONS & PLEIADES LINKS\n========================================{pleiades_content}"
        with open(REFERENCE_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(ref_content)
        print(f"Reference material saved to: {REFERENCE_OUTPUT_FILE}")
        
        # 2. Create Form
        form = self.service.forms().create(body={"info": {"title": "Expert Evaluation - Akkadian Text Classification"}}).execute()
        fid = form['formId']
        url = f"https://docs.google.com/forms/d/{fid}"
        print(f"Form URL: {url}")
        
        # Description
        desc = (
            "Thank you for participating in this expert evaluation.\n\n"
            f"You will be presented with {len(self.df)} texts from the first millennium BCE. "
            "For each text, you will see BOTH the Transliteration AND the Normalization.\n\n"
            "Your Task:\n"
            "1. Read the text excerpt (approx 100 words).\n"
            "2. Identify the likely Region and Primary Location of origin.\n"
            "3. (Optional) Provide alternative candidate locations (Ranking).\n"
            "4. Indicate your confidence and reasoning.\n\n"
            "EXTERNAL REFERENCE:\n"
            "Please open the Reference Document (Abbreviations Legend & Candidate Locations) in a separate tab while working:\n"
            "[INSERT LINK TO GOOGLE DOC HERE]\n\n"
            "You are free to use any Akkadian dictionary and the Pleiades gazetteer. "
            "We recommend that you do not try to research the texts: this isn't a research assignment. "
            "Try as quickly as you can to identify the source of the text and provide your reasoning, then move on. "
            "We would appreciate you submitting the form within a few days.\n\n"
            "Your expertise is invaluable. Thank you for your time."
        )
        self.service.forms().batchUpdate(formId=fid, body={"requests": [{"updateFormInfo": {"info": {"description": desc}, "updateMask": "description"}}]}).execute()
        
        # Settings
        self.service.forms().batchUpdate(formId=fid, body={
            "requests": [{"updateSettings": {"settings": {"quizSettings": {"isQuiz": False}}, "updateMask": "quizSettings.isQuiz"}}]
        }).execute()
        
        # Page 1: Demographics
        demos = [
            {"title": "Academic Status", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "RADIO", "options": [{"value": "MA/PhD Student"}, {"value": "Post-Doc / Researcher"}, {"value": "Tenure-Track / Professor"}, {"value": "Industry Professional"}, {"value": "Other"}]}}}},
            {"title": "Primary Area of Specialization (Select all that apply)", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "CHECKBOX", "options": [{"value": "Old Akkadian / Sargonic"}, {"value": "Old Babylonian"}, {"value": "Old Assyrian"}, {"value": "Middle Babylonian"}, {"value": "Middle Assyrian"}, {"value": "Neo-Assyrian"}, {"value": "Neo-Babylonian / Late Babylonian"}, {"value": "Achaemenid / Persian Period"}, {"value": "Royal Inscriptions"}, {"value": "Letters / Epistolary"}, {"value": "Administrative / Economic"}, {"value": "Legal Texts"}, {"value": "Literary Texts"}, {"value": "Scientific / Scholarly (Medicine, Astrology, Omens)"}, {"value": "Religious / Ritual"}, {"value": "Lexical Texts"}, {"value": "Other"}]}}}},
            {"title": "Other Specialization (Please specify)", "questionItem": {"question": {"textQuestion": {"paragraph": False}}}},
            {"title": "Years of Experience", "questionItem": {"question": {"scaleQuestion": {"low": 1, "high": 10, "lowLabel": "<1 Year", "highLabel": "10+ Years"}}}},
            {"title": "Name / Email", "description": "This is used to identify your responses.", "questionItem": {"question": {"required": True, "textQuestion": {}}}},
            {"title": "Acknowledgment", "description": "We highly appreciate you participating in this study! If you wish to be acknowledged by your name in the article, please check this box.", "questionItem": {"question": {"choiceQuestion": {"type": "CHECKBOX", "options": [{"value": "I wish to be acknowledged by name in the article"}]}}}},
            {"title": "Preferred Name and Affiliation for Acknowledgment", "description": "If you checked the box above, please provide your preferred name and affiliation.", "questionItem": {"question": {"textQuestion": {"paragraph": True}}}}
        ]
        
        batch = []
        index = 0
        for d in demos:
            batch.append({"createItem": {"item": d, "location": {"index": index}}})
            index += 1
        
        # Page Break after Demographics
        batch.append({"createItem": {"item": {"title": "Exam Texts", "description": "Please classify the following texts.", "pageBreakItem": {}}, "location": {"index": index}}})
        index += 1
        
        self.service.forms().batchUpdate(formId=fid, body={"requests": batch}).execute()
        
        # Texts
        batch = []
        print("Adding texts...")
        for i, row in self.df.iterrows():
            idx = i + 1
            
            translit = break_autolink(row.get('transliterated_text', ''))
            norm = break_autolink(row.get('normalized text', ''))
            
            desc_txt = f"[Transliteration]\n{translit}\n\n[Normalization]\n{norm}"
            
            # Text Display
            batch.append({"createItem": {"item": {"title": f"Text {idx}", "description": desc_txt, "textItem": {}}, "location": {"index": index}}})
            index += 1
            
            # Questions
            # Region (Req)
            batch.append({"createItem": {"item": {"title": "Region", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "DROP_DOWN", "options": self.region_options}}}}, "location": {"index": index}}})
            index += 1
            
            # City (Req)
            batch.append({"createItem": {"item": {"title": "Primary Candidate Location (City)", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "DROP_DOWN", "options": self.options_json}}}}, "location": {"index": index}}})
            index += 1
            
            # Ranking (Opt) - Free text to avoid API limits
            batch.append({"createItem": {"item": {"title": "2nd Choice Candidate (Optional)", "description": "Enter city name if you have an alternative guess.", "questionItem": {"question": {"required": False, "textQuestion": {}}}}, "location": {"index": index}}})
            index += 1
            batch.append({"createItem": {"item": {"title": "3rd Choice Candidate (Optional)", "description": "Enter city name if you have another alternative.", "questionItem": {"question": {"required": False, "textQuestion": {}}}}, "location": {"index": index}}})
            index += 1
            
            # Confidence (Req)
            batch.append({"createItem": {"item": {"title": "Confidence", "questionItem": {"question": {"required": True, "scaleQuestion": {"low": 1, "high": 5, "lowLabel": "Low", "highLabel": "High"}}}}, "location": {"index": index}}})
            index += 1
            
            # Factors (Req)
            batch.append({"createItem": {"item": {"title": "Decision Factors", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "CHECKBOX", "options": [{"value": "Onomastics"}, {"value": "Dialect/Grammar"}, {"value": "Orthography"}, {"value": "Vocabulary"}, {"value": "Content/Genre"}, {"value": "Other"}]}}}}, "location": {"index": index}}})
            index += 1
            
            # Reasoning (Req)
            batch.append({"createItem": {"item": {"title": "Your Analysis / Reasoning", "description": "Please share your observations.", "questionItem": {"question": {"required": True, "textQuestion": {"paragraph": True}}}}, "location": {"index": index}}})
            index += 1
            
            # Page Break
            batch.append({"createItem": {"item": {"pageBreakItem": {}}, "location": {"index": index}}})
            index += 1
            
            if len(batch) > 10:
                self.service.forms().batchUpdate(formId=fid, body={"requests": batch}).execute()
                batch = []
                print(f"  Added text {idx}...")
                
        if batch:
            self.service.forms().batchUpdate(formId=fid, body={"requests": batch}).execute()

        # Final Feedback
        final_items = [
            {"title": "Final Feedback", "textItem": {}}, 
            {"title": "General Comments", "description": "Any additional feedback.", "questionItem": {"question": {"textQuestion": {"paragraph": True}}}},
            {"title": "Submission Confirmation", "questionItem": {"question": {"required": True, "choiceQuestion": {"type": "CHECKBOX", "options": [{"value": "I confirm I have classified all texts."}]}}}}
        ]
        
        batch = []
        for it in final_items:
            batch.append({"createItem": {"item": it, "location": {"index": index}}})
            index += 1
        self.service.forms().batchUpdate(formId=fid, body={"requests": batch}).execute()
        
        print("\nDONE!")
        print(f"Form URL: {url}")
        print(f"Reference Material: {REFERENCE_OUTPUT_FILE}")
        return url

if __name__ == "__main__":
    FinalExamGenerator().create_form()
