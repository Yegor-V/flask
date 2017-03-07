from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import time

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY
from utils import get_object_dict

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)
api = Api(app)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vacancies = db.relationship('Vacancy', backref='department', lazy='dynamic', cascade='delete')
    employees = db.relationship('Employee', backref='department', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Department {}'.format(self.name)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Position {}'.format(self.name)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_opened = db.Column(db.BigInteger, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, position_id, department_id, date_opened=None):
        self.position_id = position_id
        self.department_id = department_id
        if date_opened is None:
            date_opened = int(time.time())
        self.date_opened = date_opened

    def __repr__(self):
        return 'Vacancy for {}'.format(self.position.name)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    birth_date = db.Column(db.String(50))
    start_work_date = db.Column(db.BigInteger)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position_id, department_id):
        self.name = name
        self.surname = surname
        self.position_id = position_id
        self.department_id = department_id
        self.start_work_date = int(time.time())

    def __repr__(self):
        return 'Employee {} {}'.format(self.name, self.surname)


@app.route('/')
def company():
    return render_template('company.html')


@app.route('/department/<department_name>')
def department(department_name):
    return render_template('department.html', department_name=department_name)


@app.route('/employee/<employee_id>')
def employee(employee_id):
    return render_template('employee.html', employee_id=employee_id)


class CompanyApi(Resource):
    def get(self):
        """
        :return: All data for company template: all departments and all positions info
        """
        departments = [get_object_dict(d) for d in Department.query.all()]
        positions = [get_object_dict(p) for p in Position.query.all()]
        return jsonify({'company_name': 'Evo', 'departments': departments, 'positions': positions})


class DepartmentApi(Resource):
    pass


class EmployeeApi(Resource):
    pass


api.add_resource(CompanyApi, '/api/company/')
api.add_resource(DepartmentApi, '/api/department/')
api.add_resource(EmployeeApi, '/api/employee/')


if __name__ == '__main__':
    app.run(debug=True)
