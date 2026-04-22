def get_deals():
    print("🚀 Fetching deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        print(f"Products found: {len(items)}")

        for item in items[:10]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            page = requests.get(link, headers=headers)
            psoup = BeautifulSoup(page.text, "html.parser")

            # ===== EXTRACT =====
            price_tag = psoup.select_one(".a-price-whole")
            mrp_tag = psoup.select_one(".a-text-price span")
            rating_tag = psoup.select_one(".a-icon-alt")
            review_tag = psoup.select_one("#acrCustomerReviewText")

            price = price_tag.get_text(strip=True).replace(",", "") if price_tag else "0"
            mrp = mrp_tag.get_text(strip=True).replace("₹", "").replace(",", "") if mrp_tag else "0"
            rating = rating_tag.get_text(strip=True) if rating_tag else ""
            reviews = review_tag.get_text(strip=True) if review_tag else ""

            try:
                price_value = int(price)
                mrp_value = int(mrp)
                rating_value = float(rating.split()[0])
                review_count = int(reviews.split()[0].replace(",", ""))
            except:
                continue

            # ===== CALCULATE DISCOUNT =====
            if mrp_value > 0:
                discount = int(((mrp_value - price_value) / mrp_value) * 100)
            else:
                continue

            # ===== REAL DEAL FILTER =====
            if rating_value < 4.0:
                continue

            if review_count < 500:
                continue

            if discount < 30:
                continue

            # ===== MESSAGE =====
            msg = f"""🔥 REAL DEAL

📦 {title}
💰 ₹{price_value} (₹{mrp_value})
🔥 {discount}% OFF
⭐ {rating}
📝 {reviews}

👉 {link}
"""

            deals.append(msg)

    except Exception as e:
        print("Scraping error:", e)

    print(f"Deals ready: {len(deals)}")
    return deals