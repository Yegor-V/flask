from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import time

from sqlalchemy.exc import DataError, IntegrityError

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)
api = Api(app)

COMPANY_NAME = 'RANDOM'
DATABASE_STRING_LENGTH = 50


def get_object_dict(table_row_object):
    table_row_dict = table_row_object.__dict__
    del table_row_dict['_sa_instance_state']
    return table_row_dict


def get_all_positions():
    return [get_object_dict(p) for p in Position.query.all()]


def get_all_departments():
    return [get_object_dict(d) for d in Department.query.all()]


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DATABASE_STRING_LENGTH), unique=True, nullable=False)
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
    name = db.Column(db.String(DATABASE_STRING_LENGTH), unique=True, nullable=False)
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
    name = db.Column(db.String(DATABASE_STRING_LENGTH), nullable=False)
    surname = db.Column(db.String(DATABASE_STRING_LENGTH), nullable=False)
    email = db.Column(db.String(DATABASE_STRING_LENGTH))
    phone = db.Column(db.String(DATABASE_STRING_LENGTH))
    birth_date = db.Column(db.String(DATABASE_STRING_LENGTH))
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
def company_view():
    return render_template('company.html', company_name=COMPANY_NAME)


@app.route('/department/<department_name>')
def department_view(department_name):
    return render_template('department.html', department_name=department_name)


@app.route('/employee/<employee_id>')
def employee_view(employee_id):
    return render_template('employee.html', employee_id=employee_id)


class DepartmentApi(Resource):
    @staticmethod
    def get():
        """
        :return: All departments json or particular department details if id is specified
        """
        department_id = request.args.get('department_id')
        if not department_id:
            return get_all_departments()
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                return {'error': 'department not found'}, 404 if not department else get_object_dict(department)
            except DataError:
                return {'error': 'department_id must be a number'}, 400

    @staticmethod
    def post():
        """
        Saves new department to db. name and description are needed. Name is unique.
        :return: success/error json
        """
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            return {'error': 'name and description required'}, 400
        elif len(name) > DATABASE_STRING_LENGTH or len(description) > DATABASE_STRING_LENGTH:
            return {'error': 'name and description must not be longer then {} symbols'.format(
                DATABASE_STRING_LENGTH)}, 400
        else:
            try:
                department = Department(name=name, description=description)
                db.session.add(department)
                db.session.commit()
                return {'success': 'department created', 'department': {
                    'name': department.name, 'id': department.id, 'description': department.description}}, 201
            except IntegrityError:
                return {'error': 'department with this name already exists'}, 400

    @staticmethod
    def patch():
        """
        Updates department name/description. department_id is needed.
        :return: success/error json
        """
        department_id = request.form.get('department_id')
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
        if not department_id:
            return {'error': 'department_id is required'}, 400
        elif not new_name and not new_description:
            return {'error': 'at least one of new_name and new_description needed'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                if new_name:
                    department.name = new_name
                if new_description:
                    department.description = new_description
                db.session.commit()
                return {'success': 'department updated successfully'}

            except DataError:
                return {'error': 'department_id must be string'}, 400

    @staticmethod
    def delete():
        """
        Deletes department. department_id is needed.
        :return: success/error json
        """
        department_id = request.form.get('department_id')
        if not department_id:
            return {'error': 'department_id is required'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                else:
                    db.session.delete(department)
                    db.session.commit()
                    return {'success': 'department deleted'}
            except DataError:
                return {'error': 'department_id must be string'}, 400


class PositionApi(Resource):
    @staticmethod
    def get():
        """
        :return: All positions json (needed on company page when adding/deleting/editing position)
        """
        return get_all_positions()

    @staticmethod
    def post():
        """
        Saves new position to db. name and description are needed. Name is unique.
        :return: success/error json
        """
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            return {'error': 'name and description required'}, 400
        elif len(name) > DATABASE_STRING_LENGTH or len(description) > DATABASE_STRING_LENGTH:
            return {'error': 'name and description must not be longer then {} symbols'.format(
                DATABASE_STRING_LENGTH)}, 400
        else:
            try:
                position = Position(name=name, description=description)
                db.session.add(position)
                db.session.commit()
                return {'success': 'position created'}, 201
            except IntegrityError:
                return {'error': 'position with this name already exists'}, 400

    @staticmethod
    def patch():
        """
        Updates position name/description.
        :return: success/error json
        """
        position_id = request.form.get('position_id')
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
        if not position_id:
            return {'error': 'position_id is required'}, 400
        elif not new_name and not new_description:
            return {'error': 'at least one of new_name and new_description needed'}, 400
        else:
            try:
                position = Position.query.filter_by(id=position_id).first()
                if not position:
                    return {'error': 'position with specified id not found'}, 404
                if new_name:
                    position.name = new_name
                if new_description:
                    position.description = new_description
                db.session.commit()
                return {'success': 'position updated'}

            except DataError:
                return {'error': 'position_id must be string'}, 400

    @staticmethod
    def delete():
        """
        Deletes position.
        :return: success/error json
        """
        position_id = request.form.get('position_id')
        if not position_id:
            return {'error': 'position_id is required'}, 400
        else:
            try:
                position = Department.query.filter_by(id=position_id).first()
                if not position:
                    return {'error': 'position with specified id not found'}, 404
                else:
                    db.session.delete(position)
                    db.session.commit()
                    return {'success': 'position deleted'}
            except DataError:
                return {'error': 'position_id must be string'}, 400


class VacancyApi(Resource):
    @staticmethod
    def get():
        """
        :return: All vacancies json of current department. department name is needed in request.
        """
        raise NotImplementedError

    @staticmethod
    def post():
        """
        Opens vacancy in current department. department_id and position_id are needed.
        date_opened is optional (defaults to now)
        :return: success/error json
        """
        raise NotImplementedError

    @staticmethod
    def patch():
        """
        Updates vacancy data.
        :return: success/error json
        """
        raise NotImplementedError

    @staticmethod
    def delete():
        """
        Deletes (closes) vacancy.
        :return: success/error json
        """
        raise NotImplementedError


class EmployeeApi(Resource):
    @staticmethod
    def get():
        """
        :return: All employees of current department json. Needs department_name parameter.
        """
        raise NotImplementedError

    @staticmethod
    def post():
        """
        Creates new db instance of Employee. position_id, department_id, name and surname args are needed.
        Other info (email, phone, birth_date, start_work_date and is_department_leader) is optional.
        If start_work_date is not set -> will be set to now.
        If is_department_leader is not set -> will be set to False.
        :return: success/error json
        """
        raise NotImplementedError

    @staticmethod
    def patch():
        """
        Updates employee's personal info.
        Just gets all updated info from request data and updates table row.
        :return: success/error json
        """
        raise NotImplementedError

    @staticmethod
    def delete():
        """
        Deletes employee. Needs employee_id in request. ("FIRE" button)
        :return: success/error json
        """
        raise NotImplementedError


api.add_resource(DepartmentApi, '/api/department/')
api.add_resource(PositionApi, '/api/position/')
api.add_resource(VacancyApi, '/api/vacancy/')
api.add_resource(EmployeeApi, '/api/employee/')


if __name__ == '__main__':
    app.run(debug=True)
