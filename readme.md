# 🛒 BennSryaStore

## 💡 About

**BennSryaStore** is a simple e-commerce web application built with **Django** that sells **digital products** such as mobile top-ups, data packages, game vouchers, e-money, electricity tokens, and more.
The system is integrated with the **Digiflazz API**, allowing automatic product synchronization and real-time transaction processing.

---

## 🚀 Key Features

### 👥 User (Customer)

* 🔐 **Register & Login** (with password validation — minimum 8 characters)
* 🛍️ **Browse products and variants** (data fetched from Digiflazz)
* 💳 **Create orders & upload payment proof**
* 🧾 **View transaction history**
* 👤 **Manage user profile**

### 🧑‍💼 Admin

* 📊 **Admin Dashboard** showing total users, orders, products, and 7-day transaction charts
* 🔄 **Sync product list directly from Digiflazz API**
* 🧾 **Confirm payments & send orders to Digiflazz**
* 🧹 **Auto-delete unavailable variants/products**

---

## ⚙️ Tech Stack

| Layer               | Technology                                  |
| ------------------- | ------------------------------------------- |
| **Backend**         | Django 5.x                                  |
| **Database**        | SQLite (can be changed to PostgreSQL/MySQL) |
| **Frontend**        | HTML + CSS (Bootstrap or Tailwind)          |
| **API Integration** | Digiflazz API                               |
| **Authentication**  | Django Auth System                          |
| **Hosting**         | Docker, Render, Railway, or VPS             |

---

## 📂 Project Structure (Simplified)

```
BennSryaStore/
├── store/
│   ├── models.py              # Product, ProductVariant, and Order models
│   ├── views.py               # Core business logic
│   ├── urls.py
│   ├── templates/
│   │   ├── store/
│   │   │   ├── index.html
│   │   │   ├── product_detail.html
│   │   │   ├── payment_page.html
│   │   │   ├── admin_dashboard.html
│   │   │   └── profile.html
│   │   └── registration/
│   │       ├── login.html
│   │       └── register.html
│   ├── static/
│   │   └── store/img/hero.png
│   └── helpers/forms_mapping.py  # Field mapping & brand logos
├── BennSryaStore/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── .env
```

---

## 🔑 `.env` Configuration

Create a `.env` file in the project root with the following variables:

```bash
DEBUG=True
SECRET_KEY=django-insecure-your_secret_here
ALLOWED_HOSTS=*

DIGIFLAZZ_USERNAME=your_username
DIGIFLAZZ_API_KEY=your_api_key
DIGIFLAZZ_SIGN=md5(username + api_key + 'pricelist')
```

---

## 🧰 Local Setup Guide

1. **Clone the repository**

   ```bash
   git clone https://github.com/BenSurya888/BennSryaStore.git
   cd BennSryaStore
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create an admin account**

   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**

   ```bash
   python manage.py runserver
   ```

7. **Open the app**

   ```
   http://127.0.0.1:8000/
   ```

---

## ⚙️ How the System Works

### 1️⃣ Product Synchronization

Admins can call the `/admin/sync-products/` endpoint to:

* Fetch all product data from the Digiflazz API
* Automatically create or update products & variants in the database
* Apply markup pricing dynamically for resale

---

### 2️⃣ Product Display

Users browse the homepage (`index.html`) to view products grouped by category and brand.
Brand logos are mapped automatically via `helpers/forms_mapping.py`.

---

### 3️⃣ Placing an Order

Users:

* Select a product variant
* Enter required details (e.g., phone number or game ID)
* Create an order → status becomes **pending**
* Redirected to the **payment page** to upload proof of transfer

---

### 4️⃣ Payment Upload

Users upload payment proof (bank transfer, e-wallet, or QRIS).
Status remains **pending** until confirmed by an admin.

---

### 5️⃣ Admin Confirmation & Digiflazz Order

From the **Admin Dashboard**, the admin:

* Marks order as **paid**
* The system automatically:

  * Generates a unique `ref_id`
  * Computes the Digiflazz `sign` (MD5 hash)
  * Sends an order request to Digiflazz `/v1/transaction`
  * Saves and updates the order status (`success`, `failed`, or `pending`)

---

### 6️⃣ Checking Order Status

The system can query Digiflazz by calling:

```
/check-status/<ref_id>/
```

It will automatically update the local order status based on Digiflazz response.

---

## 🧾 Key Internal Endpoints

| Endpoint                  | Method   | Description                  |
| ------------------------- | -------- | ---------------------------- |
| `/sync-products/`         | GET      | Sync products from Digiflazz |
| `/create-order/`          | POST     | Create new order             |
| `/payment/<order_id>/`    | GET/POST | Upload payment proof         |
| `/check-status/<ref_id>/` | GET      | Check transaction status     |
| `/search-products-api/`   | GET      | AJAX product search          |
| `/transaction-history/`   | GET      | User transaction history     |
| `/admin-dashboard/`       | GET      | Admin panel with statistics  |

---

## 📊 Admin Dashboard

Displays:

* Total users, products, and orders
* Pending order count
* 10 most recent orders
* 7-day order graph (using Chart.js)
* Admin actions to confirm or update order statuses

---

## 🐳 Docker Deployment (Optional)

If your project includes Docker configuration files, simply run:

```bash
docker compose up --build
```

This will build the image and run Django automatically.

---

## 🧠 Additional Notes

* All Digiflazz API integrations are handled inside `views.py`.
* Input validation for customer IDs, emails, and servers is defined in `forms_mapping.py`.
* Product prices include a random markup for more realistic resale pricing.
* Templates are modular and can be customized easily under `/templates/store/`.

---

## 💬 Credits

Developed by **BenSurya**
GitHub: [@BenSurya888](https://github.com/BenSurya888)

---
