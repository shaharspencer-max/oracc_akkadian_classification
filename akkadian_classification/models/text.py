"""Core domain models for Akkadian text analysis."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LanguageStats:
    """Statistics about languages present in a text."""
    akkadian_pct: float
    sumerian_pct: float
    other_pct: float
    total_words: int
    
    def is_primarily_akkadian(self, threshold: float = 70.0) -> bool:
        """Check if text is primarily Akkadian based on threshold."""
        return self.akkadian_pct >= threshold


@dataclass
class QualityMetrics:
    """Text quality metrics based on damage markers."""
    total_words: int
    clean_words: int
    damaged_words: int
    damage_percentage: float
    
    @property
    def quality_classification(self) -> str:
        """Classify text quality based on length and damage percentage.
        
        Thresholds:
        - Short (<50 words): Max 20% damage
        - Medium (50-200 words): Max 30% damage
        - Long (200+ words): Max 40% damage
        """
        if self.total_words < 50:
            max_damage = 20.0
        elif self.total_words < 200:
            max_damage = 30.0
        else:
            max_damage = 40.0
        
        return "GOOD_QUALITY" if self.damage_percentage < max_damage else "POOR_QUALITY"


@dataclass
class AkkadianText:
    """Represents an Akkadian text with all its representations and metadata."""
    project: str
    textid: str
    transliterated_text: str
    normalized_text: str
    lemmatized_text: Optional[str] = None
    translation: Optional[str] = None
    
    # Metadata
    city: Optional[str] = None
    writing_start_year: Optional[int] = None
    writing_end_year: Optional[int] = None
    genre: Optional[str] = None
    
    # Analysis results (computed separately)
    quality_metrics: Optional[QualityMetrics] = None
    language_stats: Optional[LanguageStats] = None
    
    @property
    def id(self) -> str:
        """Unique identifier combining project and textid."""
        return f"{self.project}:{self.textid}"
    
    def __str__(self) -> str:
        return f"AkkadianText({self.id}, city={self.city}, genre={self.genre})"
