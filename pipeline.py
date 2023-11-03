import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import time
import sqlite3

API_KEY = "0a0a4ce5b9d5043dad0dffa00fdcd250"

def create_db():
    conn = sqlite3.connect('sales_database.db')
    cursor = conn.cursor()

    # Drop the tables if they already exist
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS weather_data")

    # Creating Table 1 with order_id and product_id as a composite primary key
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        order_date DATE,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # Creating Table 2
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        email TEXT,
        lat REAL,
        lng REAL
    )
    """)

    # Creating Table 3
    cursor.execute("""
    CREATE TABLE weather_data (
        lat REAL,
        lng REAL,
        temperature REAL,
        weather TEXT,
        PRIMARY KEY (lat, lng),
        FOREIGN KEY (lat, lng) REFERENCES customers(lat, lng)
    )
    """)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Sales Database created, with following tables: orders, customers,  weather_data")
    

def get_sales_data(base_path):
    df = pd.read_csv(base_path)
    return df



def clean_sales_data(df):
    mask = df.groupby('order_id')['customer_id'].transform('nunique') == 1
    df = df[mask]  
    return df

def write_sales_data_to_db(df):
    conn = sqlite3.connect('sales_database.db')
    df.to_sql('orders', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    print('Sales data written to db.')



def fetch_user_data():
    url = "https://jsonplaceholder.typicode.com/users"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        users = response.json()

        # Extract the required fields from each user
        extracted_data = []
        for user in users:
            data = {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "email": user["email"],
                "lat": user["address"]["geo"]["lat"],
                "lng": user["address"]["geo"]["lng"]
            }
            extracted_data.append(data)
        print('User data successfully fetched from Endpoint.')
        return pd.DataFrame(extracted_data)
    else:
        print("Failed to retrieve data!")
        return None
    
    

def write_user_data_to_db(user_data_df):
    conn = sqlite3.connect('sales_database.db')
    user_data_df.to_sql('customers', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()    
    print('User data written to db.')
    

def write_weather_data_to_db(weather_data_df):
    conn = sqlite3.connect('sales_database.db')
    weather_data_df.to_sql('weather_data', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()    
    print('Weather data written to db.')
    
    
    
def get_weather(api_key, lat, lon):
#     print('Get Weather function called!')
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric'  
    }
    
    response = requests.get(base_url, params=params)
    response_data = response.json()

    if response.status_code == 200:
        weather_condition = response_data['weather'][0]['description']
        current_temperature = response_data['main']['temp']
        return weather_condition, current_temperature
    else:
        print(f"Error {response_data['cod']}: {response_data['message']}")
        return None, None
    
    
    
def get_historical_weather(api_key, lat, lon, date_string):
    base_url = "https://api.openweathermap.org/data/2.5/onecall/timemachine"
    
    # Convert the date string to a Unix timestamp at 00:00:00
    timestamp = int(time.mktime(time.strptime(date_string, '%Y-%m-%d')))
    
    params = {
        'lat': lat,
        'lon': lon,
        'dt': timestamp,
        'appid': api_key,
        'units': 'metric'  # This will give you temperature in Celsius. Change to 'imperial' for Fahrenheit.
    }

    response = requests.get(base_url, params=params)
    response_data = response.json()

    if response.status_code == 200:
        weather_condition = response_data['current']['weather'][0]['description']
        current_temperature = response_data['current']['temp']
        return weather_condition, current_temperature
    else:
        print(f"Error {response_data['cod']}: {response_data['message']}")
        return None, None
    
    

def add_weather_data_to_df(df, api_key):
    
    df['weather'] = ''
    df['temperature'] = ''
    unique_customers = df['customer_id'].unique()
    for customer in unique_customers:
        sample_row = df[df['customer_id'] == customer].iloc[0]
        lat, lon = sample_row['lat'], sample_row['lng']
        
        weather, temperature = get_weather(api_key, lat, lon)

        df.loc[df['customer_id'] == customer, 'weather'] = weather
        df.loc[df['customer_id'] == customer, 'temperature'] = temperature

    return df



def visualize_total_sales(df):
    # Calculate total sales amount and get the name for each customer_id
    sales_per_customer = df.groupby('customer_id').agg({
        'sales_amount': 'sum',
        'name': 'first'  # Since names are same for the same customer_id, 'first' will give us the correct name
    }).reset_index()

    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(sales_per_customer['customer_id'].astype(str), sales_per_customer['sales_amount'])

    # Label the bars with customer names
    for bar, name in zip(bars, sales_per_customer['name']):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, name, ha='center', va='bottom', rotation=45)

    plt.xlabel('Customer ID')
    plt.ylabel('Total Sales Amount')
    plt.title('Total Sales Amount Per Customer')
    plt.xticks(sales_per_customer['customer_id'].astype(str))
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig("results/Total_sales.png")
    print("Total sales analysis completed.")
    
    
    
def visualize_average_quantity(df):
    average_order_quantity = df.groupby('product_id')['quantity'].mean().reset_index()
    plt.figure(figsize=(12, 6))
    plt.bar(average_order_quantity['product_id'].astype(str), average_order_quantity['quantity'])
    plt.xlabel('Product ID')
    plt.ylabel('Average Quantity')
    plt.title('Average order quantity per product')
    plt.xticks(average_order_quantity['product_id'].astype(str))
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig("results/Average_quantity_per_product.png")
    print('Average quantity per product analysis completed. ')
    
    
    
def find_top_selling_product(df):
    most_sold_product_quantity = df.groupby('product_id')['quantity'].sum().reset_index()
    most_sold_product_quantity.sort_values('quantity', inplace=True, ascending=False, ignore_index=True)
    top_10_products = most_sold_product_quantity.head(10)
    plt.figure(figsize=(12, 8))
    plt.bar(top_10_products['product_id'].astype(str), top_10_products['quantity'], color='skyblue')
    plt.xlabel('Product ID')
    plt.ylabel('Total Quantity Sold')
    plt.title('Top 10 Most Selling Products')
    plt.xticks(top_10_products['product_id'].astype(str))
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig('results/top_10_selling_products.png')
    print('Top selling products analysis completed. ')
    
    
def visualize_sales_per_month(df):
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['year_month'] = df['order_date'].dt.strftime('%Y-%m')
    sales_per_month = df.groupby('year_month')['sales_amount'].sum().reset_index()
    plt.figure(figsize=(12, 8))
    plt.plot(sales_per_month['year_month'], sales_per_month['sales_amount'], marker='o', linestyle='-')
    plt.xlabel('Year-Month')
    plt.ylabel('Total Sales')
    plt.title('Total Sales Over Months')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig("results/Sales_over_months.png")
    print('Monthly sales analysis completed.')

def visualize_sales_per_weather_condition(df):
    sales_per_weather = df.groupby('weather')['sales_amount'].sum().reset_index()
    plt.figure(figsize=(12, 8))
    plt.plot(sales_per_weather['weather'], sales_per_weather['sales_amount'], marker='o', linestyle='-')
    plt.xlabel('Weather Condition')
    plt.ylabel('Total Sales')
    plt.title('Total Sales Over weather condition')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig('results/Sales_over_weather_cond.png')
    print('Sales over weather condition completed. ')
    
    
    
def main():
    create_db()
    base_path = 'sales_data.csv'
    df = get_sales_data(base_path)
    df = clean_sales_data(df)
    write_sales_data_to_db(df)
    user_data_df = fetch_user_data()
    if user_data_df is None:
        print('Failed to fetch User data, closing the program.')
        return
    write_user_data_to_db(user_data_df)
    
    merged_df = df.merge(user_data_df, left_on="customer_id", right_on='id')
    
    weather_data = []

# Iterate over each row in your DataFrame
    for index, row in user_data_df.iterrows():
        weather, temp = get_weather(API_KEY, row['lat'], row['lng'])
        if temp is not None and weather is not None:
            # Create a dictionary for the current row and add it to the list
            weather_data.append({
                'lat': row['lat'],
                'lng': row['lng'],
                'weather': weather,
                'temperature': temp
            })

    # Convert the list of dictionaries to a DataFrame
    weather_df = pd.DataFrame(weather_data)
            
    write_weather_data_to_db(weather_df)
    
    final_df = add_weather_data_to_df(merged_df, API_KEY)
    final_df['sales_amount'] = final_df['price']*final_df['quantity']
    
    visualize_total_sales(final_df)
    visualize_average_quantity(final_df)
    find_top_selling_product(final_df)
    visualize_sales_per_month(final_df)
    visualize_sales_per_weather_condition(final_df)
    
    
if __name__ == '__main__':
    main()