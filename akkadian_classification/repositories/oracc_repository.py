"""Repository for accessing ORACC corpus data."""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

from akkadian_classification.models.text import AkkadianText, LanguageStats


class ORACCRepository:
    """Repository for reading ORACC JSON files and extracting text data."""
    
    def __init__(self, parsed_results_dir: str):
        """Initialize repository with path to parsed results directory.
        
        Args:
            parsed_results_dir: Path to directory containing parsed ORACC JSONs
                                Structure: {parsed_results_dir}/{project}/{textid}.json
        """
        self.parsed_results_dir = Path(parsed_results_dir)
    
    def _find_json_path(self, project: str, textid: str) -> Optional[Path]:
        """Find JSON file using both naming conventions.
        
        Tries:
        1. {project}/{textid}.json
        2. {project}/{project}_{textid}.json
        
        Args:
            project: Project name (e.g., 'rinap-rinap1')
            textid: Text ID (e.g., 'Q003414')
        
        Returns:
            Path to JSON file if found, None otherwise
        """
        # Try standard naming
        json_path = self.parsed_results_dir / project / f"{textid}.json"
        if json_path.exists():
            return json_path
        
        # Try alternative naming with project prefix
        json_path = self.parsed_results_dir / project / f"{project}_{textid}.json"
        if json_path.exists():
            return json_path
        
        return None
    
    def load_json(self, project: str, textid: str) -> Optional[Dict[str, Any]]:
        """Load raw JSON data for a text.
        
        Args:
            project: Project name
            textid: Text ID
        
        Returns:
            Parsed JSON dict or None if file not found
        """
        json_path = self._find_json_path(project, textid)
        if not json_path:
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
    
    def get_word_language_stats(self, project: str, textid: str) -> Optional[LanguageStats]:
        """Analyze word-level language tags from JSON, excluding UNK/damaged words.
        
        Counts words by language family:
        - Akkadian: lang starts with 'akk' (akk, akk-x-neoass, etc.)
        - Sumerian: lang starts with 'sux' (sux, sux-x-emesal, etc.)
        - Other: everything else
        
        Excludes:
        - Words with 'UNK' in form
        - Words with form 'x'
        - Words with '[' in form (damaged)
        
        Args:
            project: Project name
            textid: Text ID
        
        Returns:
            LanguageStats object or None if file not found or no valid words
        """
        data = self.load_json(project, textid)
        if not data:
            return None
        
        words = data.get('content', {}).get('words', [])
        if not words:
            return None
        
        akkadian_count = 0
        sumerian_count = 0
        other_count = 0
        
        for word in words:
            # Skip UNK and damaged words
            form = word.get('form', '')
            if 'UNK' in form.upper() or form.lower() == 'x' or '[' in form:
                continue
            
            lang = word.get('lang', '')
            if lang.startswith('akk'):  # akk, akk-x-neoass, etc.
                akkadian_count += 1
            elif lang.startswith('sux'):  # sux, sux-x-emesal, etc.
                sumerian_count += 1
            else:
                other_count += 1
        
        total = akkadian_count + sumerian_count + other_count
        if total == 0:
            return None
        
        return LanguageStats(
            akkadian_pct=akkadian_count / total * 100,
            sumerian_pct=sumerian_count / total * 100,
            other_pct=other_count / total * 100,
            total_words=total
        )
    
    def is_primarily_akkadian(
        self, 
        project: str, 
        textid: str, 
        min_akkadian_pct: float = 70.0
    ) -> tuple[bool, Optional[LanguageStats]]:
        """Check if a text is primarily Akkadian based on word-level analysis.
        
        Args:
            project: Project name
            textid: Text ID
            min_akkadian_pct: Minimum percentage of Akkadian words required (default 70%)
        
        Returns:
            tuple: (is_valid, stats or None)
                   Defaults to (True, None) if analysis fails (permissive)
        """
        stats = self.get_word_language_stats(project, textid)
        
        if stats is None:
            return True, None  # Default to include if can't analyze
        
        is_valid = stats.is_primarily_akkadian(min_akkadian_pct)
        return is_valid, stats
    
    def get_text(self, project: str, textid: str) -> Optional[AkkadianText]:
        """Load AkkadianText from ORACC JSON.
        
        Note: Only loads basic text representations and metadata.
        Quality metrics and language stats should be computed separately.
        
        Args:
            project: Project name
            textid: Text ID
        
        Returns:
            AkkadianText object or None if file not found
        """
        data = self.load_json(project, textid)
        if not data:
            return None
        
        # Extract text representations
        content = data.get('content', {})
        transliterated = content.get('transliterated_text', '')
        normalized = content.get('normalized text', '')
        lemmatized = content.get('lemmatized_text')
        translation = content.get('translation')
        
        # Extract metadata
        metadata = data.get('metadata', {}).get('metadata_raw_dict', {})
        
        return AkkadianText(
            project=project,
            textid=textid,
            transliterated_text=transliterated,
            normalized_text=normalized,
            lemmatized_text=lemmatized,
            translation=translation,
            city=metadata.get('provenance'),
            writing_start_year=metadata.get('period_o_from'),
            writing_end_year=metadata.get('period_o_to'),
            genre=metadata.get('genre')
        )
