import pandas as pd
import re

predictions_path = r"/scripts and results - 27_11_2025 - zero shot llm classification witrh gemini-2.5-flash/phase 4 - fixing sender location and recreating train+test/gemini_predictions_first_millenium_with_candidates_list_no_timeframe_no_gn_no_en_with_mapped_city_filters.csv"

df = pd.read_csv(predictions_path)

def analyze_text_quality(text):
    """
    Analyze text quality based on UNK percentage and word count
    Returns: (total_words, non_unk_words, unk_percentage, non_unk_word_count)
    """
    if pd.isna(text):
        return 0, 0, 100.0, 0
    
    text = str(text)
    
    # Split into words
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return 0, 0, 100.0, 0
    
    # Count UNK words
    unk_words = sum(1 for word in words if word.strip() == 'UNK')
    non_unk_words = total_words - unk_words
    
    # Calculate UNK percentage
    unk_percentage = (unk_words / total_words) * 100
    
    return total_words, non_unk_words, unk_percentage, non_unk_words

def classify_text_quality(row):
    """
    Classify text quality based on UNK percentage, word count, and text length
    
    GOOD_QUALITY criteria (tiered by text length):
    - Short texts (< 50 total words): UNK < 35% AND non-UNK >= 10 words
    - Medium texts (50-200 total words): UNK < 50% AND non-UNK >= 25 words  
    - Long texts (200+ total words): UNK < 75% AND non-UNK >= 50 words
    
    This allows longer fragmentary texts to be considered good quality if they 
    have substantial readable content, while maintaining strict standards for short texts.
    """
    text = row['normalized text']
    total_words, non_unk_words, unk_percentage, non_unk_word_count = analyze_text_quality(text)
    
    # Short texts: strict fragmentation requirements
    if total_words < 50:
        if unk_percentage < 35 and non_unk_word_count >= 10:
            return "GOOD_QUALITY"
    
    # Medium texts: moderate fragmentation allowed  
    elif total_words < 200:
        if unk_percentage < 50 and non_unk_word_count >= 25:
            return "GOOD_QUALITY"
    
    # Long texts: high fragmentation allowed if substantial content remains
    else:
        if unk_percentage < 75 and non_unk_word_count >= 50:
            return "GOOD_QUALITY"
    
    return "POOR_QUALITY"

print("Analyzing text quality and prediction errors...")
print(f"Total predictions: {len(df)}")

# Add text quality analysis
print("\nAnalyzing text quality...")
df[['total_words', 'non_unk_words', 'unk_percentage', 'non_unk_word_count']] = df.apply(
    lambda row: pd.Series(analyze_text_quality(row['normalized text'])), axis=1
)

df['text_quality'] = df.apply(classify_text_quality, axis=1)

# Add error analysis
df['is_error'] = df['city_true'] != df['predicted_city_gemini_2.5']

print("\nText Quality Distribution:")
text_quality_counts = df['text_quality'].value_counts()
print(text_quality_counts)

print(f"\nUNK percentage statistics:")
print(f"Mean UNK percentage: {df['unk_percentage'].mean():.2f}%")
print(f"Median UNK percentage: {df['unk_percentage'].median():.2f}%")
print(f"Max UNK percentage: {df['unk_percentage'].max():.2f}%")

print(f"\nWord count statistics (non-UNK words):")
print(f"Mean non-UNK words: {df['non_unk_word_count'].mean():.2f}")
print(f"Median non-UNK words: {df['non_unk_word_count'].median():.2f}")
print(f"Min non-UNK words: {df['non_unk_word_count'].min()}")
print(f"Max non-UNK words: {df['non_unk_word_count'].max()}")

# Analyze errors by text quality
print("\n" + "="*60)
print("PREDICTION ACCURACY BY TEXT QUALITY")
print("="*60)

for quality in ['GOOD_QUALITY', 'POOR_QUALITY']:
    quality_df = df[df['text_quality'] == quality]
    if len(quality_df) == 0:
        continue
    
    errors = quality_df['is_error'].sum()
    total = len(quality_df)
    accuracy = (total - errors) / total
    
    print(f"\n{quality}:")
    print(f"  Total texts: {total}")
    print(f"  Correct predictions: {total - errors}")
    print(f"  Wrong predictions: {errors}")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Show some examples of errors with poor quality text
print("\n" + "="*60)
print("EXAMPLES OF ERRORS WITH POOR QUALITY TEXT")
print("="*60)

poor_quality_errors = df[(df['text_quality'] == 'POOR_QUALITY') & (df['is_error'] == True)]
print(f"\nTotal poor quality errors: {len(poor_quality_errors)}")

if len(poor_quality_errors) > 0:
    print("\nTop 10 examples:")
    for i, (idx, row) in enumerate(poor_quality_errors.head(10).iterrows()):
        print(f"\n{i+1}. {row['project']}/{row['textid']}")
        print(f"   True: {row['city_true']} | Predicted: {row['predicted_city_gemini_2.5']}")
        print(f"   UNK%: {row['unk_percentage']:.1f}% | Non-UNK words: {row['non_unk_word_count']}")
        text_sample = str(row['normalized text'])[:100] + "..." if len(str(row['normalized text'])) > 100 else str(row['normalized text'])
        print(f"   Text: {text_sample}")

# Show some examples of errors with good quality text  
print("\n" + "="*60)
print("EXAMPLES OF ERRORS WITH GOOD QUALITY TEXT")
print("="*60)

good_quality_errors = df[(df['text_quality'] == 'GOOD_QUALITY') & (df['is_error'] == True)]
print(f"\nTotal good quality errors: {len(good_quality_errors)}")

if len(good_quality_errors) > 0:
    print("\nTop 10 examples:")
    for i, (idx, row) in enumerate(good_quality_errors.head(10).iterrows()):
        print(f"\n{i+1}. {row['project']}/{row['textid']}")
        print(f"   True: {row['city_true']} | Predicted: {row['predicted_city_gemini_2.5']}")
        print(f"   UNK%: {row['unk_percentage']:.1f}% | Non-UNK words: {row['non_unk_word_count']}")
        text_sample = str(row['normalized text'])[:100] + "..." if len(str(row['normalized text'])) > 100 else str(row['normalized text'])
        print(f"   Text: {text_sample}")

# Save detailed results
output_path = "error_analysis_by_text_quality.csv"
df_output = df[['project', 'textid', 'city_true', 'predicted_city_gemini_2.5', 'is_error', 
                'text_quality', 'unk_percentage', 'non_unk_word_count', 'total_words', 'normalized text']]
df_output.to_csv(output_path, index=False)
print(f"\nDetailed results saved to: {output_path}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total predictions analyzed: {len(df)}")
print(f"Overall accuracy: {(1 - df['is_error'].mean()):.4f} ({(1 - df['is_error'].mean())*100:.2f}%)")
print(f"Good quality texts: {len(df[df['text_quality'] == 'GOOD_QUALITY'])}")
print(f"Poor quality texts: {len(df[df['text_quality'] == 'POOR_QUALITY'])}")

good_accuracy = (1 - df[df['text_quality'] == 'GOOD_QUALITY']['is_error'].mean()) if len(df[df['text_quality'] == 'GOOD_QUALITY']) > 0 else 0
poor_accuracy = (1 - df[df['text_quality'] == 'POOR_QUALITY']['is_error'].mean()) if len(df[df['text_quality'] == 'POOR_QUALITY']) > 0 else 0

print(f"Good quality accuracy: {good_accuracy:.4f} ({good_accuracy*100:.2f}%)")
print(f"Poor quality accuracy: {poor_accuracy:.4f} ({poor_accuracy*100:.2f}%)")

if good_accuracy > 0 and poor_accuracy > 0:
    improvement = good_accuracy - poor_accuracy
    print(f"Quality improvement: {improvement:.4f} ({improvement*100:.2f} percentage points)")

# PREDICTION CONFIDENCE ANALYSIS
print("\n" + "="*80)
print("PREDICTION CONFIDENCE ANALYSIS")
print("="*80)

def analyze_prediction_confidence(gemini_response):
    """
    Analyze confidence indicators in Gemini's response
    Returns: (response_length, uncertainty_indicators, confidence_score, reasoning_quality)
    """
    if pd.isna(gemini_response):
        return 0, 0, 0.0, "NO_RESPONSE"
    
    response = str(gemini_response).lower()
    
    # Response length (proxy for reasoning detail)
    response_length = len(response.split())
    
    # Uncertainty indicators
    uncertainty_words = [
        'possibly', 'likely', 'probably', 'might', 'could', 'may', 'perhaps', 
        'seems', 'appears', 'suggests', 'indicates', 'uncertain', 'unclear',
        'difficult', 'challenging', 'ambiguous', 'fragmentary', 'incomplete',
        'limited', 'insufficient', 'scarce', 'tentative', 'provisional',
        'however', 'although', 'but', 'nevertheless', 'nonetheless'
    ]
    
    uncertainty_count = sum(1 for word in uncertainty_words if word in response)
    
    # Confidence indicators  
    confidence_words = [
        'clearly', 'definitely', 'certainly', 'obviously', 'undoubtedly',
        'strongly', 'consistently', 'characteristic', 'typical', 'distinctive',
        'conclusive', 'evident', 'apparent', 'manifest', 'unambiguous'
    ]
    
    confidence_count = sum(1 for word in confidence_words if word in response)
    
    # Calculate confidence score (confidence words - uncertainty words, normalized)
    net_confidence = confidence_count - uncertainty_count
    confidence_score = max(0, min(10, net_confidence + 5))  # Scale 0-10
    
    # Reasoning quality based on response length and structure
    if response_length < 50:
        reasoning_quality = "BRIEF"
    elif response_length < 150:
        reasoning_quality = "MODERATE" 
    else:
        reasoning_quality = "DETAILED"
        
    return response_length, uncertainty_count, confidence_score, reasoning_quality

# Apply confidence analysis
print("Analyzing prediction confidence...")
df[['response_length', 'uncertainty_indicators', 'confidence_score', 'reasoning_quality']] = df.apply(
    lambda row: pd.Series(analyze_prediction_confidence(row['gemini_response'])), axis=1
)

# Confidence statistics
print(f"\nConfidence Score Statistics:")
print(f"Mean confidence score: {df['confidence_score'].mean():.2f}")
print(f"Median confidence score: {df['confidence_score'].median():.2f}")
print(f"Min confidence score: {df['confidence_score'].min()}")
print(f"Max confidence score: {df['confidence_score'].max()}")

print(f"\nResponse Length Statistics:")
print(f"Mean response length: {df['response_length'].mean():.2f} words")
print(f"Median response length: {df['response_length'].median():.2f} words")
print(f"Min response length: {df['response_length'].min()} words")
print(f"Max response length: {df['response_length'].max()} words")

print(f"\nReasoning Quality Distribution:")
reasoning_counts = df['reasoning_quality'].value_counts()
print(reasoning_counts)

# Analyze accuracy by confidence level
print("\n" + "-"*60)
print("ACCURACY BY CONFIDENCE LEVEL")
print("-"*60)

# Create confidence bins
df['confidence_bin'] = pd.cut(df['confidence_score'], bins=[0, 3, 6, 10], labels=['LOW', 'MEDIUM', 'HIGH'])

for conf_level in ['LOW', 'MEDIUM', 'HIGH']:
    conf_df = df[df['confidence_bin'] == conf_level]
    if len(conf_df) == 0:
        continue
    
    errors = conf_df['is_error'].sum()
    total = len(conf_df)
    accuracy = (total - errors) / total
    
    avg_conf_score = conf_df['confidence_score'].mean()
    avg_uncertainty = conf_df['uncertainty_indicators'].mean()
    
    print(f"\n{conf_level} CONFIDENCE:")
    print(f"  Total predictions: {total}")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Avg confidence score: {avg_conf_score:.2f}")
    print(f"  Avg uncertainty indicators: {avg_uncertainty:.2f}")

# Analyze accuracy by reasoning quality
print("\n" + "-"*60)
print("ACCURACY BY REASONING QUALITY")
print("-"*60)

for quality in ['BRIEF', 'MODERATE', 'DETAILED']:
    quality_df = df[df['reasoning_quality'] == quality]
    if len(quality_df) == 0:
        continue
    
    errors = quality_df['is_error'].sum()
    total = len(quality_df)
    accuracy = (total - errors) / total
    
    avg_length = quality_df['response_length'].mean()
    avg_conf_score = quality_df['confidence_score'].mean()
    
    print(f"\n{quality} REASONING:")
    print(f"  Total predictions: {total}")
    print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Avg response length: {avg_length:.1f} words")
    print(f"  Avg confidence score: {avg_conf_score:.2f}")

# Examples of high confidence errors
print("\n" + "="*80)
print("HIGH CONFIDENCE ERRORS (Overconfident mistakes)")
print("="*80)

high_conf_errors = df[(df['confidence_bin'] == 'HIGH') & (df['is_error'] == True)]
print(f"\nTotal high confidence errors: {len(high_conf_errors)}")

if len(high_conf_errors) > 0:
    print("\nTop 5 overconfident mistakes:")
    high_conf_sorted = high_conf_errors.sort_values('confidence_score', ascending=False)
    
    for i, (idx, row) in enumerate(high_conf_sorted.head(5).iterrows()):
        print(f"\n{i+1}. {row['project']}/{row['textid']}")
        print(f"   True: {row['city_true']} | Predicted: {row['predicted_city_gemini_2.5']}")
        print(f"   Confidence Score: {row['confidence_score']}")
        print(f"   Uncertainty Indicators: {row['uncertainty_indicators']}")
        print(f"   Response Length: {row['response_length']} words")
        print(f"   Text Quality: {row['text_quality']}")
        
        # Show a portion of the reasoning
        response_sample = str(row['gemini_response'])[:300] + "..." if len(str(row['gemini_response'])) > 300 else str(row['gemini_response'])
        print(f"   Reasoning: {response_sample}")

# Correlation analysis
print("\n" + "="*80)
print("CONFIDENCE vs ACCURACY CORRELATIONS")
print("="*80)

# Compute correlations
corr_conf_accuracy = df['confidence_score'].corr(~df['is_error'])  # Correlation with being correct
corr_length_accuracy = df['response_length'].corr(~df['is_error'])
corr_uncertainty_accuracy = df['uncertainty_indicators'].corr(df['is_error'])  # Correlation with being wrong

print(f"Confidence Score vs Accuracy: {corr_conf_accuracy:.4f}")
print(f"Response Length vs Accuracy: {corr_length_accuracy:.4f}")
print(f"Uncertainty Indicators vs Error Rate: {corr_uncertainty_accuracy:.4f}")

print(f"\nInterpretation:")
if corr_conf_accuracy > 0.1:
    print("✓ Higher confidence scores are associated with better accuracy")
elif corr_conf_accuracy < -0.1:
    print("⚠ Higher confidence scores are associated with worse accuracy (overconfidence)")
else:
    print("- Confidence scores show little correlation with accuracy")

if corr_length_accuracy > 0.1:
    print("✓ Longer, more detailed responses are associated with better accuracy")
elif corr_length_accuracy < -0.1:
    print("⚠ Longer responses are associated with worse accuracy")
else:
    print("- Response length shows little correlation with accuracy")

if corr_uncertainty_accuracy > 0.1:
    print("✓ More uncertainty indicators are appropriately associated with higher error rates")
elif corr_uncertainty_accuracy < -0.1:
    print("⚠ Uncertainty indicators are inversely related to errors (may indicate overconfidence in wrong answers)")
else:
    print("- Uncertainty indicators show little correlation with error rates")

# Save enhanced results with confidence metrics
output_path_enhanced = "error_analysis_with_confidence.csv"
df_output_enhanced = df[['project', 'textid', 'city_true', 'predicted_city_gemini_2.5', 'is_error', 
                        'text_quality', 'unk_percentage', 'non_unk_word_count', 'total_words',
                        'confidence_score', 'confidence_bin', 'uncertainty_indicators', 
                        'response_length', 'reasoning_quality', 'normalized text', 'gemini_response']]
df_output_enhanced.to_csv(output_path_enhanced, index=False)
print(f"\nEnhanced results with confidence metrics saved to: {output_path_enhanced}")

# Save good quality texts with errors for detailed analysis
good_quality_errors = df[(df['text_quality'] == 'GOOD_QUALITY') & (df['is_error'] == True)]
print(f"\nGood quality texts with errors: {len(good_quality_errors)}")

# Select ALL relevant columns for comprehensive error analysis
good_quality_errors_output = good_quality_errors[[
    'project', 'textid', 'city_true', 'predicted_city_gemini_2.5', 
    'writing_start_year', 'writing_end_year', 'genre',
    'unk_percentage', 'non_unk_word_count', 'total_words',
    'confidence_score', 'confidence_bin', 'uncertainty_indicators', 
    'response_length', 'reasoning_quality', 
    'translation', 'normalized text', 'lemmatized_text', 'transliterated_text',
    'input_text_source', 'user_message_gemini_2.5_fast', 'gemini_response'
]].copy()

# Add some helpful analysis columns
good_quality_errors_output['prediction_pair'] = (
    good_quality_errors_output['city_true'] + ' -> ' + good_quality_errors_output['predicted_city_gemini_2.5']
)

# Add text length category
def categorize_text_length(word_count):
    if word_count < 20:
        return "SHORT"
    elif word_count < 100:
        return "MEDIUM" 
    elif word_count < 500:
        return "LONG"
    else:
        return "VERY_LONG"

good_quality_errors_output['text_length_category'] = good_quality_errors_output['non_unk_word_count'].apply(categorize_text_length)

# Sort by confidence score (highest confidence errors first)
good_quality_errors_output = good_quality_errors_output.sort_values('confidence_score', ascending=False)

# Save to CSV
good_quality_errors_path = "good_quality_texts_with_errors.csv"
good_quality_errors_output.to_csv(good_quality_errors_path, index=False)
print(f"Good quality texts with errors saved to: {good_quality_errors_path}")

print(f"\nBreakdown of good quality errors:")
print(f"  Total good quality errors: {len(good_quality_errors_output)}")
print(f"  High confidence errors: {len(good_quality_errors_output[good_quality_errors_output['confidence_bin'] == 'HIGH'])}")
print(f"  Medium confidence errors: {len(good_quality_errors_output[good_quality_errors_output['confidence_bin'] == 'MEDIUM'])}")
print(f"  Low confidence errors: {len(good_quality_errors_output[good_quality_errors_output['confidence_bin'] == 'LOW'])}")

print(f"\nText length distribution of good quality errors:")
length_dist = good_quality_errors_output['text_length_category'].value_counts()
print(length_dist)

print(f"\nTop 10 prediction pairs in good quality errors:")
top_pairs = good_quality_errors_output['prediction_pair'].value_counts().head(10)
print(top_pairs)


