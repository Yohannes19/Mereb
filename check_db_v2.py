from app.database import SessionLocal
from app.models import Profile, ProofItem
import os

print(f"Current working directory: {os.getcwd()}")
print(f"DATABASE_URL (from database.py context): ...")

db = SessionLocal()
p = db.query(Profile).filter_by(slug="muna-studio").first()
if p:
    print(f"Profile: {p.display_name}, Slug: {p.slug}")
    for item in p.proof_items:
        print(f"  Proof Item: {item.title}, URL: {item.proof_url}")
else:
    print("Muna Studio not found!")
db.close()
