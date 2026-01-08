
from akkadian_classification import data_loader, map_builder
import os

OUTPUT_FILE = "region_map_generated.html"

def main():
    print("Running Akkadian Classification Map Generator...")
    df = data_loader.load_city_data()
    m = map_builder.build_map(df, OUTPUT_FILE)
    print(f"Map generated successfully: {os.path.abspath(OUTPUT_FILE)}")
    print("To publish, copy this file to 'docs/index.html'.")

if __name__ == "__main__":
    main()
