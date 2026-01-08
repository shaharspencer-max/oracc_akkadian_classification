# 1. https://gemini.google.com/app/d5a0904bfabaa5fd


Methodological Report: Zero-Shot Geolocation of Akkadian Texts via Large Language Models1. ObjectiveThe primary objective was to establish a rigorous baseline for predicting the geographical provenance of 2nd and 1st Millennium BCE Akkadian texts using an off-the-shelf Large Language Model (gemini-2.5-flash). The goal was to assess the model's ability to utilize lexical, morphological, and orthographic variation for geolocation, rather than relying on simple entity recognition (NER) or memorized historical facts.2. Data Pre-processing & Masking StrategyTo ensure the model performed genuine linguistic analysis rather than "entity lookup," a strict masking protocol was developed. We categorized entities into "Spoilers" (direct labels of location) and "Features" (cultural signals).2.1 The "Gentilic Leak" & The "Crowd" HypothesisA critical methodological decision was distinguishing between Ethnic Names (EN) and Personal Names (PN).Decision: We masked Ethnic Names (EN) because they often function as "Gentilics" (e.g., Aššurāyu = "The Assyrian"), which act as direct labels for the city of origin.Decision: We preserved Personal Names (PN). Following Eisenstein et al. (2010) regarding latent variables in geographic lexical variation, we hypothesized that the distribution of names (Onomastics) serves as a valid cultural fingerprint (e.g., Hurrian names indicating the Nuzi cluster) without explicitly revealing the city name.2.2 Final Baseline Masking ProtocolThe following Named Entity tags were masked with generic tokens (e.g., [GN], [RN]) to prevent data leakage:Geographical Markers: GN (Geo Name), SN (City), TN (Temple), WN (River), QN (Quarter).Political/Religious Proxies: RN / KN (Kings, who are chronological/spatial anchors), DN (Divine Names, as Patron Deities effectively label cities).Explicit Labels: EN (Ethnic Names/Gentilics).Unmasked Features: PN (Personal Names) and LN (Family Names) were retained to provide onomastic signals for clustering.3. Prompt Engineering & System ConstraintsInitial experiments using open-ended prompting resulted in significant "Gravity Well" bias, where provincial texts were consistently misclassified as major capitals (e.g., Tell Rimah $\rightarrow$ Assur).To correct this, a Constrained Candidate System was implemented:Regional Grouping: The model was provided with a closed list of candidates grouped by region (e.g., Assyria, Babylonia, Levant - Coastal, Levant - Inland). This reduced cross-regional hallucinations (e.g., confusing Ugarit with Nuzi).Base Rate Correction: Specific heuristics were encoded to counter training data bias. For example, in the Amarna corpus, the model was instructed to weigh Byblos higher than Jerusalem absent specific "Inland" keywords.Chain-of-Thought (CoT): The model was required to output a "Philological Analysis" regarding dialect and morphology before generating the final classification tag.4. Experimental Results & Error Analysis4.1 The "Capital City" Bias (Neo-Assyria)The confusion matrix revealed a distinct "Neo-Assyrian Gravity Well."Observation: Texts from Nimrud (Kalhu) were frequently misclassified as Nineveh.Analysis: Without Royal Names (RN) to distinguish the era (e.g., Ashurnasirpal II vs. Ashurbanipal), the dialect of the Neo-Assyrian chancellery is effectively identical across these capitals. The model defaulted to Nineveh due to its higher representation in the training corpus.Implication: The model successfully identified the "Assyrian Cluster" but struggled with fine-grained city distinction within the core heartland.4.2 The "Library" Effect (Babylonia vs. Assyria)Observation: Standard Babylonian literary texts found at Nineveh were often predicted as Babylon.Analysis: This represents a correct linguistic classification but an incorrect archaeological one. The model identified the Standard Babylonian dialect correctly, ignoring the physical find-spot (the Library of Ashurbanipal).Success: The model achieved 100% accuracy on true Babylonian texts, proving it successfully distinguishes the Southern dialect from the Northern (Assyrian) dialect solely on grammatical features.4.3 The Amarna ImprovementInitial runs showed a massive bias toward "Biblical" cities (Jerusalem, Lachish). After implementing "Coastal vs. Inland" candidate splitting and base-rate constraints, the model began correctly identifying Phoenician coastal origins (Byblos, Tyre) based on maritime context and formulaic distinctiveness.5. Conclusion & MetricsThe "Baseline" performance demonstrates that gemini-2.5-flash can act as a Dialect Classifier but requires careful constraints to act as a Provenance Predictor.Future Evaluation Metrics (per Advisory Board recommendations):Geodesic Error: Measuring Haversine distance between Predicted and True coordinates to penalize "near misses" (e.g., Nimrud $\rightarrow$ Nineveh) less than "far misses."Cluster Accuracy: Evaluating performance based on 100km/150km geographic clusters, where identifying the correct cultural zone (e.g., Middle Euphrates) is weighted positively even if the specific city is incorrect.





# 2. https://gemini.google.com/app/489c38b368b5c45b


Research Report: Evaluating LLM Capabilities in Geolocation of Masked Akkadian Texts
Model Evaluated: Gemini Flash 2.5 Task: Zero-shot classification of city-of-origin for 1st Millennium BCE Akkadian texts. Methodology:

Input Data: Akkadian cuneiform transliterations.

Control Variable: Entity Masking. All Proper Nouns (Personal Names PN, Geographic Names GN, Divine Names DN) were masked to force the model to rely on linguistic features (orthography, morphology, formula) rather than keyword association.

Prompt Strategy: Expert System Prompt ("Expert in Akkadian regional dialects") with a fixed list of candidate locations.

1. Experiment A: The Impact of Temporal Metadata
Setup: The model was provided with the WRITING_TIMEFRAME (e.g., "705–681 BCE") alongside the masked text.

Key Observations
High Regional Fidelity (The "Regional Firewall"): The model demonstrated near-perfect separation between the Northern (Assyrian) and Southern (Babylonian) dialect groups. False positives crossing the regional boundary were statistically negligible.

The "Nineveh Magnet" (Class Imbalance & Standardization): A significant bias was observed where texts from secondary Assyrian sites (Assur, Nimrud, Dur-Katlimmu) were misclassified as Nineveh.

Analysis: Nineveh acts as the "Standard Neo-Assyrian" bucket. Due to the standardization of the Neo-Assyrian chancery script and the dominance of the Library of Ashurbanipal in the training corpus, the model treats "Nineveh" as the default label for any standard Assyrian text lacking specific local markers.

The "Dur-Sharrukin" Anomaly (Historical Over-reliance): The model frequently predicted Dur-Sharrukin for texts found in Nineveh that dated to the Sargonid period.

Analysis: This reveals a conflict between Composition and Provenance. The model utilized the WRITING_TIMEFRAME to deduce the active political capital (Dur-Sharrukin) rather than the archaeological find-spot (Nineveh). This indicates the model prioritized historical logic over linguistic analysis.

The Babylon/Borsippa Identity Crisis: The model failed to distinguish Borsippa from Babylon, splitting Borsippa texts between Babylon and Uruk.

Analysis: This reflects the "Twin City" historical reality. The proximity and shared theological/scribal culture between Borsippa and Babylon resulted in a legal and administrative dialect so similar that, without explicit city names, they are computationally indistinguishable to the model.

2. Experiment B: Ablation Study (Removal of Timeframe)
Setup: The WRITING_TIMEFRAME was removed. The model had to classify based on the masked text alone.

Key Observations
Collapse of the "Political Guardrail": Without the date to anchor the text to the "Neo-Assyrian Empire," the distinction between Assyrian sites and Babylonian sites weakened for specific genres.

The "Standard Babylonian" Leak: A distinct pattern emerged where texts from Nimrud (North) were misclassified as Babylon (South).

Analysis: Many texts in Assyrian libraries were written in "Standard Babylonian" (the literary/scholarly dialect). Without the date to frame the text as "Assyrian property," the model classified the dialect purely linguistically. Since the dialect was Babylonian in origin, the model defaulted to Babylon.

Babylon as the "Super-Attractor": The model’s reliance on priors increased. Babylon absorbed significant probability mass from smaller sites (Burmarina, Nimrud). This suggests that in the absence of strong differentiating features, the model reverts to the mean (the most statistically probable city in its training data).

3. Discussion & Conclusions
The Limits of "Computational Philology"
The experiments demonstrate that while Large Language Models possess a strong understanding of Akkadian regional macro-dialects (Assyrian vs. Babylonian), they struggle with micro-regional geolocation (City A vs. City B).

The Role of Named Entities vs. Style
By masking named entities, we proved that the model’s previous successes in this domain likely relied on "keyword spotting" (e.g., identifying a specific temple name). When forced to rely on morphology and orthography alone:

Legal/Administrative Texts remained identifiable by region (North/South) due to distinct formulaic structures.

Scholarly/Literary Texts lost their geographic signal, as the "Standard Babylonian" dialect was used internationally, making it a poor feature for geolocation without metadata.

Final Verdict
The model operates effectively as a Chronological and Regional Classifier but fails as a reliable Archival Classifier. It can determine when a text was written (based on linguistic evolution) and roughly where (North vs. South), but it cannot currently replicate the specific idiolects of local scribal schools without the aid of prosopography (names) or explicit historical metadata.




# 3. https://gemini.google.com/app/0750c79a7f1ec21b




1. ObjectiveTo evaluate the capability of a Large Language Model (LLM) to identify the geographical origin and authorship of a Late Bronze Age diplomatic letter (Amarna Archive) under two distinct conditions:Condition A (Blind/Masked): Transliterated Akkadian text with Named Entities (NEs) masked.Condition B (Unmasked): English translation with Named Entities visible.2. MethodologyThe text selected for analysis was EA 362, a letter from Rib-Hadda of Byblos to the Egyptian Pharaoh.Input A: A transliteration of the text where specific proper nouns (Person Names, Geographic Names) were replaced with generic tokens (PN, GN, UNK).Input B: The full English translation of the text with names restored (e.g., "Rib-Addi," "Byblos," "Abdi-Ashirta").Constraint: The model was instructed to use internal knowledge only and prohibited from using external search tools.3. ResultsTest ConditionInput TypeModel PredictionAccuracyConfidence StatedA (Masked)Transliterated Akkadian (Masked NEs)Jerusalem (Abdi-Heba)IncorrectHighB (Unmasked)English Translation (Visible NEs)Byblos (Rib-Hadda)CorrectHigh4. Analysis of Error (Condition A)In the absence of prosopographical data (names of people and places), the model correctly identified the text as a Canaanite-Akkadian letter from the Amarna Period (c. 1350 BCE). However, it misattributed the specific city of origin to Jerusalem.Factors contributing to the misclassification:Shared Vocabulary: The text contained terms common to both the Jerusalem and Byblos corpora, specifically habirī (renegades/mercenaries) and ṣābī piṭṭāti (Egyptian archers).Rhetorical Overlap: The tone of desperation, the claims of being "slandered" (karṣi), and the warning that "the land will be lost" are tropes shared by both Rib-Hadda (Byblos) and Abdi-Heba (Jerusalem).The "Habiru" Signal: The model heavily weighted the mention of habirī as a marker for Jerusalem, despite the term appearing frequently in the Byblos correspondence as well.5. DiscussionThe experiment demonstrates that while the LLM possesses a strong typological understanding of the Amarna corpus (correctly identifying the language dialect and historical era), it struggles to differentiate between specific Levantine polities based solely on rhetorical structure and generic vocabulary.The model exhibited "hallucinated confidence" in Condition A, assigning a high probability to the Jerusalem attribution based on circumstantial linguistic evidence. Correct identification was only achieved in Condition B when unique Named Entities (Rib-Addi, Byblos, Abdi-Ashirta) were reintroduced, indicating that the model relies more heavily on prosopography than on dialectal nuances for fine-grained geolocation.






# 4. https://gemini.google.com/app/876e2ed6eb582cae




Here is a summary of the methodology and rationale we discussed for your Akkadian city classification project. You can use this structure for your report or methodology section.

Methodology Summary: Conditional Feature Engineering by Era
Objective: To train a model to identify the city of origin for Akkadian texts while mitigating historical data biases and preventing data leakage.

Core Strategy: A "Hybrid Feature Selection" approach where the input features change based on the historical era of the text.

1. Global Pre-processing: Proper Noun Masking
Action: All Proper Nouns (PNs) and Geographic Names (GNs) are masked in the input text.

Rationale: Prevents direct data leakage. The model must learn scribal habits and dialect, not simply read the city name (e.g., "I am in Sippar") or specific local officials' names to make a prediction.

Constraint: Masking must include Gentilics (e.g., lú-UD.KIB.NUN{ki} / "The Sipparian") to ensure total blinding.

2. The 2nd Millennium Strategy: Retaining Timeframe
Action: The "Writing Timeframe" is included as a feature.

Rationale:

Living Dialects: 2nd Millennium dialects (Old/Middle Babylonian vs. Old/Middle Assyrian) were distinct and evolving. Time serves as a valid linguistic proxy to help the model distinguish temporal language shifts (e.g., loss of mimation) from regional variations.

Archive Distribution: Excavated texts from this era are distributed across many competing powers (Mari, Larsa, Babylon, Assur). Therefore, a specific date does not statistically guarantee a specific city, avoiding the "shortcut" problem.

3. The 1st Millennium Strategy: Dropping Timeframe
Action: The "Writing Timeframe" is masked or imputed (replaced with a generic token) for all texts.

Rationale:

The "Nineveh Effect": The 1st Millennium dataset is heavily skewed toward the Library of Ashurbanipal (Nineveh). Including dates creates a statistical bias where the model ignores the text and predicts "Nineveh" based solely on the 7th-century timestamp.

Standard Babylonian (SB): Scribes in this era often used a "frozen" literary dialect common to both Assyria and Babylonia. Removing the date forces the model to ignore the generic literary style and focus on subtle clues: specific orthography (sign usage) and vocabulary (e.g., Aramaisms) to distinguish Neo-Assyrian from Neo-Babylonian origins.

Conclusion: By treating the two millennia differently, the model is forced to learn linguistic evolution in the 2nd Millennium and scribal idiosyncrasies in the 1st Millennium, resulting in a robust classifier that does not rely on archaeological metadata biases.