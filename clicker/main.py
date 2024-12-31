import json
import os
import random
import time
import uuid
from datetime import datetime
from typing import List

from agentdesk import Desktop
from google.cloud import storage
from PIL import Image

# Define your list of popular websites
popular_websites = [
    # Travel & Accommodation
    "https://www.airbnb.com",
    "https://www.booking.com",
    "https://www.expedia.com",
    "https://www.tripadvisor.com",
    "https://www.hotels.com",
    "https://www.kayak.com",
    "https://www.opentable.com",
    "https://flights.google.com",
    # Real Estate
    "https://www.zillow.com",
    "https://www.realtor.com",
    "https://www.trulia.com",
    "https://www.redfin.com",
    "https://www.apartments.com",
    # Shopping
    "https://www.amazon.com",
    "https://www.walmart.com",
    "https://www.target.com",
    "https://www.ebay.com",
    "https://www.etsy.com",
    "https://www.bestbuy.com",
    "https://www.lowes.com",
    "https://www.ikea.com",
    "https://www.macys.com",
    "https://www.nordstrom.com",
    "https://www.dickssportinggoods.com",
    # Entertainment
    "https://www.youtube.com",
    "https://www.twitch.tv",
    # Entertainment & Culture
    "https://www.imdb.com",
    "https://www.rottentomatoes.com",
    "https://www.metacritic.com",
    "https://www.billboard.com",
    "https://www.rollingstone.com",
    # News & Information
    "https://www.cnn.com",
    "https://www.bbc.com",
    "https://www.nytimes.com",
    "https://www.wikipedia.org",
    "https://www.weather.com",
    "https://www.reuters.com",
    "https://www.apnews.com",
    "https://www.bloomberg.com",
    "https://www.theguardian.com",
    "https://www.washingtonpost.com",
    "https://www.usatoday.com",
    "https://www.foxnews.com",
    "https://www.nbcnews.com",
    "https://www.huffpost.com",
    # Tech News
    "https://www.theverge.com",
    "https://www.techcrunch.com",
    "https://www.wired.com",
    "https://www.cnet.com",
    "https://www.engadget.com",
    # E-commerce & Classifieds
    "https://www.craigslist.org",
    "https://www.wayfair.com",
    "https://www.homedepot.com",
    "https://www.costco.com",
    "https://www.overstock.com",
    # Job Search
    "https://www.indeed.com",
    "https://www.glassdoor.com",
    # Tech & Productivity
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.google.com",
    # Education
    "https://www.khanacademy.org",
    "https://www.duolingo.com",
    # Sports
    "https://www.espn.com",
    "https://www.nba.com",
    "https://www.nfl.com",
    "https://www.mlb.com",
    "https://www.fifa.com",
    # Health & Wellness
    "https://www.webmd.com",
    "https://www.mayoclinic.org",
    "https://www.healthline.com",
    # Gaming
    "https://www.epicgames.com",
    "https://www.minecraft.net",
    "https://www.playstation.com",
    # Food & Recipes
    "https://www.allrecipes.com",
    "https://www.foodnetwork.com",
    "https://www.epicurious.com",
    "https://www.simplyrecipes.com",
    "https://www.seriouseats.com",
    "https://www.taste.com.au",
    "https://www.bbcgoodfood.com",
    "https://www.bonappetit.com",
    # Automotive
    "https://www.cars.com",
    "https://www.autotrader.com",
    "https://www.kbb.com",
    "https://www.edmunds.com",
    # Reference & Education
    "https://www.britannica.com",
    "https://www.dictionary.com",
    "https://www.thesaurus.com",
    "https://www.howstuffworks.com",
    "https://www.nationalgeographic.com",
    # Science & Technology
    "https://www.space.com",
    "https://www.scientificamerican.com",
    "https://www.popsci.com",
    # Home & Garden
    "https://www.bhg.com",
    "https://www.hgtv.com",
    "https://www.bobvila.com",
    "https://www.familyhandyman.com",
]


def upload_to_gcs(image: Image.Image, bucket_name: str) -> str:
    """Upload image to GCS and return the path"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Create unique filename with timestamp
    file_id = str(uuid.uuid4())
    blob_path = f"datasets/clicker/screenshots/{file_id}.png"
    blob = bucket.blob(blob_path)

    # Save image temporarily and upload
    temp_path = f"/tmp/{file_id}.png"
    image.save(temp_path)
    blob.upload_from_filename(temp_path)
    # Make the blob public
    blob.make_public()

    # Clean up temp file
    os.remove(temp_path)

    # Return the public URL instead of the gs:// path
    return blob.public_url


def random_mouse_movement(
    desktop: Desktop, bucket_name: str, num_moves: int = 10
) -> List[dict]:
    queries = []

    width, height = 1024, 768

    for _ in range(num_moves):
        x = random.randint(0, width)
        y = random.randint(0, height)

        desktop.move_mouse(x, y)
        time.sleep(0.1)

        shots = desktop.take_screenshots()
        screenshot = shots[-1]

        # Upload screenshot to GCS
        image_path = upload_to_gcs(screenshot, bucket_name)

        # Create query entry
        query_entry = {
            "query": "What are the current coordinates of the mouse <image>",
            "images": [image_path],
            "response": json.dumps({"x": x, "y": y}),
        }
        queries.append(query_entry)

    return queries


def simulate_browsing(
    desktop: Desktop,
    bucket_name: str,
    click_limit: int = 10,
    num_moves: int = 10,
):
    clicks = 0
    total_examples = 0
    start_time = time.time()
    urls_visited = []

    # Create a filename with timestamp
    filename = f"browsing_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

    while True:
        url = random.choice(popular_websites)
        urls_visited.append(url)
        desktop.open_url(url)
        print(f"Opened URL: {url}")

        time.sleep(4)

        while clicks < click_limit:
            # Get queries with screenshots and coordinates
            queries = random_mouse_movement(desktop, bucket_name, num_moves=num_moves)
            total_examples += len(queries)

            # Write each query to JSONL
            with open(filename, "a") as f:
                for query in queries:
                    f.write(json.dumps(query) + "\n")
                    f.flush()

            desktop.click()
            clicks += 1

            # Print periodic statistics
            elapsed_time = time.time() - start_time
            print("\nProgress Statistics:")
            print(f"Total examples collected: {total_examples}")
            print(f"Unique websites visited: {len(urls_visited)}")
            print(f"Running time: {elapsed_time:.1f} seconds")
            print(
                f"Collection rate: {total_examples / elapsed_time:.1f} examples/second"
            )
            print(f"Current click: {clicks}/{click_limit}\n")

            time.sleep(4)

        # Reset clicks for next iteration
        clicks = 0


if __name__ == "__main__":
    desktop = Desktop.docker()
    bucket_name = "agentsea-dev-hub-images"
    simulate_browsing(desktop, bucket_name, click_limit=10, num_moves=10)
