 Olist Orders Data Analysis & Feature Engineering

This project focuses on building a clean, feature-rich dataset from raw Olist e-commerce data to enable downstream analytics and machine learning tasks.

The goal is to transform multiple relational datasets into a single training-ready table capturing order behavior, delivery performance, pricing, and customer satisfaction.

 Project Objective

Create a unified dataset at order level containing:

Delivery performance metrics
Customer review signals
Order complexity (items & sellers)
Pricing & freight cost
Optional geographic distance feature

This dataset can be used for:

Business analytics
Machine Learning (e.g. review prediction)
KPI tracking
Dataset Overview

The project uses the following datasets:

orders
order_items
order_reviews
customers
sellers
products
geolocation
 Feature Engineering
1.  Delivery Performance (get_wait_time)

Features:

wait_time
expected_wait_time
delay_vs_expected
order_status

✔ Only delivered orders are considered
✔ Datetime conversions applied
✔ Delay calculated as:

delay = max(actual_delivery - estimated_delivery, 0)
2.  Review Score (get_review_score)

Features:

review_score
dim_is_five_star
dim_is_one_star

✔ Binary flags for extreme satisfaction levels

3.  Number of Items (get_number_items)
number_of_items = count(order_item_id)

✔ Measures order size / complexity

4.  Number of Sellers (get_number_sellers)
number_of_sellers = unique(seller_id)

✔ Indicates multi-seller orders

5.  Price & Freight (get_price)

Features:

price
freight_value

✔ Aggregated per order:

price = sum(price)
freight_value = sum(freight_value)
6.  Distance (Optional) (get_distance_seller_customer)
Uses Haversine formula
Computes distance between:
Customer location
Seller location

✔ If multiple sellers → average distance per order

Final Dataset (get_training_data)

All features are merged into a single DataFrame:

training = (
    wait_time
    + review_score
    + number_of_items
    + number_of_sellers
    + price
)

✔ Final step:

Drop missing values
Reset index

Final Features
Feature	Description
order_id	Unique order ID
wait_time	Delivery duration
expected_wait_time	Estimated delivery time
delay_vs_expected	Delay vs estimation
review_score	Customer rating
dim_is_five_star	5-star flag
dim_is_one_star	1-star flag
number_of_items	Total items
number_of_sellers	Unique sellers
price	Total price
freight_value	Shipping cost
distance_seller_customer	Distance (optional)

 Key Insight (Distance Analysis)
Mean distance ≈ 600 km
Median distance ≈ 433 km
Long-tail distribution (some orders > 8000 km)

Indicates:

Wide geographic coverage
Potential impact on delivery time & satisfaction

 Testing

All features are validated using pytest:

✔ wait_time → PASSED
✔ review_score → PASSED
✔ number_items → PASSED
✔ number_sellers → PASSED
✔ price → PASSED
✔ training_data → PASSED
✔ distance → PASSED

Tech Stack
Python
Pandas
NumPy
Seaborn / Matplotlib
Pytest

How to Run
git clone <repo>
cd data-orders

pip install -r requirements.txt

pytest -v
Business Value

This dataset enables:

Delivery delay analysis
Customer satisfaction modeling
Price vs review relationship
Distance impact on logistics

Author

Doruk Pamir
Data Analyst
