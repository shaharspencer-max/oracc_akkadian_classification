"""Unit tests for ORACCRepository."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from akkadian_classification.repositories.oracc_repository import ORACCRepository
from akkadian_classification.models.text import LanguageStats


class TestORACCRepository:
    """Tests for ORACCRepository."""
    
    @pytest.fixture
    def mock_parsed_results_dir(self, tmp_path):
        """Create a temporary directory structure for tests."""
        return tmp_path / "parsed_results"
    
    @pytest.fixture
    def repository(self, mock_parsed_results_dir):
        return ORACCRepository(str(mock_parsed_results_dir))
    
    def test_init(self, mock_parsed_results_dir):
        repo = ORACCRepository(str(mock_parsed_results_dir))
        assert repo.parsed_results_dir == Path(mock_parsed_results_dir)
    
    def test_find_json_path_standard_naming(self, repository, mock_parsed_results_dir):
        # Create test file with standard naming
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        json_file.write_text("{}")
        
        path = repository._find_json_path("rinap-rinap1", "Q003414")
        assert path == json_file
    
    def test_find_json_path_alternative_naming(self, repository, mock_parsed_results_dir):
        # Create test file with project prefix naming
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "rinap-rinap1_Q003414.json"
        json_file.write_text("{}")
        
        path = repository._find_json_path("rinap-rinap1", "Q003414")
        assert path == json_file
    
    def test_find_json_path_not_found(self, repository):
        path = repository._find_json_path("nonexistent", "Q999999")
        assert path is None
    
    def test_load_json_success(self, repository, mock_parsed_results_dir):
        # Create test JSON
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "metadata": {"id_text": "Q003414"},
            "content": {"words": []}
        }
        json_file.write_text(json.dumps(test_data))
        
        data = repository.load_json("rinap-rinap1", "Q003414")
        assert data == test_data
    
    def test_load_json_not_found(self, repository):
        data = repository.load_json("nonexistent", "Q999999")
        assert data is None
    
    def test_get_word_language_stats_all_akkadian(self, repository, mock_parsed_results_dir):
        # Create test JSON with all Akkadian words
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "words": [
                    {"form": "ana", "lang": "akk"},
                    {"form": "šarri", "lang": "akk-x-neoass"},
                    {"form": "bēl", "lang": "akk"},
                    {"form": "rabê", "lang": "akk"},
                ]
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        stats = repository.get_word_language_stats("rinap-rinap1", "Q003414")
        
        assert stats is not None
        assert stats.akkadian_pct == 100.0
        assert stats.sumerian_pct == 0.0
        assert stats.other_pct == 0.0
        assert stats.total_words == 4
    
    def test_get_word_language_stats_mixed_languages(self, repository, mock_parsed_results_dir):
        # Create test JSON with mixed languages
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "words": [
                    {"form": "ana", "lang": "akk"},  # Akkadian
                    {"form": "lugal", "lang": "sux"},  # Sumerian
                    {"form": "bēl", "lang": "akk"},  # Akkadian
                    {"form": "e2", "lang": "sux-x-emesal"},  # Sumerian
                    {"form": "rabê", "lang": "akk"},  # Akkadian
                    {"form": "other", "lang": "qpc"},  # Other
                ]
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        stats = repository.get_word_language_stats("rinap-rinap1", "Q003414")
        
        assert stats is not None
        assert stats.akkadian_pct == 50.0  # 3/6
        assert stats.sumerian_pct == pytest.approx(33.33, rel=0.1)  # 2/6
        assert stats.other_pct == pytest.approx(16.67, rel=0.1)  # 1/6
        assert stats.total_words == 6
    
    def test_get_word_language_stats_excludes_damaged(self, repository, mock_parsed_results_dir):
        # Create test JSON with damaged words
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "words": [
                    {"form": "ana", "lang": "akk"},
                    {"form": "UNK", "lang": "akk"},  # Should be excluded
                    {"form": "x", "lang": "akk"},  # Should be excluded
                    {"form": "[damaged]", "lang": "akk"},  # Should be excluded
                    {"form": "bēl", "lang": "akk"},
                ]
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        stats = repository.get_word_language_stats("rinap-rinap1", "Q003414")
        
        assert stats is not None
        assert stats.total_words == 2  # Only 'ana' and 'bēl' counted
        assert stats.akkadian_pct == 100.0
    
    def test_get_word_language_stats_no_words(self, repository, mock_parsed_results_dir):
        # Create test JSON with no words
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {"content": {"words": []}}
        json_file.write_text(json.dumps(test_data))
        
        stats = repository.get_word_language_stats("rinap-rinap1", "Q003414")
        assert stats is None
    
    def test_is_primarily_akkadian_above_threshold(self, repository, mock_parsed_results_dir):
        # Create test JSON with 80% Akkadian
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "words": [
                    {"form": "word1", "lang": "akk"},
                    {"form": "word2", "lang": "akk"},
                    {"form": "word3", "lang": "akk"},
                    {"form": "word4", "lang": "akk"},
                    {"form": "word5", "lang": "sux"},
                ]
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        is_valid, stats = repository.is_primarily_akkadian("rinap-rinap1", "Q003414")
        
        assert is_valid is True
        assert stats.akkadian_pct == 80.0
    
    def test_is_primarily_akkadian_below_threshold(self, repository, mock_parsed_results_dir):
        # Create test JSON with 60% Akkadian (below 70% threshold)
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "words": [
                    {"form": "word1", "lang": "akk"},
                    {"form": "word2", "lang": "akk"},
                    {"form": "word3", "lang": "akk"},
                    {"form": "word4", "lang": "sux"},
                    {"form": "word5", "lang": "sux"},
                ]
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        is_valid, stats = repository.is_primarily_akkadian("rinap-rinap1", "Q003414")
        
        assert is_valid is False
        assert stats.akkadian_pct == 60.0
    
    def test_is_primarily_akkadian_file_not_found(self, repository):
        # Should default to True if file not found (permissive)
        is_valid, stats = repository.is_primarily_akkadian("nonexistent", "Q999999")
        
        assert is_valid is True
        assert stats is None
    
    def test_get_text_success(self, repository, mock_parsed_results_dir):
        # Create test JSON with full text data
        project_dir = mock_parsed_results_dir / "rinap-rinap1"
        project_dir.mkdir(parents=True)
        json_file = project_dir / "Q003414.json"
        
        test_data = {
            "content": {
                "transliterated_text": "ana {d}aš-šur",
                "normalized text": "ana Aššur",
                "lemmatized_text": "ana[to]PRP Aššur[1]DN",
                "translation": "To Aššur"
            },
            "metadata": {
                "id_text": "Q003414",
                "metadata_raw_dict": {
                    "provenance": "Nineveh",
                    "period_o_from": -700,
                    "period_o_to": -681,
                    "genre": "Historical"
                }
            }
        }
        json_file.write_text(json.dumps(test_data))
        
        text = repository.get_text("rinap-rinap1", "Q003414")
        
        assert text is not None
        assert text.project == "rinap-rinap1"
        assert text.textid == "Q003414"
        assert text.transliterated_text == "ana {d}aš-šur"
        assert text.normalized_text == "ana Aššur"
        assert text.city == "Nineveh"
        assert text.writing_start_year == -700
        assert text.genre == "Historical"
    
    def test_get_text_not_found(self, repository):
        text = repository.get_text("nonexistent", "Q999999")
        assert text is None
