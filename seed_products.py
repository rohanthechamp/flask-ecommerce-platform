import random
from server import app, db
from models import ProductInformation

CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports"]

def generate_products():
    products = []
    for i in range(1, 51):
        category = random.choice(CATEGORIES)
        mrp = round(random.uniform(50.0, 1000.0), 2)
        discount = round(mrp * random.uniform(0.6, 0.9), 2)  # 10% to 40% discount
        
        products.append({
            "product_name": f"Premium {category} Item {i}",
            "product_info": f"This is a high-quality product belonging to the {category} category. Ideal for daily use.",
            "product_category": category,
            "product_img_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
            "mrp_product_price": mrp,
            "discount_product_price": discount
        })
    return products

if __name__ == "__main__":
    with app.app_context():
        # Check if products already exist to prevent duplicate seeding
        if ProductInformation.query.count() < 50:
            print("Seeding 50 products into the database...")
            for p_data in generate_products():
                product = ProductInformation(**p_data)
                db.session.add(product)
            db.session.commit()
            print("Successfully inserted 50 dummy products!")
        else:
            print("Products already exist in the database. Skipping seed to prevent duplicates.")
