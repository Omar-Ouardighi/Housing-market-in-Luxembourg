from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

def extract_listings(soup):

    listings = soup.find_all('article')

    all_listing_details = []

    for listing in listings:
        # Extracting description
        description = listing.find('h3').a.get('title')

        # Extracting price
        price = listing.find('li', class_='propertyPrice').span.get_text()
        link = listing.find('h3').a.get('href')
        # Extracting location
        location = listing.find('span', itemprop='addressLocality').get_text()

        # Extracting area, number of rooms, bathrooms, and parking spaces
        area = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_area02' in str(li)), None)
        number_of_rooms = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_bed02' in str(li)), None)
        number_of_bathrooms = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_bath02' in str(li)), None)
        parking_spaces = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_garage02' in str(li)), None)

        listing_details = {
            'description': description,
            'price': price,
            'location': location,
            'area': area,
            'number_of_rooms': number_of_rooms,
            'number_of_bathrooms': number_of_bathrooms,
            'parking_spaces': parking_spaces,
            'link': link
        }

        all_listing_details.append(listing_details)

    return all_listing_details

def get_next_page_url(soup, base_url):
    # Find the 'next page' link and return its URL if it exists
    next_page = soup.find('a', class_='nextPage')
    return next_page['href'] if next_page else None


def scrape_all_pages(base_url):
    all_data = []
    while True:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        all_data.extend(extract_listings(soup))

        next_page_url = get_next_page_url(soup, base_url)
        if not next_page_url:
            break

        base_url = "https://www.athome.lu" + next_page_url
        time.sleep(1) # Sleep to prevent overwhelming the server

    print("the scraping is done")
    # Save all_data to a CSV file or database
    df = pd.DataFrame(all_data)

    # Save to CSV
    csv_filename = 'listings.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    base_url = 'https://www.athome.lu/srp/?tr=rent&q=faee1a4a&loc=L2-luxembourg&ptypes=flat'
    scrape_all_pages(base_url)