import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import random


# Function to scrape product details
def scrape_amazon_products():
    # Define the URL for the Amazon search page
    # Note: This code works for those product which is displayed by Amazon in a list format, and not in a grid format. 
    url = "https://www.amazon.com/s?k=flipper+zero&crid=1GRO0CVFPVC8E&sprefix=%2Caps%2C88&ref=nb_sb_ss_recent_3_0_recent"

    # List of user agents to rotate for each request
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

    # Set up Chrome options for headless browsing
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Set up the Chrome driver
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    products_data = []

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for a few seconds to ensure the page is fully loaded
        time.sleep(random.uniform(2, 5))

        # Parse the page content with BeautifulSoup
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')

        # Find the main container with product listings
        product_container = soup.find('div', {'class': 's-main-slot s-result-list s-search-results sg-row'})

        if product_container:
            # Loop through all product divs
            products = product_container.find_all('div', {'data-component-type': 's-search-result'})

            for product in products:
                # Extract the product title
                title_element = product.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
                title = title_element.get_text() if title_element else 'No title found'

                # Extract the price
                price_element = product.find('span', {'class': 'a-price-whole'})
                price = price_element.get_text().replace(',', '') if price_element else '0'

                # Extract the rating
                rating_element = product.find('span', {'class': 'a-icon-alt'})
                rating = rating_element.get_text() if rating_element else 'No rating found'

                # Convert price to float
                try:
                    price = float(price)
                except ValueError:
                    price = None

                # Store the product information
                products_data.append({
                    'title': title,
                    'price': price,
                    'rating': rating
                })

    finally:
        # Quit the driver
        driver.quit()

    return products_data


# Function to save the data to a JSON file
def save_to_json(data, filename='product_data.json'):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


# Function to load data from a JSON file
def load_from_json(filename='product_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    return []


# Function to compare prices and notify the user of changes
def compare_prices_and_notify(new_data, old_data):
    notifications = []

    # Compare each item in the new data with the old data
    for new_item in new_data:
        title = new_item['title']
        new_price = new_item['price']

        # Find the corresponding old item by title
        old_item = next((item for item in old_data if item['title'] == title), None)

        if old_item and old_item['price'] and new_price:
            old_price = old_item['price']

            # Check if the new price is lower
            if new_price < old_price:
                message = f"Price drop detected for '{title}': Old Price = ${old_price}, New Price = ${new_price}"
                print(message)
                notifications.append({
                    'title': title,
                    'old_price': old_price,
                    'new_price': new_price,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

    return notifications


# Main logic for running the scraper and checking for price drops
def main():
    # Scrape the current product data
    print("Scraping Amazon product details...")
    new_data = scrape_amazon_products()

    # Load previously saved data
    old_data = load_from_json()

    # Compare new data with old data and notify of price drops
    if old_data:
        notifications = compare_prices_and_notify(new_data, old_data)

        if notifications:
            print("\nPrice drop notifications:")
            for note in notifications:
                print(note)
        else:
            print("\nNo price drops detected.")
    else:
        print("\nNo previous data found. Saving current data for future comparisons.")

    # Save the new data to the JSON file for future comparisons
    save_to_json(new_data)
    print("\nData saved successfully.")


# Run the program, wait 2 minutes, and then check for price changes
if __name__ == "__main__":
    main()
    print("\nWaiting for 2 minutes before re-checking prices...")
    time.sleep(120)  # Wait for 120 seconds (2 minutes)
    main()
