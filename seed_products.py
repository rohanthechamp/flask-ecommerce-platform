import random
import uuid

from extensions import db
from models import (
    ProductInformation,
    UserDatabase,
    CartDatabase,
    OrderDatabase,
    OrderItem,
)

class Seeder:

    CATEGORIES = [
        "Electronics", "Home & Kitchen", "Fashion", "Grocery",
        "Beauty", "Books", "Sports & Outdoors", "Toys & Games", "Health"
    ]

    IMAGE_URLS = [f"https://picsum.photos/seed/{i}/500/500" for i in range(1, 51)]

    @classmethod
    def seed_products(cls):
        if ProductInformation.query.count() >= 50:
            print("Products already exist.")
            return

        print("Seeding products...")

        for i in range(50):
            category = random.choice(cls.CATEGORIES)
            mrp = round(random.uniform(100, 2000), 2)
            discount = round(mrp * random.uniform(0.6, 0.9), 2)

            product = ProductInformation(
                product_name=f"{category} Item {i+1}",
                product_info=f"High-quality {category} product.",
                product_category=category,
                product_img_url=cls.IMAGE_URLS[i],
                mrp_product_price=mrp,
                discount_product_price=discount
            )

            db.session.add(product)

        db.session.commit()
        print("Products seeded.")

    @classmethod
    def seed_users(cls):
        if UserDatabase.query.count() >= 5:
            print("Users already exist.")
            return

        print("Seeding users...")

        users = []
        for i in range(5):
            user = UserDatabase(
                email=f"user{i}@test.com",
                password="123456",
                name=f"User {i}",
                is_oauth_user=False
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        print("Users seeded.")
        return users

    @classmethod
    def seed_cart(cls):
        print("Seeding cart...")

        users = UserDatabase.query.all()
        products = ProductInformation.query.all()

        for user in users:
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)

                cart_item = CartDatabase(
                    customer_id=user.id,
                    product_id=product.id,
                    quantity=random.randint(1, 2)
                )

                db.session.add(cart_item)

        db.session.commit()
        print("Cart seeded.")

    @classmethod
    def seed_orders(cls):
        print("Seeding orders...")

        users = UserDatabase.query.all()
        products = ProductInformation.query.all()

        for user in users:
            order_total = 0

            order = OrderDatabase(
                customer_id=user.id,
                payment_id=str(uuid.uuid4()),
                order_total_price=0
            )

            db.session.add(order)
            db.session.flush()  # get order.id

            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                quantity = random.randint(1, 2)
                price = product.discount_product_price * quantity

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price
                )

                order_total += price
                db.session.add(order_item)

            order.order_total_price = order_total

        db.session.commit()
        print("Orders seeded.")

    @classmethod
    def run(cls):
        cls.seed_products()
        cls.seed_users()
        cls.seed_cart()
        cls.seed_orders()


