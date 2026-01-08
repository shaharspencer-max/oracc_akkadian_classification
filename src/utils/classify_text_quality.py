import pandas as pd


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