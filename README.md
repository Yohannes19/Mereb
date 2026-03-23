# ProofPage

FastAPI MVP for Ethiopian creators, freelancers, and small businesses who need a public proof profile.

## What it does

- Account signup and login
- Public profile page
- Proof item gallery for finished work
- Ratings and testimonials
- API key auth for adding proof and ratings later

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`.

## Demo login

- Email: `demo@proofpage.et`
- Password: `changeme123`

## Core idea

Many deals happen in DMs, on Telegram, Instagram, or WhatsApp. People can say they have done good work, but they still need proof.

ProofPage gives them one link with:

- real project examples
- testimonials
- ratings
- social links
- trust signals they can share anywhere

## Main routes

- `GET /dashboard`
- `GET /p/{profile_slug}`
- `POST /v1/proof`
- `GET /v1/proof`
- `POST /v1/ratings`
- `GET /v1/ratings`
- `GET /v1/profile`

Swagger UI is available at `http://127.0.0.1:8000/docs`.
