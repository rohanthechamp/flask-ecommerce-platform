# 🛒 Flask E-Commerce Platform

Flask-based full-stack eCommerce application with authentication, Stripe payments, admin dashboard, and order management.

---

## 🚀 Features

- 🛍️ Product listing and detailed views  
- 🛒 Shopping cart and checkout system  
- ❤️ Wishlist functionality  
- 💸 Order placement with Stripe payment integration  
- 🔍 Order tracking system  
- 🔐 User authentication (Email + Google OAuth2)  
- 👨‍💼 Admin dashboard (manage products, users, orders)  
- 🗣️ Customer support system  

---

## 🛠 Tech Stack

- **Backend:** Flask  
- **Database:** PostgreSQL / SQLite  
- **Authentication:** OAuth2 (Google)  
- **Payments:** Stripe API  
- **Caching:** Redis  
- **Frontend:** HTML, CSS, Bootstrap  

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/rohanthechamp/flask-ecommerce-platform.git
cd flask-ecommerce-platform

# create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# install dependencies
pip install -r requirements.txt

# run the app
python app.py
