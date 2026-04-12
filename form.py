from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    IntegerField,
    PasswordField,
    TextAreaField,
    SelectField,
)


from wtforms.validators import DataRequired, URL, Email, Length
from states_of_india import  INDIAN_STATES


class ProductForm(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired()])
    product_info = TextAreaField("Product_info", validators=[DataRequired()])
    product_img_url = StringField(
        " Product Image URL", validators=[DataRequired(), URL()]
    )
    product_category = StringField("Product Category ", validators=[DataRequired()])
    discount_product_price = StringField(
        "Discount product price", validators=[DataRequired()]
    )
    mrp_product_price = StringField("Product MRP price", validators=[DataRequired()])
    submit = SubmitField("Submit Data")


class SearchProduct(FlaskForm):

    query = StringField("Search Your Product here")
    submit = SubmitField("Submit Data")


class RegisterForm(FlaskForm):
    Name = StringField("Name", validators=[DataRequired()])
    Email = StringField("Email", validators=[DataRequired(), Email()])
    Password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    Email = StringField(label="Email", validators=[DataRequired(), Email()])
    Password = PasswordField(
        label="Password", validators=[DataRequired(), Length(min=8, max=50)]
    )
    submit = SubmitField("Let me in")

class ShippingForm(FlaskForm):
    First_Name = StringField(label="First Name", validators=[DataRequired()])
    Last_Name = StringField(label="Last Name", validators=[DataRequired()])
    Email = StringField(label="Email Address", validators=[DataRequired(), Email()])
    Shipping_Address = TextAreaField(
        label="Shipping Address", validators=[DataRequired()]
    )
    City = StringField(label="City", validators=[DataRequired()])
    State = SelectField(
        "State",
        choices=INDIAN_STATES,
        validators=[],
    )
    Pin_Code = IntegerField(label="Pin Code", validators=[DataRequired()])

    submit = SubmitField("Go Ahead")
