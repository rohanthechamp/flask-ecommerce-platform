import os
from flask import Blueprint, abort
from models import ProductInformation
from extensions import db
from seed_products import Seeder  # your class we created
from auth import admin_only

seed_bp = Blueprint("seed", __name__)


@seed_bp.route("/seed/<key>", methods=["GET"])
@admin_only
def seed_data(key):

    # prevent duplicate seeding
    if ProductInformation.query.count() >= 50:
        return "Already seeded. Skipping."

    Seeder.run()

    return "Database seeded successfully!"
