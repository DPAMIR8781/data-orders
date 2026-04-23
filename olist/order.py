import numpy as np
import pandas as pd

from olist.data import Olist


class Order:
    def __init__(self):
        self.data = Olist().get_data()

    def get_wait_time(self):
        orders = self.data["orders"].copy()

        orders = orders[orders["order_status"] == "delivered"].copy()

        orders["order_purchase_timestamp"] = pd.to_datetime(
            orders["order_purchase_timestamp"]
        )
        orders["order_delivered_customer_date"] = pd.to_datetime(
            orders["order_delivered_customer_date"]
        )
        orders["order_estimated_delivery_date"] = pd.to_datetime(
            orders["order_estimated_delivery_date"]
        )

        orders["wait_time"] = (
            orders["order_delivered_customer_date"]
            - orders["order_purchase_timestamp"]
        ).dt.days

        orders["expected_wait_time"] = (
            orders["order_estimated_delivery_date"]
            - orders["order_purchase_timestamp"]
        ).dt.days

        orders["delay_vs_expected"] = (
            orders["order_delivered_customer_date"]
            - orders["order_estimated_delivery_date"]
        ).dt.days

        orders["delay_vs_expected"] = orders["delay_vs_expected"].apply(
            lambda x: x if x > 0 else 0
        )

        return orders[
            [
                "order_id",
                "wait_time",
                "expected_wait_time",
                "delay_vs_expected",
                "order_status",
            ]
        ]

    def get_review_score(self):
        reviews = self.data["order_reviews"].copy()

        reviews = reviews[["order_id", "review_score"]].copy()
        reviews["dim_is_five_star"] = (reviews["review_score"] == 5).astype(int)
        reviews["dim_is_one_star"] = (reviews["review_score"] == 1).astype(int)

        return reviews

    def get_number_items(self):
        order_items = self.data["order_items"].copy()

        number_items = (
            order_items.groupby("order_id", as_index=False)
            .agg(number_of_items=("order_item_id", "count"))
        )

        return number_items

    def get_number_sellers(self):
        order_items = self.data["order_items"].copy()

        number_sellers = (
            order_items.groupby("order_id", as_index=False)
            .agg(number_of_sellers=("seller_id", "nunique"))
        )

        return number_sellers

    def get_price(self):
        order_items = self.data["order_items"].copy()

        price = (
            order_items.groupby("order_id", as_index=False)
            .agg(
                price=("price", "sum"),
                freight_value=("freight_value", "sum"),
            )
        )

        return price

    def get_training_data(self):
        training = (
            self.get_wait_time()
            .merge(self.get_review_score(), on="order_id", how="left")
            .merge(self.get_number_items(), on="order_id", how="left")
            .merge(self.get_number_sellers(), on="order_id", how="left")
            .merge(self.get_price(), on="order_id", how="left")
        )

        training = training.dropna().reset_index(drop=True)

        return training

    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        r = 6371.0

        lat1, lon1, lat2, lon2 = map(
            np.radians, [lat1, lon1, lat2, lon2]
        )

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        )
        c = 2 * np.arcsin(np.sqrt(a))

        return r * c

    def get_distance_seller_customer(self):
        orders = self.data["orders"].copy()
        order_items = self.data["order_items"].copy()
        customers = self.data["customers"].copy()
        sellers = self.data["sellers"].copy()
        geolocation = self.data["geolocation"].copy()

        orders = orders[["order_id", "customer_id"]]
        customers = customers[["customer_id", "customer_zip_code_prefix"]]
        sellers = sellers[["seller_id", "seller_zip_code_prefix"]]

        geo = (
            geolocation.groupby("geolocation_zip_code_prefix", as_index=False)
            .agg(
                geolocation_lat=("geolocation_lat", "mean"),
                geolocation_lng=("geolocation_lng", "mean"),
            )
        )

        customer_geo = geo.rename(
            columns={
                "geolocation_zip_code_prefix": "customer_zip_code_prefix",
                "geolocation_lat": "customer_lat",
                "geolocation_lng": "customer_lng",
            }
        )

        seller_geo = geo.rename(
            columns={
                "geolocation_zip_code_prefix": "seller_zip_code_prefix",
                "geolocation_lat": "seller_lat",
                "geolocation_lng": "seller_lng",
            }
        )

        df = orders.merge(customers, on="customer_id", how="left")
        df = df.merge(
            order_items[["order_id", "seller_id"]],
            on="order_id",
            how="left",
        )
        df = df.merge(sellers, on="seller_id", how="left")
        df = df.merge(customer_geo, on="customer_zip_code_prefix", how="left")
        df = df.merge(seller_geo, on="seller_zip_code_prefix", how="left")

        df = df.dropna(
            subset=["customer_lat", "customer_lng", "seller_lat", "seller_lng"]
        ).copy()

        df["distance_seller_customer"] = self._haversine_distance(
            df["customer_lat"],
            df["customer_lng"],
            df["seller_lat"],
            df["seller_lng"],
        )

        matching_geo = (
            df.groupby("order_id", as_index=False)
            .agg(distance_seller_customer=("distance_seller_customer", "mean"))
        )

        return matching_geo
