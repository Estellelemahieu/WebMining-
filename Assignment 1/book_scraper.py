"""Simple scraper for books.toscrape.com

This script downloads the front page at https://books.toscrape.com,
extracts each book's title, price, and star rating, and saves the
results to `books.csv` using pandas.
"""

try:
    import requests
except ImportError:
    raise SystemExit("Missing dependency 'requests'. Install with: python3 -m pip install --user requests")

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit("Missing dependency 'beautifulsoup4'. Install with: python3 -m pip install --user beautifulsoup4")

# pandas is used for saving the full CSV, but make it optional so a quick
# test run can still work even if pandas isn't installed in the environment.
try:
    import pandas as pd
except ImportError:
    pd = None
    print("Warning: 'pandas' not installed. Full CSV output will not be available. Install with: python3 -m pip install --user pandas")

from urllib.parse import urljoin
import time


def extract_rating_int(star_tag):
    """Convert the star-rating class (e.g. 'Three') to an integer 1-5.
    If no rating is found, return None."""
    if not star_tag:
        return None
    classes = star_tag.get('class', [])
    # The rating is encoded as a word in the class list, e.g. ['star-rating', 'Three']
    words = [c for c in classes if c.lower() != 'star-rating']
    if not words:
        return None
    word = words[0].lower()
    mapping = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5
    }
    return mapping.get(word)


def scrape_all_pages(base_url="https://books.toscrape.com"):
    """Scrape all pages by following the 'next' link and return a DataFrame.

    This function downloads each page, extracts title, price and star rating
    from each book entry, and follows pagination until no next page exists.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BookScraper/1.0)'}
    url = base_url
    results = []
    page_num = 1

    while True:
        # Download page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all book entries on the page
        books = soup.find_all('article', class_='product_pod')
        if not books:
            break

        # Extract details for each book
        for book in books:
            title_tag = book.find('h3').find('a')
            title = title_tag.get('title', '').strip()

            price_text = book.find('p', class_='price_color').text.strip()
            # Remove currency symbol and convert to float
            price = float(price_text.replace('£', '').strip())

            rating_tag = book.find('p', class_='star-rating')
            rating = extract_rating_int(rating_tag)

            results.append({'title': title, 'price': price, 'rating': rating})

        print(f"Scraped page {page_num}: {len(books)} books")
        page_num += 1

        # Look for a 'next' link and follow it if present
        next_li = soup.find('li', class_='next')
        if next_li and next_li.find('a'):
            next_href = next_li.find('a')['href']
            url = urljoin(url, next_href)
            # Polite delay between requests
            time.sleep(1)
            continue
        else:
            break

    # Convert to pandas DataFrame
    df = pd.DataFrame(results, columns=['title', 'price', 'rating'])
    return df


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Scrape books.toscrape.com and save to books.csv')
    parser.add_argument('--test', action='store_true', help='Run a quick test: print books from the first page without saving')
    parser.add_argument('--test-count', type=int, default=10, help='Number of books to print in test mode')
    parser.add_argument('--output', type=str, default='books.csv', help='Output CSV filename')
    args = parser.parse_args()

    if args.test:
        # Quick test mode: download the front page and print the first N books
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; BookScraper/1.0)'}
        url = 'https://books.toscrape.com'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        results = []
        for book in books[:args.test_count]:
            title = book.find('h3').find('a').get('title', '').strip()
            price_text = book.find('p', class_='price_color').text.strip()
            price = float(price_text.replace('£', '').strip())
            rating = extract_rating_int(book.find('p', class_='star-rating'))
            results.append({'title': title, 'price': price, 'rating': rating})
        for r in results:
            print(r)
        print(f"\nPrinted {len(results)} books (test mode).")
    else:
        # Full run: require pandas to save CSV
        if pd is None:
            raise SystemExit("Missing dependency 'pandas'. Install with: python3 -m pip install --user pandas")
        df = scrape_all_pages('https://books.toscrape.com')
        df.to_csv(args.output, index=False, encoding='utf-8')
        print(f"Saved {len(df)} books to {args.output}")
