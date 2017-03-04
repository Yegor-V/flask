from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import time


from credentials import POSTGRES_CREDENTIALS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    positions = db.relationship('Position', backref='department', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Department {}'.format(self.name)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic')
    employees = db.relationship('Employee', backref='position', lazy='dynamic')

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        return 'Position {}'.format(self.name)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    date_opened = db.Column(db.BigInteger, nullable=False)

    def __init__(self, position, date_opened):
        self.position = position
        self.date_opened = date_opened

    def __repr__(self):
        return 'Vacancy for {}'.format(self.position.name)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    email = db.Column(db.String(80))
    phone = db.Column(db.String(80))
    birth_date = db.Column(db.String(80))
    start_work_date = db.Column(db.BigInteger)
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position, start_work_date=None):
        self.name = name
        self.surname = surname
        self.position = position
        if start_work_date is None:
            start_work_date = int(time.time())
        self.start_work_date = start_work_date

    def __repr__(self):
        return 'Employee {} {}'.format(self.name, self.surname)


@app.route('/')
def index():
    all_departments = Department.query.all()
    return render_template('index.html', depts=all_departments)


@app.route('/department/<department_name>')
def department_details(department_name):
    positions = Department.query.filter_by(name=department_name).first().positions
    vacancies = []
    employees = []
    for position in positions:
        vacancies += position.vacancies
        employees += position.employees

    return render_template('department.html', department_name=department_name,
                           positions=positions, vacancies=vacancies, employees=employees)


if __name__ == '__main__':
    app.run()
