from DrissionPage import Chromium
import time

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

# Extract product names
for item in page.eles('css: h2.a-size-base-plus span'):
    try:
        # Extract the text of the <span> element directly
        name = item.text # Note: Use `item.text`
        print(name)
        names.append(name)
    except Exception as e:
        # Print the exception details
        print(f"Error extracting title: {e}")
        names.append("N/A")

# Extract product links
for i in page.eles('css: a.s-line-clamp-4'):
    try:
        link = i.attr('href')
        print(link)
        links_to_product.append(link)
    except Exception as e:
        print(f"Error extracting link: {e}")
        links_to_product.append("N/A")

# Extract product prices
for idx, whole_price_elem in enumerate(page.eles('css: span.a-price-whole'), start=1):
    try:
        # Extract the whole part of the price
        whole_price = whole_price_elem.text.strip()
    except Exception:
        whole_price = "N/A"

    try:
        # Extract the decimal part of the price (if it exists)
        decimal_price_elem = page.ele(f'css: span.a-price-fraction')
        decimal_price = decimal_price_elem.text.strip() if decimal_price_elem else ""
        print (decimal_price)
    except Exception:
        decimal_price = ""

    # Combine the whole and decimal parts
    price = f"{whole_price}{decimal_price}" if whole_price != "N/A" else "N/A"
    print (price)
    prices.append(price)

# Step 6: Print the results
if names:
    print(f"\nFound {len(names)} products for '{search_query}':")
    for idx, name in enumerate(names, start=1):
        link = links_to_product[idx - 1] if idx <= len(links_to_product) else "N/A"
        price = prices[idx - 1] if idx <= len(prices) else "N/A"
        print(f"Product {idx}:")
        print(f"Name: {name}")
        print(f"Link: https://www.amazon.com{link}")
        print(f"Price: {price}")
        print("-" * 50)
else:
    print(f"No products found for '{search_query}'.")

# Step 7: Close the browser session
browser.quit()