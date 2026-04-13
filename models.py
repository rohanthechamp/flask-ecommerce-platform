from datetime import datetime
import pytz
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Boolean
from flask_login import UserMixin
from extensions import db
from sqlalchemy import Enum as SQLEnum


class ProductInformation(db.Model):
    __tablename__ = "product_information"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(250), nullable=False)
    product_info: Mapped[str] = mapped_column(String(550), nullable=False)
    product_category: Mapped[str] = mapped_column(String(250), nullable=False)
    product_img_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="url('../static/assets/img/default_product.jpg')",
    )

    discount_product_price: Mapped[float] = mapped_column(Float, nullable=True)
    mrp_product_price: Mapped[float] = mapped_column(Float, nullable=True)

    # Adding relationship reference to cart items
    cart_items: Mapped[list["CartDatabase"]] = relationship(
        "CartDatabase", back_populates="product"
    )
    # Adding relationship reference to order items
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )

    wishlist: Mapped[list["WishList"]] = relationship(
        "WishList", back_populates="product"
    )

    def __repr__(self):
        return f"Product name is: {self.product_name}"


class UserDatabase(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_oauth_user: Mapped[bool] = mapped_column(Boolean, default=False)  # New field

    def is_password_auth(self):
        return bool(self.password)

    cart_items: Mapped[list["CartDatabase"]] = relationship(
        "CartDatabase", back_populates="customer", cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderDatabase"]] = relationship(
        "OrderDatabase", back_populates="customer", cascade="all, delete-orphan"
    )

    wishlist: Mapped["WishList"] = relationship(
        "WishList",
        uselist=False,
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"User name is: {self.name}"


class CartDatabase(db.Model):  #
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer: Mapped["UserDatabase"] = relationship(
        "UserDatabase", back_populates="cart_items"
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product_information.id"), nullable=False
    )
    product: Mapped["ProductInformation"] = relationship(
        "ProductInformation", back_populates="cart_items"
    )

    def __repr__(self):
        return f"<CartItem id={self.id}, product_id={self.product_id}, qty={self.quantity}>"


KOLKATA_TZ = pytz.timezone("Asia/Kolkata")


def get_current_day_month():
    """Return current day and month as a string (e.g., '06 Feb')."""
    now = datetime.now(KOLKATA_TZ)
    return now.strftime("%Y-%m-%d")


class OrderStatus(Enum):
    PLACED = "Placed"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


class OrderDatabase(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PLACED
    )
    payment_id: Mapped[str] = mapped_column(String(100), nullable=False)
    order_date: Mapped[datetime] = mapped_column(
        String(100), default=get_current_day_month
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer: Mapped["UserDatabase"] = relationship(
        "UserDatabase", back_populates="orders"
    )
    order_total_price: Mapped[float] = mapped_column(Float, nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order id={self.id} status={self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["OrderDatabase"] = relationship(
        "OrderDatabase", back_populates="order_items"
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product_information.id"), nullable=False
    )
    product: Mapped["ProductInformation"] = relationship(
        "ProductInformation", back_populates="order_items"
    )

    def __repr__(self):
        return f"<OrderItem id={self.id}, order_id={self.order_id}, product_id={self.product_id}>"


class WishList(db.Model):
    __tablename__ = "user_wishlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    in_wishlist: Mapped[bool] = mapped_column(Boolean, default=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    customer: Mapped["UserDatabase"] = relationship(
        "UserDatabase", back_populates="wishlist"
    )

    # Adding relationship reference to product items
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product_information.id"), nullable=False
    )
    product: Mapped["ProductInformation"] = relationship(
        "ProductInformation", back_populates="wishlist"
    )

    def __repr__(self):
        return f"Wishlist ID: {self.id}"


class UserShippingAddress(db.Model):
    __tablename__ = "shipping_detail"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    First_Name: Mapped[str] = mapped_column(String(100), nullable=False)
    Last_Name: Mapped[str] = mapped_column(String(100), nullable=False)
    Email: Mapped[str] = mapped_column(String(100), nullable=False)
    Shipping_Address: Mapped[str] = mapped_column(String(500), nullable=False)
    City: Mapped[str] = mapped_column(String(100), nullable=False)
    State: Mapped[str] = mapped_column(String(100), nullable=False)
    Pin_Code: Mapped[int] = mapped_column(Integer, nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<User Name id={self.First_Name}, Email={self.Email}, Shipping_Address={self.Shipping_Address}>"
