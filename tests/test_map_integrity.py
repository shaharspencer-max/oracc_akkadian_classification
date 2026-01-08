
import unittest
import sys
import os

# Add project root to path to verify local package
PROJECT_ROOT = r"C:\Users\shaha\PycharmProjects\thesis\oracc_akkadian_classification"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from akkadian_classification import data_loader, config

class TestMapIntegrity(unittest.TestCase):
    """
    Verifies the integrity of the Akkadian Classification Map Data.
    Target: 106 Cities, Specific Region Reassignments, Exclusion of Missing Data.
    """
    
    @classmethod
    def setUpClass(cls):
        print("\n[TestMapIntegrity] Loading Data...")
        cls.df = data_loader.load_city_data()
        
    def test_01_total_city_count(self):
        """Verify strict city count of 106."""
        count = len(self.df)
        self.assertEqual(count, 106, f"Expected 106 cities, found {count}")
        
    def test_02_larak_configuration(self):
        """Verify Larak is in Babylonia (South) with corrected coordinates."""
        city_row = self.df[self.df['city'] == 'Larak']
        self.assertFalse(city_row.empty, "Larak should be present")
        
        row = city_row.iloc[0]
        self.assertEqual(row['region'], 'Babylonia (South)', "Larak should be in Babylonia (South)")
        self.assertAlmostEqual(row['lat'], 32.31275, places=4, msg="Larak Latitude Mismatch")
        self.assertAlmostEqual(row['lon'], 45.661, places=3, msg="Larak Longitude Mismatch")
        
    def test_03_tell_baradan_configuration(self):
        """Verify Tell Baradan is in Eastern Mesopotamia."""
        city_row = self.df[self.df['city'] == 'Tell Baradan']
        self.assertFalse(city_row.empty, "Tell Baradan should be present")
        self.assertEqual(city_row.iloc[0]['region'], 'Eastern Mesopotamia')

    def test_04_excluded_cities(self):
        """Verify cities with missing/invalid IDs are excluded."""
        # consistently excluded cities from the 117-list
        excluded = ['Allabria', 'Arzuhina', 'Barhalza', 'Bit-Zamani', 
                    'Eshnunna', 'Habruri', 'Kar-Sharrukin', 'Kisheshim', 
                    'Mannea', 'Parsua', 'Qunbuna']
        
        found = []
        for city in excluded:
            if not self.df[self.df['city'] == city].empty:
                found.append(city)
        
        self.assertEqual(len(found), 0, f"The following cities should be excluded but were found: {found}")

    def test_05_region_colors(self):
        """Verify all used regions have a defined color."""
        used_regions = self.df['region'].unique()
        defined_regions = config.COLOR_MAP.keys()
        
        for region in used_regions:
            self.assertIn(region, defined_regions, f"Region '{region}' has no color definition")

if __name__ == '__main__':
    unittest.main()
