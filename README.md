# Kam Luxury Real Estate – Django + Bootstrap Starter

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Configure
- Edit `.env` with your **Paystack** keys and **WhatsApp** number.
- Add properties in **/admin** (cover image, price, category etc.).
- Studio/1–4BR and Mall Shops included via categories.
- Users can filter/search, chat on WhatsApp, and pay a reservation via Paystack.
