# backend/main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from bs4 import BeautifulSoup
from backend.emailing.sender import send_email  # Keep email import
from backend.alerting.telegram import send_telegram_alert  # Import telegram
from backend.db.db import get_db_conn, link_exists, insert_links, create_links_table
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


async def fetch_page(session, url):
    """Asynchronous helper to fetch pages with proper error handling"""
    try:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to fetch {url}. Status: {response.status}")
            return await response.text()
    except Exception as e:
        raise Exception(f"Error fetching {url}: {str(e)}")


async def parse_listing(article):
    """Parse individual listing with safe element access"""
    listing = {}

    # Safely extract image URL
    image_div = article.find('div', class_='aditem-image')
    if image_div:
        image_a = image_div.find('a')
        if image_a and 'href' in image_a.attrs:
            listing['image_url'] = 'https://www.kleinanzeigen.de' + \
                image_a['href']

    # Safely extract price
    price_div = article.find(
        'div', class_='aditem-main--middle--price-shipping')
    if price_div:
        price_element = price_div.find(
            'p', class_='aditem-main--middle--price-shipping--price')
        listing['price'] = price_element.text.strip() if price_element else ''

    # Safely extract title and description
    title_element = article.find('h2', class_='text-module-begin').find('a')
    listing['title'] = title_element.text.strip() if title_element else ''

    desc_element = article.find('p', class_='aditem-main--middle--description')
    listing['description'] = desc_element.text.strip() if desc_element else ''

    return listing


async def get_listings(query):
    """Main function to fetch and process listings asynchronously"""
    if not query:
        return []

    URL = f"https://www.kleinanzeigen.de/s-eschborn/{query}/k0l4558r20"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            page_content = await fetch_page(session, URL)
            soup = BeautifulSoup(page_content, "html.parser")

            result = soup.find_all('ul', {'id': 'srchrslt-adtable'})
            listings = []

            for ul in result:
                li_elements = ul.find_all('li', {'class': 'ad-listitem'})
                for li in li_elements:
                    article = li.find('article', class_='aditem')
                    if article:
                        listing = await parse_listing(article)
                        if listing.get('image_url'):
                            listings.append(listing)

            return listings
    except Exception as e:
        raise Exception(f"Error processing listings: {str(e)}")


@app.get("/query")
async def get_query(q: str):
    try:
        query = quote_plus(q)
        listings = await get_listings(query)

        async with get_db_conn() as conn:
            new_listings = []
            for listing in listings:
                exists = await link_exists(conn, listing['image_url'])
                print(
                    f"Checking if link exists: {listing['image_url']} - Exists: {exists}")
                if not exists:
                    await insert_links(conn, listing['image_url'])
                    new_listings.append(listing)

            print(f"Total new listings: {len(new_listings)}")
            if new_listings:
                # Try Telegram first
                tg_success = await send_notification_async(new_listings, method='telegram')
                if not tg_success:
                    # Fallback to email if Telegram fails
                    logger.info("Telegram failed, attempting email fallback.")
                    await send_notification_async(new_listings, method='email')
            else:
                logger.info(f"No new listings found for query: {q}")

            return {"message": f"Query received: {query}", "new_listings": len(new_listings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def send_notification_async(listings, method='telegram'):
    if method == 'telegram':
        messages = []
        for listing in listings:
            # Escape HTML characters in title/description if necessary, though basic tags are okay with HTML parse_mode
            title = listing.get('title', 'No Title').replace(
                '<', '<').replace('>', '>')
            price = listing.get('price', 'N/A')
            url = listing.get('image_url', 'No URL')
            msg = f"🆕 <b>{title}</b>\n💶 {price}\n{url}"
            messages.append(msg)
        full_message = "\n\n".join(messages[:10])  # Limit message length
        return send_telegram_alert(full_message)

    elif method == 'email':
        sender = os.environ.get('SENDER_MAIL')
        receiver = os.environ.get('RECEIVER_MAIL')
        if not sender or not receiver:
            logger.error(
                "Email sender or receiver not configured. Cannot send email.")
            return False

        # Create the HTML content with f-string for immediate formatting
        listings_html = "\n".join([
            f"""
            <div class="listing">
                <h3>{listing.get('title', 'No Title')}</h3>
                <p class="price">{listing.get('price', 'N/A')}</p>
                <p>{listing.get('description', '')}</p>
                <a href="{listing.get('image_url', '#')}">View Listing</a>
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
            <h2>New Ebay Kleinanzeigen Listings Found!</h2>
            <p>We found {len(listings)} new listing(s):</p>
            {listings_html}
        </body>
        </html>
        """

        subject = f"New Ebay Kleinanzeigen Listings - {len(listings)} found"
        try:
            send_email(sender, os.environ.get('SENDER_PASSWORD'),
                       receiver, subject, html_content)
            logger.info("Email notification sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    else:
        logger.error(f"Unknown notification method: {method}")
        return False
