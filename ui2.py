from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a more secure key

API_URL = "http://127.0.0.1:8888/submit"


# TODO: generate from Tap class
# TODO: required field
# TODO:
class DataForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    optional_field = StringField("Optional Field", validators=[Optional()])
    choice = SelectField(
        "Choice",
        choices=[
            ("Option1", "Option1"),
            ("Option2", "Option2"),
            ("Option3", "Option3"),
        ],
        validators=[DataRequired()],
    )
    # TODO: somehow the button is overladed on the label
    agree = BooleanField("Agree", validators=[Optional()])
    submit_json = SubmitField("Send POST JSON")
    submit_get = SubmitField("Send GET Request")
    submit_form = SubmitField("Send POST Form")


@app.route("/", methods=["GET", "POST"])
def index():
    form: DataForm = DataForm()
    response_data = None

    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "age": form.age.data,
            "optional_field": form.optional_field.data,
            "choice": form.choice.data,
            "agree": form.agree.data,
        }

        if form.submit_json.data:
            response = requests.post(API_URL, json=data)
        elif form.submit_get.data:
            response = requests.get(API_URL, params=data)
        elif form.submit_form.data:
            response = requests.post(f"{API_URL}-form", data=data)

        if response.ok:
            response_data = response.json()
        else:
            flash("Failed to get response from API", "danger")

    return render_template("index.html", form=form, response_data=response_data)


if __name__ == "__main__":
    app.run(debug=True)
