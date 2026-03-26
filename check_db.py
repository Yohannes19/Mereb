from app.database import SessionLocal
from app.models import Profile

db = SessionLocal()
profiles = db.query(Profile).all()
print(f"Total profiles: {len(profiles)}")
for p in profiles:
    print(f"Slug: {p.slug}, Email: {p.email}")
db.close()
