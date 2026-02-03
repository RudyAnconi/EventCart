# EventCart

EventCart is a full-stack demo storefront that showcases an order workflow using the outbox pattern, idempotency, and reliable async processing. It is designed to be interview-ready: clean architecture, modern stack, and a tight demo flow.

## What It Is
- FastAPI + Postgres backend with JWT auth and refresh rotation.
- Outbox pattern with a worker that reliably processes `order.paid` events.
- Next.js storefront with a cart, checkout, orders, and simulated payment.

## Architecture Overview
- **API** (`/apps/api`): FastAPI async app. Modules are split into `api`, `services`, `repo`, and `models`.
- **Worker** (`/apps/worker`): Polls the outbox table and fulfills orders with retries/backoff.
- **Web** (`/apps/web`): Next.js App Router UI with TanStack Query.
- **Database** (Postgres 16): stores users, orders, outbox, idempotency keys, and sessions.

Auth notes:
- Refresh token is stored in an `httpOnly` cookie.
- Access token is stored in memory + `localStorage` for demo simplicity.

### Outbox Flow
1. Order created with `PENDING_PAYMENT` and stock is reserved.
2. `/payments/confirm/{order_id}` marks order `PAID` and inserts an outbox event in the same transaction.
3. Worker claims events using `SELECT ... FOR UPDATE SKIP LOCKED` and marks orders `FULFILLED`.
4. Failures retry with exponential backoff + jitter. After max attempts, events go `DEAD`.

## One-Command Run

```bash
cp .env.example .env

docker compose up --build
```

This will:
- Run migrations
- Start API, worker, web, and Postgres
- Seed demo data

You can also seed explicitly:

```bash
make seed
```

## Demo Script (2–5 Minutes)
1. Open `http://localhost:13000` and show demo credentials.
2. Sign in with `demo@eventcart.dev / Demo1234!`.
3. Browse products and add two tickets to cart.
4. Checkout — show the order created in `PENDING_PAYMENT`.
5. Click “Pay now”. The order changes to `PAID`, then `FULFILLED` after worker processes outbox.
6. Show outbox behavior in logs (worker printing `order.fulfilled`).
7. Optional: repeat checkout quickly and show idempotency by reusing the same `Idempotency-Key`.

## API Examples (curl)

Register:
```bash
curl -i -X POST http://localhost:18000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo2@eventcart.dev","password":"Demo1234!"}'
```

Login:
```bash
curl -i -X POST http://localhost:18000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@eventcart.dev","password":"Demo1234!"}'
```

List products:
```bash
curl http://localhost:18000/products
```

Create order (idempotent):
```bash
curl -i -X POST http://localhost:18000/orders \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <ACCESS_TOKEN>' \
  -H 'Idempotency-Key: demo-123' \
  -d '{"items":[{"product_id":"<PRODUCT_ID>","qty":1}]}'
```

Confirm payment:
```bash
curl -X POST http://localhost:18000/payments/confirm/<ORDER_ID> \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'
```

## Tests

Run backend tests (requires DB and migrations already running):

```bash
make api-test
```

## Troubleshooting
- **Web can’t reach API**: ensure `.env` has `NEXT_PUBLIC_API_URL=http://localhost:18000` and `API_ALLOWED_ORIGINS=http://localhost:13000`.
- **Auth refresh not working**: cookies are `httpOnly` and `sameSite=lax`. For production, set `secure=true`.
- **Worker not processing**: check logs and ensure migrations are applied.

## Repo Layout
```
/apps
  /api
  /worker
  /web
/infra
/migrations
/scripts
```

## Demo Credentials
- Email: `demo@eventcart.dev`
- Password: `Demo1234!`
