"""Service for analyzing and classifying text quality."""

import pandas as pd
from typing import Tuple

from akkadian_classification.models.text import QualityMetrics


class TextQualityService:
    """Service for assessing text quality based on damage markers."""
    
    # Damage indicators
    DAMAGE_MARKERS = ['UNK', 'x', '[', ']', '...', '⸢', '⸣']
    
    def analyze_text(self, text: str) -> QualityMetrics:
        """Analyze text quality by counting damaged vs clean words.
        
        Damage indicators:
        - UNK: Unknown/unreadable text
        - x: Damaged/illegible character
        - [, ]: Editorial restoration brackets
        - ...: Text breaks
        - ⸢, ⸣: Half brackets (damaged but partially readable)
        
        Args:
            text: The text to analyze (typically normalized text)
        
        Returns:
            QualityMetrics with word counts and damage percentage
        """
        if pd.isna(text):
            return QualityMetrics(
                total_words=0,
                clean_words=0,
                damaged_words=0,
                damage_percentage=100.0
            )
        
        text = str(text)
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return QualityMetrics(
                total_words=0,
                clean_words=0,
                damaged_words=0,
                damage_percentage=100.0
            )
        
        damaged_count = 0
        for word in words:
            # Strip punctuation to catch "UNK." or "(UNK)"
            clean_word = word.strip(".,;:!?()[]")
            
            # Check for any damage marker
            if any(marker in word for marker in self.DAMAGE_MARKERS):
                damaged_count += 1
        
        clean_words = total_words - damaged_count
        damage_percentage = (damaged_count / total_words) * 100
        
        return QualityMetrics(
            total_words=total_words,
            clean_words=clean_words,
            damaged_words=damaged_count,
            damage_percentage=damage_percentage
        )
    
    def classify_quality(self, text: str) -> str:
        """Classify text quality as GOOD_QUALITY or POOR_QUALITY.
        
        Quality thresholds based on text length:
        - Short (<50 words): Max 20% damage
        - Medium (50-200 words): Max 30% damage
        - Long (200+ words): Max 40% damage
        
        Args:
            text: The text to classify (typically normalized text)
        
        Returns:
            'GOOD_QUALITY' or 'POOR_QUALITY'
        """
        metrics = self.analyze_text(text)
        return metrics.quality_classification
    
    def classify_from_metrics(self, metrics: QualityMetrics) -> str:
        """Get quality classification from pre-computed metrics.
        
        Args:
            metrics: Pre-computed QualityMetrics
        
        Returns:
            'GOOD_QUALITY' or 'POOR_QUALITY'
        """
        return metrics.quality_classification
