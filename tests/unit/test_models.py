"""Unit tests for domain models."""

import pytest
from akkadian_classification.models.text import (
    AkkadianText,
    LanguageStats,
    QualityMetrics
)


class TestLanguageStats:
    """Tests for LanguageStats model."""
    
    def test_create_language_stats(self):
        stats = LanguageStats(
            akkadian_pct=75.0,
            sumerian_pct=20.0,
            other_pct=5.0,
            total_words=100
        )
        assert stats.akkadian_pct == 75.0
        assert stats.sumerian_pct == 20.0
        assert stats.total_words == 100
    
    def test_is_primarily_akkadian_default_threshold(self):
        # Above default threshold (70%)
        stats_high = LanguageStats(
            akkadian_pct=75.0,
            sumerian_pct=20.0,
            other_pct=5.0,
            total_words=100
        )
        assert stats_high.is_primarily_akkadian() is True
        
        # Below default threshold
        stats_low = LanguageStats(
            akkadian_pct=65.0,
            sumerian_pct=30.0,
            other_pct=5.0,
            total_words=100
        )
        assert stats_low.is_primarily_akkadian() is False
    
    def test_is_primarily_akkadian_custom_threshold(self):
        stats = LanguageStats(
            akkadian_pct=75.0,
            sumerian_pct=20.0,
            other_pct=5.0,
            total_words=100
        )
        assert stats.is_primarily_akkadian(threshold=80.0) is False
        assert stats.is_primarily_akkadian(threshold=70.0) is True
        assert stats.is_primarily_akkadian(threshold=50.0) is True


class TestQualityMetrics:
    """Tests for QualityMetrics model."""
    
    def test_create_quality_metrics(self):
        metrics = QualityMetrics(
            total_words=100,
            clean_words=80,
            damaged_words=20,
            damage_percentage=20.0
        )
        assert metrics.total_words == 100
        assert metrics.clean_words == 80
        assert metrics.damaged_words == 20
        assert metrics.damage_percentage == 20.0
    
    def test_quality_classification_short_text_good(self):
        # Short text (<50 words) with 15% damage - should be GOOD
        metrics = QualityMetrics(
            total_words=40,
            clean_words=34,
            damaged_words=6,
            damage_percentage=15.0
        )
        assert metrics.quality_classification == "GOOD_QUALITY"
    
    def test_quality_classification_short_text_poor(self):
        # Short text with 25% damage - should be POOR (threshold 20%)
        metrics = QualityMetrics(
            total_words=40,
            clean_words=30,
            damaged_words=10,
            damage_percentage=25.0
        )
        assert metrics.quality_classification == "POOR_QUALITY"
    
    def test_quality_classification_medium_text_good(self):
        # Medium text (50-200 words) with 25% damage - should be GOOD (threshold 30%)
        metrics = QualityMetrics(
            total_words=100,
            clean_words=75,
            damaged_words=25,
            damage_percentage=25.0
        )
        assert metrics.quality_classification == "GOOD_QUALITY"
    
    def test_quality_classification_medium_text_poor(self):
        # Medium text with 35% damage - should be POOR
        metrics = QualityMetrics(
            total_words=100,
            clean_words=65,
            damaged_words=35,
            damage_percentage=35.0
        )
        assert metrics.quality_classification == "POOR_QUALITY"
    
    def test_quality_classification_long_text_good(self):
        # Long text (200+ words) with 35% damage - should be GOOD (threshold 40%)
        metrics = QualityMetrics(
            total_words=250,
            clean_words=162,
            damaged_words=88,
            damage_percentage=35.2
        )
        assert metrics.quality_classification == "GOOD_QUALITY"
    
    def test_quality_classification_long_text_poor(self):
        # Long text with 45% damage - should be POOR
        metrics = QualityMetrics(
            total_words=250,
            clean_words=137,
            damaged_words=113,
            damage_percentage=45.2
        )
        assert metrics.quality_classification == "POOR_QUALITY"


class TestAkkadianText:
    """Tests for AkkadianText model."""
    
    def test_create_minimal_akkadian_text(self):
        text = AkkadianText(
            project="rinap-rinap1",
            textid="Q003414",
            transliterated_text="ana {d}aš-šur EN GAL-e EN-ia",
            normalized_text="ana Aššur bēl rabê bēlīya"
        )
        assert text.project == "rinap-rinap1"
        assert text.textid == "Q003414"
        assert text.id == "rinap-rinap1:Q003414"
    
    def test_create_full_akkadian_text(self):
        quality_metrics = QualityMetrics(
            total_words=50,
            clean_words=45,
            damaged_words=5,
            damage_percentage=10.0
        )
        
        lang_stats = LanguageStats(
            akkadian_pct=90.0,
            sumerian_pct=8.0,
            other_pct=2.0,
            total_words=100
        )
        
        text = AkkadianText(
            project="rinap-rinap1",
            textid="Q003414",
            transliterated_text="ana {d}aš-šur",
            normalized_text="ana Aššur",
            lemmatized_text="ana[to]PRP Aššur[1]DN",
            translation="To Aššur",
            city="Nineveh",
            writing_start_year=-700,
            writing_end_year=-681,
            genre="Historical",
            quality_metrics=quality_metrics,
            language_stats=lang_stats
        )
        
        assert text.city == "Nineveh"
        assert text.genre == "Historical"
        assert text.quality_metrics.quality_classification == "GOOD_QUALITY"
        assert text.language_stats.is_primarily_akkadian() is True
    
    def test_id_property(self):
        text = AkkadianText(
            project="rinap-rinap2",
            textid="Q003500",
            transliterated_text="test",
            normalized_text="test"
        )
        assert text.id == "rinap-rinap2:Q003500"
    
    def test_str_representation(self):
        text = AkkadianText(
            project="rinap-rinap1",
            textid="Q003414",
            transliterated_text="test",
            normalized_text="test",
            city="Nineveh",
            genre="Historical"
        )
        str_repr = str(text)
        assert "rinap-rinap1:Q003414" in str_repr
        assert "Nineveh" in str_repr
        assert "Historical" in str_repr
