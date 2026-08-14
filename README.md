# Demo Fashion Store — E-Commerce Prototype

A mobile-first Django e-commerce prototype for a local clothing store, built
so the same codebase can be re-skinned for a different shop later.

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

# Creates demo categories, 12 demo products, store settings, and an
# admin login (username: owner / password: ChangeThisPassword123)
python manage.py seed_demo

python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- Owner dashboard: http://127.0.0.1:8000/admin-dashboard/
  (login with the `owner` account created by `seed_demo`)

**Change the demo admin password immediately** — either right after first
login via Django's password change flow, or by running
`python manage.py changepassword owner`.

## 2. What's implemented

- Full customer flow: Home → Shop → Product → Cart → Checkout → Order
  Confirmation, with a real Django-backed session cart and server-side
  stock validation (an order can never push stock negative or exceed
  available quantity).
- **Delivery radius (10 km) enforcement that's real, not cosmetic.** The
  checkout page asks the browser for the customer's actual device location
  (HTML5 Geolocation API) and the server computes the true great-circle
  distance to the store's configured coordinates (Haversine formula in
  `store/utils.py`) before allowing the order. If location access is
  denied, the order is blocked with an honest message — the system never
  pretends a typed address or PIN code has been verified. See the comments
  in `store/utils.py` and `store/views.py::checkout` for the full reasoning
  and the documented limitation (no paid geocoding API is wired in — the
  architecture is ready for one).
- **Private owner dashboard** at `/admin-dashboard/…` — every single view is
  wrapped in `store/decorators.py::staff_required`, which checks
  authentication and `is_staff` on the server for every request, not just
  hidden navigation. Try visiting `/admin-dashboard/` while logged out —
  you'll be redirected to login, never shown data.
- Order management (status: New / Confirmed / Completed), product CRUD,
  category management, and a single **Store Settings** page that controls
  every piece of shop-specific branding (name, phone, address, Instagram,
  story, photos, delivery radius).
- Premium, minimal, mobile-first design system in
  `store/static/store/css/style.css` — CSS variables at the top control the
  whole palette/typography for easy re-theming.

## 3. Turning this into a REAL shop

Everything shop-specific lives in one place: **Store Settings** in the
owner dashboard (`/admin-dashboard/settings/`), backed by the single
`StoreConfig` database row (`store/models.py`). To relaunch this for a
different store:

1. Log in to the dashboard → Store Settings → replace name, tagline,
   phone, address, Instagram, story, and upload real photos.
2. Store Settings → set the real `Store Latitude` / `Store Longitude`
   (right-click the shop's exact location on Google Maps to copy
   coordinates) and the desired delivery radius.
3. Dashboard → Products / Categories → delete the demo catalogue and add
   the real one (or bulk-load it — see `store/management/commands/seed_demo.py`
   as a template for a script-based import).
4. `fashion_store/settings.py` → `STORE_DEFAULTS` is only used the very
   first time `seed_demo` runs on a fresh database; it's safe to leave as
   reference defaults.
5. Optional: swap the primary color, fonts, and radii by editing the
   `:root` CSS variables at the top of `store/static/store/css/style.css`.

No shop name, phone number, image, or color is hard-coded in any template.

## 4. Known prototype limitations (intentional, documented in code)

- **No payment gateway** — orders are recorded with status "New" and the
  store contacts the customer to confirm, per the brief.
- **No delivery tracking** — out of scope per the brief.
- **No geocoding API** — delivery-radius verification relies on the
  customer's own device location (browser Geolocation API) rather than
  converting a typed address into coordinates, since that would require a
  paid third-party API key. The distance check itself is real (Haversine
  formula against the store's configured coordinates), not simulated. See
  `store/utils.py` for the exact reasoning and the clean extension point
  if a geocoding service is added later.
- `DEBUG = True` and a placeholder `SECRET_KEY` in `settings.py` are fine
  for this local prototype/demo but must be changed before any real
  deployment (env-based secret key, `DEBUG = False`, real `ALLOWED_HOSTS`,
  HTTPS).

## 5. Project layout

```
fashion_store/
├── fashion_store/        # project settings, root urls
├── store/
│   ├── models.py         # StoreConfig, Category, Product, Order, OrderItem
│   ├── views.py           # storefront + dashboard views
│   ├── cart.py            # session-based cart
│   ├── utils.py            # Haversine delivery-radius check
│   ├── decorators.py       # staff_required (server-side dashboard auth)
│   ├── forms.py
│   ├── management/commands/seed_demo.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── store/          # public pages
│   │   └── dashboard/       # private owner dashboard
│   └── static/store/{css,js}/
└── requirements.txt
```

## 6. A note on how this was built

This code was written directly (not run/tested in this environment,
since the sandbox that produced it has no network access to install
Django) — see the assistant's final message for the full disclosure and
a checklist of what to verify on first run.
