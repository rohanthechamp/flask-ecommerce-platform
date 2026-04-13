import os
from flask import Blueprint, abort,redirect,request
from models import ProductInformation
from extensions import db
from seed_products import Seeder  # your class we created
from auth import admin_only

seed_bp = Blueprint("seed", __name__)


@seed_bp.route("/seed", methods=["GET","POST"])
@admin_only
def seed_data():
    print("Entered in  Already seeded. Skipping.")
    # prevent duplicate seeding
    if ProductInformation.query.count() >= 50:
        print("Already seeded. Skipping.")
        return redirect(request.referrer)

    Seeder.run()

    return "Database seeded successfully!"
