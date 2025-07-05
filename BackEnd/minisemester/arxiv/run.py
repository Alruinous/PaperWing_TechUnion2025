from datetime import date, timedelta
from arxiv_crawler import ArxivScraper
today = date.today().strftime("%Y-%m-%d"),

scraper = ArxivScraper(
    date_from=today,
    date_until=today,
)
scraper.fetch_update()
scraper.to_markdown()
scraper.to_csv(csv_config=dict(delimiter="\t", header=False))