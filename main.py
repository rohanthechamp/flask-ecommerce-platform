from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    jsonify,
    abort
)
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func
import stripe
import os
from dotenv import load_dotenv
from extensions import db, cache, redis_client
from form import SearchProduct, ShippingForm
from models import (
    ProductInformation,
    CartDatabase,
    OrderDatabase,
    OrderItem,
    UserShippingAddress,
    WishList,
)

main_bp = Blueprint("main", __name__)

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")
OUR_DOMAIN = "http://127.0.0.1:5000"

def get_current_user_cart_items(Database_name, customer_id, item_id):
    try:
        return Database_name.query.filter_by(customer_id=customer_id, product_id=item_id).first()
    except DatabaseError as e:
        return None

def get_all_current_user_database_item(Database_name, user_id):
    try:
        return Database_name.query.filter_by(customer_id=user_id).all()
    except DatabaseError as e:
        return []

def remove_user_item(item_to_remove, location_name):
    if not item_to_remove:
        flash(f"Item not found in {location_name}", "error")
        return False
    try:
        db.session.delete(item_to_remove)
        db.session.commit()
        flash(f"Product removed from {location_name} successfully!", "success")
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while removing item from {location_name}", "error")
        return False

@main_bp.context_processor
def base():
    form = SearchProduct()
    try:
        list_of_category_tuples = db.session.query(ProductInformation.product_category).distinct().all()
        list_of_category = [category[0] for category in list_of_category_tuples]
    except Exception:
        list_of_category = []

    user_cart_items = []
    subtotal_price = 0
    total_price = 0
    if current_user.is_authenticated:
        user_cart_items = get_all_current_user_database_item(CartDatabase, current_user.get_id())
        for cart_item in user_cart_items:
            subtotal_price += cart_item.product.mrp_product_price * cart_item.quantity
            total_price += cart_item.product.discount_product_price * cart_item.quantity

    user_pic = session.get("user_pic")

    return dict(
        form=form,
        list_of_category=list_of_category,
        subtotal_price=round(subtotal_price, 2),
        total_price=round(total_price, 2),
        user_cart_items=user_cart_items,
        user_pic=user_pic,
    )

@main_bp.route("/")
def home_page():
    return render_template("homepage.html")

@main_bp.route("/get_all_items", methods=["GET", "POST"])
@cache.cached(timeout=60, unless=lambda: current_user.is_authenticated, query_string=True)
def get_all_items():
    page = request.args.get("page", 1, type=int)
    per_page = 9
    offset_value = (page - 1) * per_page
    stmt = db.select(ProductInformation).offset(offset_value).limit(per_page)
    items = db.session.execute(stmt).scalars().all()
    total = db.session.execute(db.select(func.count()).select_from(ProductInformation)).scalar()
    return render_template("index.html", all_items=items, page=page, per_page=per_page, total=total)

@main_bp.route("/item/<int:item_id>", methods=["GET", "POST"])
@cache.cached(timeout=60, unless=lambda: current_user.is_authenticated)
def show_item(item_id):
    requested_item = db.get_or_404(ProductInformation, item_id)
    in_wishlist_check = False
    if current_user.is_authenticated:
        existing_item = WishList.query.filter_by(customer_id=current_user.get_id(), product_id=item_id).first()
        in_wishlist_check = existing_item is not None
    return render_template("product_details.html", item_data=requested_item, in_wishlist_check=in_wishlist_check)

@main_bp.route("/search", methods=["GET", "POST"])
def search_product():
    form = SearchProduct()
    user_query = None
    results = None
    if form.validate_on_submit():
        user_query = form.query.data
        results = ProductInformation.query.filter(
            or_(
                ProductInformation.product_name.ilike(f"%{user_query}%"),
                ProductInformation.product_info.ilike(f"%{user_query}%"),
            )
        ).all()
        return render_template("search.html", form=form, results=results, query=user_query)
    return render_template("index.html", form=form, query=user_query)

@main_bp.route("/show_category/<string:category_name>", methods=["GET", "POST"])
@cache.cached(timeout=60, unless=lambda: current_user.is_authenticated)
def show_category(category_name):
    results_category = ProductInformation.query.filter(
        ProductInformation.product_category.ilike(f"%{category_name}%")
    ).all()
    return render_template("category.html", results_category=results_category)

@main_bp.route("/cart/<int:item_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(item_id):
    requested_item_for_cart = db.get_or_404(ProductInformation, item_id)
    existing_item = get_current_user_cart_items(CartDatabase, current_user.get_id(), item_id=item_id)

    if existing_item:
        existing_item.quantity += 1
    else:
        adding_to_cart = CartDatabase(
            quantity=1,
            customer_id=current_user.get_id(),
            product_id=requested_item_for_cart.id,
        )
        db.session.add(adding_to_cart)
        flash("Added in Cart", "success")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return "An error occurred while adding the item to your cart.", 500

    return redirect(request.referrer)

@main_bp.route("/redirect_to_cart")
@login_required
def redirect_to_cart():
    user_cart_items = get_all_current_user_database_item(CartDatabase, current_user.get_id())
    return render_template("cart.html", cart_items=user_cart_items)

@main_bp.route("/wishlist_page")
@login_required
def wishlist_page():
    user_wishlist_items = get_all_current_user_database_item(WishList, current_user.get_id())
    return render_template("wishlist.html", user_wishlist_items=user_wishlist_items)

@main_bp.route("/add_products_wishlist/<int:item_id>", methods=["GET", "POST"])
@login_required
def add_products_wishlist(item_id):
    requested_item_for_cart = db.get_or_404(ProductInformation, item_id)
    adding_to_wishlist = WishList(
        in_wishlist=True,
        customer_id=current_user.get_id(),
        product_id=requested_item_for_cart.id,
    )
    db.session.add(adding_to_wishlist)
    flash("Added to wishlist", "success")
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(request.referrer)

@main_bp.route("/remove_from_wishlist/<int:item_id>", methods=["GET", "POST"])
@login_required
def remove_from_wishlist(item_id):
    item_to_remove = WishList.query.filter_by(customer_id=current_user.get_id(), product_id=item_id).first()
    remove_user_item(item_to_remove, "Wishlist")
    return redirect(request.referrer)

@main_bp.route("/remove_from_cart/<int:item_id>", methods=["GET", "POST"])
@login_required
def remove_from_cart(item_id):
    requested_item_for_cart = db.get_or_404(ProductInformation, item_id)
    item_to_remove = get_current_user_cart_items(CartDatabase, current_user.get_id(), item_id=requested_item_for_cart.id)
    remove_user_item(item_to_remove, "Cart")
    return redirect(request.referrer)

@main_bp.route("/remove_all_items_from_cart", methods=["GET", "POST"])
@login_required
def remove_all_items_from_cart():
    user_cart_items = get_all_current_user_database_item(CartDatabase, current_user.get_id())
    try:
        for items in user_cart_items:
            db.session.delete(items)
        db.session.commit()
        flash("Products Removed from Cart successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while removing items from your cart.", "error")
    return redirect(request.referrer)

@main_bp.route("/decreasing_item_quantity/<int:item_id>", methods=["GET", "POST"])
@login_required
def decreasing_item_quantity(item_id):
    existing_item = get_current_user_cart_items(CartDatabase, current_user.get_id(), item_id=item_id)
    if existing_item and existing_item.quantity > 1:
        existing_item.quantity -= 1
        db.session.commit()
    return redirect(request.referrer)

@main_bp.route("/increasing_item_quantity/<int:item_id>", methods=["GET", "POST"])
@login_required
def increasing_item_quantity(item_id):
    existing_item = get_current_user_cart_items(CartDatabase, current_user.get_id(), item_id=item_id)
    if existing_item:
        existing_item.quantity += 1
        db.session.commit()
    return redirect(request.referrer)

@main_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout_page():
    user_shipping_details = ShippingForm()
    if user_shipping_details.validate_on_submit():
        shipping_details = UserShippingAddress(
            First_Name=user_shipping_details.First_Name.data,
            Last_Name=user_shipping_details.Last_Name.data,
            Email=user_shipping_details.Email.data,
            Shipping_Address=user_shipping_details.Shipping_Address.data,
            City=user_shipping_details.City.data,
            State=user_shipping_details.State.data,
            Pin_Code=user_shipping_details.Pin_Code.data,
            customer_id=current_user.get_id(),
        )
        db.session.add(shipping_details)
        db.session.commit()
        return redirect(url_for("main.create_checkout_session"))
    return render_template("checkout.html", form=user_shipping_details)

@main_bp.route("/cancel_page")
def cancel_page():
    return render_template("cancel.html")

@main_bp.route("/create-checkout-session", methods=["GET", "POST"])
@login_required
def create_checkout_session():
    try:
        user_cart_items = get_all_current_user_database_item(CartDatabase, current_user.get_id())
        line_items = []
        for cart_item in user_cart_items:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": cart_item.product.product_name},
                    "unit_amount": int(cart_item.product.discount_product_price * 100),
                },
                "quantity": cart_item.quantity,
            })
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url=url_for("main.success_page", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=OUR_DOMAIN + "/cancel_page",
            payment_intent_data={"metadata": {"user_id": str(current_user.get_id())}},
        )
        session["payment_intent_id"] = checkout_session.payment_intent
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

def clear_cart_items():
    user_cart_items = CartDatabase.query.filter_by(customer_id=current_user.get_id()).all()
    for item in user_cart_items:
        db.session.delete(item)

@main_bp.route("/success_page")
@login_required
def success_page():
    session_id = request.args.get("session_id")
    if not session_id:
        return redirect(url_for('main.home_page'))
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_id = checkout_session.get("payment_intent")
        if checkout_session.payment_status == "paid":
            user_cart_items = CartDatabase.query.filter_by(customer_id=current_user.get_id()).all()
            total_price = sum((c.product.discount_product_price * c.quantity) for c in user_cart_items)
            user_order_items = [
                OrderItem(quantity=c.quantity, price=c.product.discount_product_price, product_id=c.product.id)
                for c in user_cart_items
            ]
            new_order = OrderDatabase(
                payment_id=payment_id,
                customer_id=current_user.get_id(),
                order_total_price=total_price,
                order_items=user_order_items,
            )
            db.session.add(new_order)
            clear_cart_items()
            db.session.commit()
            return render_template("success.html")
        else:
            return jsonify({"error": "Payment not completed"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

def get_user_order():
    try:
        current_user_id = current_user.get_id()
        user_order_items = (
            OrderDatabase.query.options(
                joinedload(OrderDatabase.order_items).joinedload(OrderItem.product)
            ).filter_by(customer_id=current_user_id).all()
        )
        user_shipping_details = (
            db.session.query(UserShippingAddress)
            .filter_by(customer_id=current_user_id)
            .order_by(UserShippingAddress.id.desc())
            .first()
        )
        return user_order_items, user_shipping_details
    except SQLAlchemyError as e:
        return [], None
    except Exception as e:
        return [], None

@main_bp.route("/process_orders")
@login_required
def process_orders():
    user_order_items, user_shipping_details = get_user_order()
    return render_template("order.html", user_order_items=user_order_items, user_shipping_details=user_shipping_details)

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/contact")
def contact():
    return render_template("contact.html")

@main_bp.errorhandler(404)
@main_bp.errorhandler(DatabaseError)
def page_not_found(e):
    return render_template("404.html"), 404
