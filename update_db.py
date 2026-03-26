from app.database import SessionLocal
from app.models import Profile, ProofItem

db = SessionLocal()
profile = db.query(Profile).filter_by(slug="muna-studio").first()
if profile:
    for item in profile.proof_items:
        if "instagram.com" in item.proof_url:
            item.proof_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            print("Updated demo proof to YouTube.")
    db.commit()
db.close()
