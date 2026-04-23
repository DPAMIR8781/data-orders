import pandas as pd
from pathlib import Path


class Olist:

    def __init__(self):
        self.path = Path(__file__).resolve().parents[1] / "data"

    def get_data(self):

        data = {}

        data["orders"] = pd.read_csv(self.path / "orders.csv")
        data["order_items"] = pd.read_csv(self.path / "order_items.csv")
        data["order_reviews"] = pd.read_csv(self.path / "order_reviews.csv")
        data["products"] = pd.read_csv(self.path / "products.csv")
        data["sellers"] = pd.read_csv(self.path / "sellers.csv")
        data["customers"] = pd.read_csv(self.path / "customers.csv")
        data["geolocation"] = pd.read_csv(self.path / "geolocation.csv")

        return data
