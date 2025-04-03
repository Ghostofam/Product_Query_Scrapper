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

# Step 7: Save the extracted Amazon links to a CSV file
amazon_csv_filename = "amazon_product_links.csv"
with open(amazon_csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Link", "Price"])
    for name, link, price in zip(names, links_to_product, prices):
        writer.writerow([name, link, price])
print(f"Amazon product links saved to {amazon_csv_filename}")

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
additional_csv_filename = "amazon_product_details.csv"
with open(additional_csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Link", "Description", "Rating", "Product ID", "Image URL", "Key Features"])
    writer.writeheader()
    writer.writerows(additional_data)
print(f"Additional product details saved to {additional_csv_filename}")

# Step 11: Scrape Alibaba and save data to CSV
def scrape_alibaba(search_query):
    """Scrape product data from Alibaba and save it to a CSV file."""
    alibaba_url = f"https://www.alibaba.com/trade/search?spm=a2700.galleryofferlist.the-new-header_fy23_pc_search_bar.keydown__Enter&tab=all&SearchText={search_query.replace(' ', '+')}"
    print(f"Searching for '{search_query}' on Alibaba...")
    page.get(alibaba_url)
    time.sleep(5)  # Wait for the page to load

    # Lists to store Alibaba data
    alibaba_names = []
    alibaba_links = []
    alibaba_prices = []

    # Extract product names
    for item in page.eles('css: h2.search-card-e-title>a>span'):
        try:
            name = item.text.strip()
            print(name)
            alibaba_names.append(name)
        except Exception as e:
            print(f"Error extracting title: {e}")
            alibaba_names.append("N/A")

    # Extract product links
    for item in page.eles('css: h2.search-card-e-title>a'):
        try:
            link = item.attr('href')
            print(link)
            alibaba_links.append(link)
        except Exception as e:
            print(f"Error extracting link: {e}")
            alibaba_links.append("N/A")

    # Extract product prices
    for item in page.eles('css: div.search-card-e-price-main'):
        try:
            price = item.text.strip()
            print(price)
            alibaba_prices.append(price)
        except Exception as e:
            print(f"Error extracting price: {e}")
            alibaba_prices.append("N/A")

    # Save the extracted Alibaba data to a CSV file
    alibaba_csv_filename = "alibaba_product_links.csv"
    with open(alibaba_csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Link", "Price"])
        for name, link, price in zip(alibaba_names, alibaba_links, alibaba_prices):
            writer.writerow([name, link, price])
    print(f"Alibaba product links saved to {alibaba_csv_filename}")
    
    return alibaba_links

def extract_alibaba_details(links):
    """Extract detailed attributes, image, and pricing from Alibaba product pages."""
    details_data = []
    for idx, link in enumerate(links, start=1):
        print(f"\nExtracting details from Alibaba product {idx}: {link}")
        try:
            page.get(link)
            time.sleep(3)  # Wait for the page to load

            # Extract attributes
            attributes = []
            for attr_item in page.eles('css: div.attribute-item'):
                try:
                    left = attr_item.ele('css: .left').text.strip()
                    right = attr_item.ele('css: .right').text.strip()
                    combined_attribute = f"{left}: {right}"
                    attributes.append(combined_attribute)
                except Exception as e:
                    print(f"Error extracting attribute: {e}")
                    continue

            combined_attributes = " | ".join(attributes) if attributes else "N/A"

            # Extract product image
            try:
                image_url = page.ele('css: div.id-relative.id-w-full > img').attr('src')
                print(image_url)
            except Exception:
                image_url = "N/A"

            # Extract prices by quantity
            pricing = []
            for qty_elem, price_elem in zip(page.eles('css: div.quality'), page.eles('css: div.price')):
                try:
                    quantity = qty_elem.text.strip()
                    price = price_elem.text.strip()
                    combined_pricing = f"Quantity: {quantity} | Price: {price}"
                    pricing.append(combined_pricing)
                except Exception as e:
                    print(f"Error extracting pricing: {e}")
                    continue

            combined_pricing = " | ".join(pricing) if pricing else "N/A"

            # Append the extracted data
            details_data.append({
                "Link": link,
                "Attributes": combined_attributes,
                "Image URL": image_url,
                "Pricing": combined_pricing
            })
            print(f"Extracted attributes: {combined_attributes}")
            print(f"Extracted image URL: {image_url}")
            print(f"Extracted pricing: {combined_pricing}")
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            details_data.append({
                "Link": link,
                "Attributes": "N/A",
                "Image URL": "N/A",
                "Pricing": "N/A"
            })

    # Save the extracted details to a CSV file
    details_csv_filename = "alibaba_product_details.csv"
    with open(details_csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Link", "Attributes", "Image URL", "Pricing"])
        writer.writeheader()
        writer.writerows(details_data)
    print(f"Alibaba product details saved to {details_csv_filename}")

# Step 10: Scrape Alibaba and extract details
alibaba_links = scrape_alibaba(search_query)
extract_alibaba_details(alibaba_links)

# Step 11: Close the browser session
browser.quit()