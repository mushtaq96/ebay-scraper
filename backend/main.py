import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from emailing.sender import send_email
from db.db import get_db_conn, get_links, insert_links, link_exists, create_links_table
import schedule
import time
import threading
from dotenv import load_dotenv

from urllib.parse import quote_plus

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


query = ""

@app.on_event("startup")
async def startup():
    async with get_db_conn() as conn:
        await create_links_table(conn)


@app.get("/query")
async def get_query(q: str):
    async with get_db_conn() as conn:
        # code for checking ebay kleinanzeigen listings and sending email
        global query
        query = quote_plus(q)
        listings = get_listings()

        # Process listings
        new_listings = []
        for listing in listings:
            exists = await link_exists(conn, listing['image_url'])
            print(f"Checking if link exists: {listing['image_url']} - Exists: {exists}")
            if not exists:
                await insert_links(conn, listing['image_url'])
                new_listings.append(listing)
                print(f"Added to new_listings: {listing['image_url']}") 
        print(f"Total new listings: {len(new_listings)}")
        
        # Send email with formatted content
        if new_listings:
            await send_notification_async(new_listings)
        return {"message": f"Query received: {query}", "new_listings": len(new_listings)}

async def send_notification_async(listings):
    sender = os.environ.get('SENDER_MAIL')
    receiver = os.environ.get('RECEIVER_MAIL')
    
    # Create the HTML content with f-string for immediate formatting
    listings_html = "\n".join([
        f"""
        <div class="listing">
            <h3>{listing['title']}</h3>
            <p class="price">{listing['price']}</p>
            <p>{listing['description']}</p>
            <a href="{listing['image_url']}">View Listing</a>
        </div>
        """ for listing in listings
    ])

    html_content = f"""
    <html>
    <head>
        <style>
            .listing {{
                border: 1px solid #ddd;
                margin: 10px 0;
                padding: 15px;
                border-radius: 5px;
            }}
            .listing img {{
                max-width: 200px;
                height: auto;
                margin: 10px 0;
            }}
            .price {{
                font-weight: bold;
                color: #2c5282;
            }}
        </style>
    </head>
    <body>
        <h2>New Listings Found!</h2>
        <p>We found {len(listings)} new listing(s):</p>
        {listings_html}
    </body>
    </html>
    """

    subject = f"New Ebay Kleinanzeigen Listings - {len(listings)} found"
    send_email(sender, os.environ.get('SENDER_PASSWORD'), receiver, subject, html_content)

def get_listings():
    global query
    if not query:
        return []
    # Fügt die Query in den Ebay-Kleinanzeigen URL ein. / Inserts the query into the Ebay-Kleinanzeigen URL.
    URL = "https://www.kleinanzeigen.de/s-eschborn/" + \
        query + "/k0l4558r20" # 20 stands for 20 km radius

    # Setzt die Headers der Anfrage (Den User-Agent), damit Ebay-Kleinanzeigen die Anfrage nicht blockt. / Sets the headers of the request (the User-Agent) so that Ebay-Kleinanzeigen does not block the request.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }

    # Gibt den HTML text der Website in eine Variable wieder. / Puts the HTML text of the website into a variable again.
    response = requests.get(url=URL, headers=headers)

    # Setzt den Content der Website in eine Variable. / Sets the content of the website into a variable.
    page = response.content

    # Erstellt eine BeautifulSoup-Instanz mit dem Website-Content und einem passendem Parser. / Creates a BeautifulSoup instance with the website content and a suitable parser.
    soup = BeautifulSoup(page, "html.parser")
    # Setzt die Search-Results-Content in eine Variable. / Sets the search results content into a variable.
    srchRsltsContent = soup.find("div", id="srchrslt-content")

    # Setzt die Einträge inheralb der Seach-Results und dem Table dortdrinn in eine Variable / Array. / Sets the entries within the search results and the table therein into a variable/array.
    srchRslts = soup.find_all("li")

    # Setzt einen Counter. / Sets a counter.
    counter = 0

    # Setzt einen zweiten Counter. / Sets a second counter for 'VB' listings.
    vbCounter = 0
    ePreise = []

    count = 0
    listings = []
    baseURL = 'https://www.kleinanzeigen.de'
    result = soup.find_all('ul', {'id': 'srchrslt-adtable'})
    
    for ul in result:
        li_elements = ul.find_all('li', {'class': 'ad-listitem'})
        for li in li_elements:
            listing = {}
            article = li.find('article', class_='aditem')
            if not article:
                continue
            # Extract image URL
            image_div = article.find('div', class_='aditem-image')
            image_a = image_div.find('a')
            listing['image_url'] = 'https://www.kleinanzeigen.de' + image_a['href']
            
            # Extract price
            price_div = article.find('div', class_='aditem-main--middle--price-shipping')
            if price_div:
                price_text = price_div.find('p', class_='aditem-main--middle--price-shipping--price').text.strip()
                listing['price'] = price_text
            
            # Extract title and description
            title_a = article.find('h2', class_='text-module-begin').find('a')
            listing['title'] = title_a.text.strip()
            listing['description'] = article.find('p', class_='aditem-main--middle--description').text.strip()
            
            listings.append(listing)
    
    return listings

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


# create a schedule to run every 2 minutes
schedule.every(2).minutes.do(get_listings)

# start the schedule in a separate thread
schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()
