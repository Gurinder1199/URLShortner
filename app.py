from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(3))

    def __init__(self, long, short):
        self.long = long
        self.short = short


@app.before_first_request
def create_tables():
    db.create_all()


# USE THIS INSTEAD
with app.app_context():
    db.create_all()


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters


@app.route('/', methods=['Post', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        # Check for already existing urls
        found_url = Urls.query.filter_by(long=url_received).first()
        if found_url:
            # return short url if found
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            # Create Short URL if not found
            short_url = shorten_url()
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    # return url_received
    else:
        return render_template('home.html')


@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1>URL doesnt exist</h1>'


if __name__ == '__main__':
    app.run(port=5000, debug=True)
