from DrissionPage import Chromium
import time
import csv

# Step 1: Initialize Drission and DrissionPage
browser = Chromium()
page = browser.latest_tab

# Step 2: Prompt the user to enter the search query
search_query = input("Enter your search query: ").strip()
if not search_query:
    print("Search query cannot be empty. Exiting...")
    exit()

# Step 3: Construct the Amazon search URL
url = f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}"

# Step 4: Open the Amazon search page
print(f"Searching for '{search_query}' on Amazon...")
page.get(url)

# Optional: Wait for the page to load completely
time.sleep(5)  # Increased wait time to ensure dynamic content loads

# Step 5: Extract product information (names, links, and prices)
names = []
links_to_product = []
prices = []

def extract_data():
    """Function to extract product data from the current page."""
    global names, links_to_product, prices

    # Extract product names
    for item in page.eles('css: h2.a-size-base-plus span'):
        try:
            name = item.text  # Note: Use `item.text`
            print(name)
            names.append(name)
        except Exception as e:
            print(f"Error extracting title: {e}")
            names.append("N/A")

    # Extract product links
    for i in page.eles('css: a.s-line-clamp-4'):
        try:
            link = i.attr('href')
            if link.startswith("/"):
                link = "https://www.amazon.com" + link
            print(link)
            links_to_product.append(link)
        except Exception as e:
            print(f"Error extracting link: {e}")
            links_to_product.append("N/A")

    # Extract product prices
    for idx, whole_price_elem in enumerate(page.eles('css: span.a-price-whole'), start=1):
        try:
            whole_price = whole_price_elem.text.strip()
        except Exception:
            whole_price = "N/A"

        try:
            decimal_price_elem = page.ele(f'css: span.a-price-fraction')
            decimal_price = decimal_price_elem.text.strip() if decimal_price_elem else ""
            print(decimal_price)
        except Exception:
            decimal_price = ""

        price = f"{whole_price}{decimal_price}" if whole_price != "N/A" else "N/A"
        print(price)
        prices.append(price)

# Step 6: Pagination loop
max_pages = 2  # Maximum number of pages to scrape (adjust as needed)
current_page = 1

while current_page <= max_pages:
    print(f"\nExtracting data from page {current_page}...")
    extract_data()

    # Check if the "Next" button exists
    try:
        next_button = page.ele('css: a.s-pagination-next')
        if next_button:
            print("Navigating to the next page...")
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
            current_page += 1
        else:
            print("No more pages to navigate. Stopping pagination.")
            break
    except Exception as e:
        print(f"Error during pagination: {e}")
        break

# Step 7: Save the extracted links to a CSV file
csv_filename = "product_links.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Link", "Price"])
    for name, link, price in zip(names, links_to_product, prices):
        writer.writerow([name, link, price])
print(f"Product links saved to {csv_filename}")

# Step 8: Open each link and extract additional features including Product Image and Key Features
def extract_additional_features(link):
    """Function to extract additional features from a product page."""
    try:
        page.get(link)
        time.sleep(3)  # Wait for the page to load

        # Extract product description
        try:
            description = page.ele('css: div#productDescription>p>span').text.strip()
        except Exception:
            description = "N/A"

        # Extract average rating
        try:
            rating = page.ele('css: span.a-icon-alt').text.strip()
        except Exception:
            rating = "N/A"

        # Extract Product ID
        try:
            product_id = page.ele('xpath: //*[@id="productDetails_detailBullets_sections1"]/tbody/tr[1]/td').text.strip()
        except Exception:
            product_id = "N/A"

        # Extract Product Image URL
        try:
            image_url = page.ele('css: img#landingImage').attr('src')
        except Exception:
            image_url = "N/A"

        # Extract Key Features
        try:
            features = []
            for feature in page.eles('css: ul.a-unordered-list.a-vertical.a-spacing-mini > li > span'):
                features.append(feature.text.strip())
            combined_features = " | ".join(features) if features else "N/A"
        except Exception:
            combined_features = "N/A"

        return {
            "Description": description,
            "Rating": rating,
            "Product ID": product_id,
            "Image URL": image_url,
            "Key Features": combined_features
        }
    except Exception as e:
        print(f"Error extracting features from {link}: {e}")
        return {
            "Description": "N/A",
            "Rating": "N/A",
            "Product ID": "N/A",
            "Image URL": "N/A",
            "Key Features": "N/A"
        }

# Step 9: Extract additional features for all links
additional_data = []
for idx, link in enumerate(links_to_product, start=1):
    print(f"\nExtracting additional features from product {idx}: {link}")
    features = extract_additional_features(link)
    additional_data.append({
        "Link": link,
        "Description": features["Description"],
        "Rating": features["Rating"],
        "Product ID": features["Product ID"],
        "Image URL": features["Image URL"],
        "Key Features": features["Key Features"]
    })

# Step 10: Save the additional features to a CSV file
additional_csv_filename = "product_details.csv"
with open(additional_csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Link", "Description", "Rating", "Product ID", "Image URL", "Key Features"])
    writer.writeheader()
    writer.writerows(additional_data)
print(f"Additional product details saved to {additional_csv_filename}")

# Step 11: Close the browser session
browser.quit()