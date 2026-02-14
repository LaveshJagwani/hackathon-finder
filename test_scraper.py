from devfolio import scrape_devfolio
from database import SessionLocal
from crud import save_hackathons

data = scrape_devfolio()

db = SessionLocal()

save_hackathons(db, data)

db.close()

print("Data saved to database.")
