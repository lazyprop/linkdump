from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
db = SQLAlchemy(app)

class LinkForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

@app.route('/')
def index():
    links = Link.query.order_by(Link.timestamp.desc()).all()
    return render_template('index.html', links=links)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = LinkForm()
    if form.validate_on_submit():
        url = form.url.data

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip()
        except Exception as e:
            title = 'Unable to fetch title'
            print(e)
            
        link = Link(title=title, url=url, notes=form.notes.data)
        db.session.add(link)
        db.session.commit()
        flash('Link added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
