import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load database URL
load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL_NON_POOLING")
if not DATABASE_URL:
    raise ValueError("POSTGRES_URL_NON_POOLING not set")
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

# Create engine
engine = create_engine(DATABASE_URL)

def run_migration():
    print("Running migration: Adding profile_image_url to profiles table...")
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='profiles' AND column_name='profile_image_url'"))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE profiles ADD COLUMN profile_image_url VARCHAR(500) NULL"))
                conn.commit()
                print("Successfully added profile_image_url column.")
            else:
                print("Column profile_image_url already exists.")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migration()
