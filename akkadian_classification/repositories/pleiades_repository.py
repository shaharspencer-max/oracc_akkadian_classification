"""Repository for accessing Pleiades Gazetteer geographic data."""

import pandas as pd
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class PleiadesLocation:
    """Geographic location from Pleiades Gazetteer."""
    city_name: str
    pleiades_id: str
    latitude: float
    longitude: float


class PleiadesRepository:
    """Repository for Pleiades geographic coordinate data."""
    
    def __init__(self, pleiades_csv_path: str):
        """Initialize repository with path to Pleiades mapping CSV.
        
        Args:
            pleiades_csv_path: Path to provenances_to_plaides_data_mapping.csv
        """
        self.csv_path = pleiades_csv_path
        self._df: Optional[pd.DataFrame] = None
        self._city_to_location: Optional[Dict[str, PleiadesLocation]] = None
    
    def _load_data(self):
        """Lazy load and cache the CSV data."""
        if self._df is None:
            self._df = pd.read_csv(self.csv_path).fillna('')
            self._build_city_index()
    
    def _build_city_index(self):
        """Build city name -> PleiadesLocation index for fast lookups."""
        self._city_to_location = {}
        
        for _, row in self._df.iterrows():
            city = row.get('city_name', '').strip()
            pid = str(row.get('plaides_id', '')).strip()  # Note: typo in CSV column name
            lat = row.get('lat')
            lon = row.get('lon')
            
            # Only include valid entries
            # Check that lat and lon are valid numbers (not empty strings or NaN)
            try:
                if city and pid and pid not in ['?', '-', ''] and pd.notna(lat) and pd.notna(lon):
                    lat_float = float(lat)
                    lon_float = float(lon)
                    self._city_to_location[city] = PleiadesLocation(
                        city_name=city,
                        pleiades_id=pid,
                        latitude=lat_float,
                        longitude=lon_float
                    )
            except (ValueError, TypeError):
                # Skip entries with invalid coordinates
                pass
    
    def get_location(self, city: str) -> Optional[PleiadesLocation]:
        """Get geographic location for a city.
        
        Args:
            city: City name
        
        Returns:
            PleiadesLocation if found and valid, None otherwise
        """
        self._load_data()
        return self._city_to_location.get(city.strip())
    
    def has_valid_pleiades_id(self, city: str) -> bool:
        """Check if a city has a valid Pleiades ID.
        
        Args:
            city: City name
        
        Returns:
            True if city has valid Pleiades ID and coordinates
        """
        return self.get_location(city) is not None
    
    def get_valid_cities(self) -> set[str]:
        """Get set of all cities with valid Pleiades IDs.
        
        Returns:
            Set of city names with valid Pleiades data
        """
        self._load_data()
        return set(self._city_to_location.keys())
    
    def get_pleiades_url(self, city: str) -> Optional[str]:
        """Get Pleiades Gazetteer URL for a city.
        
        Args:
            city: City name
        
        Returns:
            URL string or None if city not found
        """
        location = self.get_location(city)
        if location and location.pleiades_id.isdigit():
            return f"https://pleiades.stoa.org/places/{location.pleiades_id}"
        return None
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the full Pleiades mapping dataframe.
        
        Returns:
            DataFrame with all Pleiades data
        """
        self._load_data()
        return self._df.copy()
