# 📈 Stocks API

A FastAPI demo service that fetches stock data from Polygon.io and scrapes performance from MarketWatch.

---

## What does it do?
- **GET /stock/{symbol}** – Returns up-to-date stock data + performance table.
- **POST /stock/{symbol}** – Updates amount (body: {"amount": int}).

---

## Quick Setup

1. **Create a Python venv:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set your API Key:**
   - Copy `.env.example` to `.env` and set your POLYGON_API_KEY.
4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Docker (optional)
```bash
docker build -t stocks-api .
docker run -p 8000:8000 --env-file .env stocks-api
```

---

## API Example

### Get stock:
```bash
curl http://localhost:8000/stock/IBM
```

### Update amount:
```bash
curl -X POST http://localhost:8000/stock/IBM -H "Content-Type: application/json" -d '{"amount": 5}'
```

---

## Testing
```bash
pip install -r requirements-dev.txt
pytest
```

---

## Project Structure
```
app/    # main application code
  main.py
  models/
  services/
  repositories/
  api/v1/routers/
tests/  # test code
```
