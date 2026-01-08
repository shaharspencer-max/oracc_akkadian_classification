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