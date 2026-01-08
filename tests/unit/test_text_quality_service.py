"""Unit tests for TextQualityService."""

import pytest
from akkadian_classification.services.text_quality_service import TextQualityService
from akkadian_classification.models.text import QualityMetrics


class TestTextQualityService:
    """Tests for TextQualityService."""
    
    @pytest.fixture
    def service(self):
        return TextQualityService()
    
    def test_analyze_clean_text(self, service):
        text = "ana Aššur bēl rabê bēlīya"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.clean_words == 5
        assert metrics.damaged_words == 0
        assert metrics.damage_percentage == 0.0
    
    def test_analyze_text_with_unk(self, service):
        text = "ana UNK bēl rabê UNK"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.clean_words == 3
        assert metrics.damaged_words == 2
        assert metrics.damage_percentage == 40.0
    
    def test_analyze_text_with_brackets(self, service):
        text = "ana [Aššur] bēl rabê bēlīya"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.damaged_words == 1  # [Aššur] is damaged
        assert metrics.clean_words == 4
    
    def test_analyze_text_with_x(self, service):
        text = "ana x x bēl rabê"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.damaged_words == 2
        assert metrics.clean_words == 3
        assert metrics.damage_percentage == 40.0
    
    def test_analyze_text_with_ellipsis(self, service):
        text = "ana Aššur ... bēl rabê"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.damaged_words == 1  # ... is damaged
        assert metrics.clean_words == 4
    
    def test_analyze_text_with_half_brackets(self, service):
        text = "ana ⸢Aššur⸣ bēl rabê"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 4
        assert metrics.damaged_words == 1  # ⸢Aššur⸣ is damaged
        assert metrics.clean_words == 3
    
    def test_analyze_text_with_punctuation(self, service):
        # UNK. should be detected even with punctuation
        text = "ana UNK. bēl rabê bēlīya"
        metrics = service.analyze_text(text)
        
        assert metrics.total_words == 5
        assert metrics.damaged_words == 1
    
    def test_analyze_empty_text(self, service):
        metrics = service.analyze_text("")
        
        assert metrics.total_words == 0
        assert metrics.clean_words == 0
        assert metrics.damage_percentage == 100.0
    
    def test_analyze_nan_text(self, service):
        import pandas as pd
        metrics = service.analyze_text(pd.NA)
        
        assert metrics.total_words == 0
        assert metrics.damage_percentage == 100.0
    
    def test_classify_quality_short_good(self, service):
        # Short text with 15% damage
        text = "word1 word2 word3 word4 UNK word6 word7 word8 word9 word10"
        quality = service.classify_quality(text)
        
        metrics = service.analyze_text(text)
        assert metrics.total_words == 10
        assert metrics.damage_percentage == 10.0
        assert quality == "GOOD_QUALITY"
    
    def test_classify_quality_short_poor(self, service):
        # Short text with 30% damage (above 20% threshold)
        text = "word1 UNK word3 UNK word5 UNK word7 word8 word9 word10"
        quality = service.classify_quality(text)
        
        assert quality == "POOR_QUALITY"
    
    def test_classify_quality_medium_good(self, service):
        # Medium text (100 words) with 25% damage
        words = ["word"] * 75 + ["UNK"] * 25
        text = " ".join(words)
        quality = service.classify_quality(text)
        
        assert quality == "GOOD_QUALITY"  # 25% < 30% threshold
    
    def test_classify_quality_medium_poor(self, service):
        # Medium text with 35% damage
        words = ["word"] * 65 + ["UNK"] * 35
        text = " ".join(words)
        quality = service.classify_quality(text)
        
        assert quality == "POOR_QUALITY"  # 35% > 30% threshold
    
    def test_classify_quality_long_good(self, service):
        # Long text (250 words) with 35% damage
        words = ["word"] * 162 + ["UNK"] * 88
        text = " ".join(words)
        quality = service.classify_quality(text)
        
        metrics = service.analyze_text(text)
        assert metrics.total_words == 250
        assert quality == "GOOD_QUALITY"  # 35.2% < 40% threshold
    
    def test_classify_quality_long_poor(self, service):
        # Long text with 45% damage
        words = ["word"] * 137 + ["UNK"] * 113
        text = " ".join(words)
        quality = service.classify_quality(text)
        
        assert quality == "POOR_QUALITY"  # 45.2% > 40% threshold
    
    def test_classify_from_metrics(self, service):
        # Create metrics directly
        good_metrics = QualityMetrics(
            total_words=100,
            clean_words=75,
            damaged_words=25,
            damage_percentage=25.0
        )
        
        poor_metrics = QualityMetrics(
            total_words=100,
            clean_words=65,
            damaged_words=35,
            damage_percentage=35.0
        )
        
        assert service.classify_from_metrics(good_metrics) == "GOOD_QUALITY"
        assert service.classify_from_metrics(poor_metrics) == "POOR_QUALITY"
    
    def test_all_damage_markers(self, service):
        # Test that all damage markers are detected
        test_cases = [
            ("word UNK word", 1),
            ("word x word", 1),
            ("word [damaged] word", 1),
            ("word ] word", 1),
            ("word ... word", 1),
            ("word ⸢half⸣ word", 1),
            ("word ⸢damaged word", 1),
            ("word damaged⸣ word", 1),
        ]
        
        for text, expected_damaged in test_cases:
            metrics = service.analyze_text(text)
            assert metrics.damaged_words == expected_damaged, f"Failed for: {text}"
