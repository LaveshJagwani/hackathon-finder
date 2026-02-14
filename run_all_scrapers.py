from database import SessionLocal
from crud import save_hackathons

from hackerearth import scrape_hackerearth
from devfolio import scrape_devfolio
from unstop import scrape_unstop
from mlh import scrape_mlh
from devpost import scrape_devpost


def main():

    db = SessionLocal()

    print("Scraping HackerEarth...")
    he = scrape_hackerearth()

    print("Scraping Devfolio...")
    df = scrape_devfolio()

    print("Scraping Unstop...")
    us = scrape_unstop()

    print("Scraping MLH...")
    mlh = scrape_mlh()

    print("Scraping Devpost...")
    dp = scrape_devpost()

    all_data = he + df + us + mlh + dp

    print("Saving to database...")
    save_hackathons(db, all_data)

    print("Done.")


if __name__ == "__main__":
    main()
