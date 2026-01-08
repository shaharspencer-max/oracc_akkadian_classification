"""Unit tests for PleiadesRepository."""

import pytest
import pandas as pd
from pathlib import Path
from akkadian_classification.repositories.pleiades_repository import (
    PleiadesRepository,
    PleiadesLocation
)


class TestPleiadesRepository:
    """Tests for PleiadesRepository."""
    
    @pytest.fixture
    def mock_pleiades_csv(self, tmp_path):
        """Create a temporary Pleiades CSV file for tests."""
        csv_path = tmp_path / "pleiades_test.csv"
        
        # Create test data
        data = {
            'city_name': ['Nineveh', 'Babylon', 'Assur', 'InvalidCity', 'NoCoords'],
            'plaides_id': ['874621', '893951', '893945', '?', '123456'],
            'lat': [36.3667, 32.5355, 35.4583, 36.0, None],
            'lon': [43.1525, 44.4275, 43.2603, 43.0, None]
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        
        return str(csv_path)
    
    @pytest.fixture
    def repository(self, mock_pleiades_csv):
        return PleiadesRepository(mock_pleiades_csv)
    
    def test_init(self, mock_pleiades_csv):
        repo = PleiadesRepository(mock_pleiades_csv)
        assert repo.csv_path == mock_pleiades_csv
        assert repo._df is None  # Lazy loading
        assert repo._city_to_location is None
    
    def test_lazy_loading(self, repository):
        # Data should not be loaded initially
        assert repository._df is None
        
        # First access triggers loading
        repository.get_location("Nineveh")
        assert repository._df is not None
        assert repository._city_to_location is not None
    
    def test_get_location_valid_city(self, repository):
        location = repository.get_location("Nineveh")
        
        assert location is not None
        assert isinstance(location, PleiadesLocation)
        assert location.city_name == "Nineveh"
        assert location.pleiades_id == "874621"
        assert location.latitude == 36.3667
        assert location.longitude == 43.1525
    
    def test_get_location_invalid_pleiades_id(self, repository):
        # City with '?' as pleiades_id should not be included
        location = repository.get_location("InvalidCity")
        assert location is None
    
    def test_get_location_missing_coords(self, repository):
        # City with missing coordinates should not be included
        location = repository.get_location("NoCoords")
        assert location is None
    
    def test_get_location_nonexistent_city(self, repository):
        location = repository.get_location("NonexistentCity")
        assert location is None
    
    def test_get_location_case_sensitive(self, repository):
        # Test that city names are matched exactly
        location = repository.get_location("nineveh")  # lowercase
        assert location is None  # Should not match "Nineveh"
    
    def test_get_location_strips_whitespace(self, repository):
        # Test that whitespace is stripped
        location = repository.get_location("  Nineveh  ")
        assert location is not None
        assert location.city_name == "Nineveh"
    
    def test_has_valid_pleiades_id_valid(self, repository):
        assert repository.has_valid_pleiades_id("Nineveh") is True
        assert repository.has_valid_pleiades_id("Babylon") is True
    
    def test_has_valid_pleiades_id_invalid(self, repository):
        assert repository.has_valid_pleiades_id("InvalidCity") is False
        assert repository.has_valid_pleiades_id("NoCoords") is False
        assert repository.has_valid_pleiades_id("NonexistentCity") is False
    
    def test_get_valid_cities(self, repository):
        valid_cities = repository.get_valid_cities()
        
        assert isinstance(valid_cities, set)
        assert len(valid_cities) == 3  # Nineveh, Babylon, Assur
        assert "Nineveh" in valid_cities
        assert "Babylon" in valid_cities
        assert "Assur" in valid_cities
        assert "InvalidCity" not in valid_cities
        assert "NoCoords" not in valid_cities
    
    def test_get_pleiades_url_valid_city(self, repository):
        url = repository.get_pleiades_url("Nineveh")
        assert url == "https://pleiades.stoa.org/places/874621"
    
    def test_get_pleiades_url_invalid_city(self, repository):
        url = repository.get_pleiades_url("InvalidCity")
        assert url is None
    
    def test_get_pleiades_url_nonexistent_city(self, repository):
        url = repository.get_pleiades_url("NonexistentCity")
        assert url is None
    
    def test_get_dataframe(self, repository):
        df = repository.get_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5  # All rows from test CSV
        assert 'city_name' in df.columns
        assert 'plaides_id' in df.columns
        assert 'lat' in df.columns
        assert 'lon' in df.columns
    
    def test_get_dataframe_returns_copy(self, repository):
        # Ensure we get a copy, not the original
        df1 = repository.get_dataframe()
        df2 = repository.get_dataframe()
        
        assert df1 is not df2  # Different objects
        assert df1.equals(df2)  # But same data
    
    def test_multiple_valid_cities(self, repository):
        # Test multiple cities in one session
        nineveh = repository.get_location("Nineveh")
        babylon = repository.get_location("Babylon")
        assur = repository.get_location("Assur")
        
        assert nineveh.city_name == "Nineveh"
        assert babylon.city_name == "Babylon"
        assert assur.city_name == "Assur"
        
        assert nineveh.pleiades_id == "874621"
        assert babylon.pleiades_id == "893951"
        assert assur.pleiades_id == "893945"


class TestPleiadesLocation:
    """Tests for PleiadesLocation dataclass."""
    
    def test_create_location(self):
        location = PleiadesLocation(
            city_name="Nineveh",
            pleiades_id="874621",
            latitude=36.3667,
            longitude=43.1525
        )
        
        assert location.city_name == "Nineveh"
        assert location.pleiades_id == "874621"
        assert location.latitude == 36.3667
        assert location.longitude == 43.1525
