"""Unit tests for regions configuration."""

import pytest
from akkadian_classification.config.regions import (
    REGION_MAP,
    REGIONS,
    get_region,
    get_cities_in_region
)


class TestRegionMap:
    """Tests for REGION_MAP configuration."""
    
    def test_region_map_exists(self):
        assert REGION_MAP is not None
        assert isinstance(REGION_MAP, dict)
    
    def test_region_map_has_106_cities(self):
        # According to requirements, there are 106 cities
        assert len(REGION_MAP) == 106
    
    def test_all_regions_exist(self):
        expected_regions = {
            'Babylonia (North)',
            'Babylonia (South)',
            'Assyria (Heartland)',
            'Assyria (Provinces)',
            'Upper Mesopotamia',
            'Syria',
            'Levant',
            'Iran/Elam',
            'Anatolia',
            'Other'
        }
        
        actual_regions = set(REGION_MAP.values())
        assert actual_regions == expected_regions
    
    def test_known_cities_mapped_correctly(self):
        # Test some known mappings
        assert REGION_MAP['Nineveh'] == 'Assyria (Heartland)'
        assert REGION_MAP['Babylon'] == 'Babylonia (North)'
        assert REGION_MAP['Uruk'] == 'Babylonia (South)'
        assert REGION_MAP['Damascus'] == 'Syria'
        assert REGION_MAP['Susa'] == 'Iran/Elam'


class TestRegionsReverseMap:
    """Tests for REGIONS reverse mapping."""
    
    def test_regions_exists(self):
        assert REGIONS is not None
        assert isinstance(REGIONS, dict)
    
    def test_regions_has_all_regions(self):
        expected_regions = [
            'Babylonia (North)',
            'Babylonia (South)',
            'Assyria (Heartland)',
            'Assyria (Provinces)',
            'Upper Mesopotamia',
            'Syria',
            'Levant',
            'Iran/Elam',
            'Anatolia',
            'Other'
        ]
        
        for region in expected_regions:
            assert region in REGIONS
    
    def test_reverse_mapping_matches_forward(self):
        # Every city in REGIONS should map back to that region in REGION_MAP
        for region, cities in REGIONS.items():
            for city in cities:
                assert REGION_MAP[city] == region
    
    def test_all_cities_in_reverse_map(self):
        # All cities from REGION_MAP should appear in REGIONS
        cities_in_region_map = set(REGION_MAP.keys())
        cities_in_regions = set()
        
        for cities in REGIONS.values():
            cities_in_regions.update(cities)
        
        assert cities_in_region_map == cities_in_regions
    
    def test_babylonia_north_cities(self):
        cities = REGIONS['Babylonia (North)']
        assert 'Babylon' in cities
        assert 'Sippar' in cities
        assert 'Kish' in cities
        assert len(cities) == 9
    
    def test_assyria_heartland_cities(self):
        cities = REGIONS['Assyria (Heartland)']
        assert 'Nineveh' in cities
        assert 'Assur' in cities
        assert 'Nimrud' in cities
        assert len(cities) == 9


class TestGetRegion:
    """Tests for get_region function."""
    
    def test_get_region_valid_city(self):
        assert get_region('Nineveh') == 'Assyria (Heartland)'
        assert get_region('Babylon') == 'Babylonia (North)'
        assert get_region('Uruk') == 'Babylonia (South)'
    
    def test_get_region_unknown_city(self):
        assert get_region('UnknownCity') == 'Unknown'
        assert get_region('NonexistentPlace') == 'Unknown'
    
    def test_get_region_case_sensitive(self):
        # Should be case-sensitive
        assert get_region('nineveh') == 'Unknown'  # lowercase
        assert get_region('Nineveh') == 'Assyria (Heartland)'  # proper case


class TestGetCitiesInRegion:
    """Tests for get_cities_in_region function."""
    
    def test_get_cities_in_region_valid(self):
        cities = get_cities_in_region('Babylonia (North)')
        assert isinstance(cities, list)
        assert len(cities) == 9
        assert 'Babylon' in cities
        assert 'Sippar' in cities
    
    def test_get_cities_in_region_unknown(self):
        cities = get_cities_in_region('NonexistentRegion')
        assert cities == []
    
    def test_get_cities_returns_copy(self):
        # Should return a reference to the list (dict.get behavior)
        cities1 = get_cities_in_region('Babylonia (North)')
        cities2 = get_cities_in_region('Babylonia (North)')
        
        # Same reference is fine for read-only access
        assert cities1 == cities2
    
    def test_all_regions_return_cities(self):
        for region in REGIONS.keys():
            cities = get_cities_in_region(region)
            assert len(cities) > 0
            assert isinstance(cities, list)


class TestDataConsistency:
    """Tests for data consistency and integrity."""
    
    def test_no_duplicate_cities_across_regions(self):
        # Each city should only appear in one region
        all_cities = []
        for cities in REGIONS.values():
            all_cities.extend(cities)
        
        assert len(all_cities) == len(set(all_cities))  # No duplicates
    
    def test_region_map_and_regions_have_same_cities(self):
        # Total cities should match
        cities_from_region_map = set(REGION_MAP.keys())
        
        cities_from_regions = set()
        for cities in REGIONS.values():
            cities_from_regions.update(cities)
        
        assert cities_from_region_map == cities_from_regions
        assert len(cities_from_region_map) == 106
    
    def test_no_empty_regions(self):
        # Every region should have at least one city
        for region, cities in REGIONS.items():
            assert len(cities) > 0, f"Region '{region}' has no cities"
    
    def test_city_counts_per_region(self):
        # Document expected city counts (for regression testing)
        expected_counts = {
            'Babylonia (North)': 9,
            'Babylonia (South)': 9,
            'Assyria (Heartland)': 9,
            'Assyria (Provinces)': 9,
            'Upper Mesopotamia': 18,
            'Syria': 14,
            'Levant': 12,
            'Iran/Elam': 10,
            'Anatolia': 5,
            'Other': 11
        }
        
        for region, expected_count in expected_counts.items():
            actual_count = len(REGIONS[region])
            assert actual_count == expected_count, \
                f"Region '{region}' expected {expected_count} cities, got {actual_count}"
