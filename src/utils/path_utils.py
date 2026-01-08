import pandas as pd


def get_provenenances_to_plaides_data_mapping()->pd.DataFrame:
    csv_path_with_pleidaes_data = r"C:\Users\shaha\PycharmProjects\oracc_preprocessing\data\metadata_preprocessing\provenances_to_plaides_data_mapping.csv"
    provenance_to_plaides_coords_mapping = pd.read_csv(csv_path_with_pleidaes_data)
    return provenance_to_plaides_coords_mapping