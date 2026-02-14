from database import engine, Base
import models  # IMPORTANT: ensures models are registered

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Tables reset successfully.")
