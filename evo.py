from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import time

from sqlalchemy.exc import DataError, IntegrityError

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY
from utils import to_timestamp

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


def get_department_vacancies(department_id):
    return [get_object_dict(v) for v in Vacancy.query.filter_by(department_id=department_id)]


def get_department_employees(department_id):
    return [get_object_dict(e) for e in Employee.query.filter_by(department_id=department_id)]


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
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    email = db.Column(db.String(DATABASE_STRING_LENGTH))
    phone = db.Column(db.String(DATABASE_STRING_LENGTH))
    birth_date = db.Column(db.String(DATABASE_STRING_LENGTH))
    start_work_date = db.Column(db.BigInteger)
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position_id, department_id,
                 email=None, phone=None, birth_date=None,
                 start_work_date=int(time.time()), is_department_leader=False):
        self.name = name
        self.surname = surname
        self.position_id = position_id
        self.department_id = department_id
        self.email = email
        self.phone = phone
        self.birth_date = birth_date
        self.start_work_date = start_work_date
        self.is_department_leader = is_department_leader

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
        department_id = request.form.get('id')
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
        :return: All vacancies json of current department. department id is needed in request.
        """
        department_id = request.args.get('department_id')
        if not department_id:
            return {'error': 'department_id id required'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                else:
                    return get_department_vacancies(department_id)
            except DataError:
                return {'error': 'department_id must be int'}, 400

    @staticmethod
    def post():
        """
        Opens vacancy in current department. department_id and position_id are needed.
        date_opened is optional (defaults to now)
        :return: success/error json
        """
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')
        date_opened = request.form.get('date_opened')

        if not position_id or not department_id:
            return {'error': 'position_id and department_id required'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                position = Position.query.filter_by(id=position_id).first()
            except DataError:
                return {'error': 'department_id and position_id must be ints'}, 400

            if not department or not position:
                return {'error': 'department or position not found'}, 404

            else:
                if date_opened:
                    try:
                        date_opened = to_timestamp(date_opened)
                        vacancy = Vacancy(department_id=department_id, position_id=position_id, date_opened=date_opened)
                    except ValueError:
                        return {'error': 'date_opened must be in format mm/dd/yyyy'}, 400
                else:
                    vacancy = Vacancy(department_id=department_id, position_id=position_id)
                db.session.add(vacancy)
                db.session.commit()
                return {
                    'success': 'vacancy created',
                    'vacancy': {
                        'id': vacancy.id, 'department_id': vacancy.department_id, 'date_opened': vacancy.date_opened,
                        'position': {'id': vacancy.position.id, 'name': vacancy.position.name}
                    }
                }

    @staticmethod
    def patch():
        """
        Updates vacancy data.
        :return: success/error json
        """
        vacancy_id = request.form.get('vacancy_id')
        new_department_id = request.form.get('new_department_id')
        new_position_id = request.form.get('new_position_id')
        new_date_opened = request.form.get('new_date_opened')

        if not vacancy_id or not all((new_department_id, new_position_id, new_date_opened)):
            return {
                'error': 'vacancy_id and at least one of new_department_id, new_position_id, new_date_opened needed'
            }, 400
        else:
            try:
                vacancy = Vacancy.query.filter_by(id=vacancy_id).first()
                if not vacancy:
                    return {'error': 'vacancy not found'}, 404
                if new_department_id:
                    vacancy.department_id = new_department_id
                if new_position_id:
                    vacancy.position_id = new_position_id
                if new_date_opened:
                    try:
                        vacancy.date_opened = to_timestamp(new_date_opened)
                    except ValueError:
                        return {'error': 'date_opened must be in format mm/dd/yyyy'}, 400
                db.session.add(vacancy)
                db.session.commit()
                return {
                    'success': 'vacancy updated',
                    'vacancy': {
                        'id': vacancy.id,
                        'date_opened': vacancy.date_opened,
                        'department': {'id': vacancy.department_id, 'name': vacancy.department.name},
                        'position': {'id': vacancy.position_id, 'name': vacancy.position.name}
                    }
                }
            except (DataError, IntegrityError):
                return {'error': 'bad department_id, position_id, vacancy_id'}

    @staticmethod
    def delete():
        """
        Deletes (closes) vacancy.
        :return: success/error json
        """
        vacancy_id = request.form.get('vacancy_id')
        if not vacancy_id:
            return {'error': 'vacancy_id is required'}, 400
        else:
            try:
                vacancy = Vacancy.query.filter_by(id=vacancy_id).first()
                if not vacancy:
                    return {'error': 'vacancy with specified id not found'}, 404
                else:
                    db.session.delete(vacancy)
                    db.session.commit()
                    return {'success': 'vacancy deleted'}
            except DataError:
                return {'error': 'vacancy_id must be string'}, 400


class EmployeeApi(Resource):
    @staticmethod
    def get():
        """
        :return: All employees of current department json. Needs department_id parameter.
        """
        department_id = request.args.get('department_id')
        employee_id = request.args.get('employee_id')

        if not department_id and not employee_id:
            return {'error': 'department_id or/and employee_id is required'}, 400

        if employee_id:
            try:
                employee = Employee.query.filter_by(id=employee_id).first()
                if not employee:
                    return {'error': 'employee with specified employee_id not found'}, 404
                else:
                    return get_object_dict(employee)
            except DataError:
                return {'error': 'employee_id must be a string'}, 400

        elif department_id:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                else:
                    return get_department_employees(department_id)
            except DataError:
                return {'error': 'department_id must be a string'}, 400

    @staticmethod
    def post():
        """
        Creates new db instance of Employee. position_id, department_id, name and surname args are needed.
        Other info (email, phone, birth_date, start_work_date and is_department_leader) is optional.
        If start_work_date is not set -> will be set to now.
        If is_department_leader is not set -> will be set to False.
        :return: success/error json
        """
        position_id = request.form.get('position_id')
        department_id = request.form.get('department_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        birth_date = request.form.get('birth_date')
        start_work_date = request.form.get('start_work_date')
        is_department_leader = request.form.get('is_department_leader')

        if not all((position_id, department_id, name, surname)):
            return {'error': 'position_id, department_id, name, surname required'}, 400
        else:
            try:
                employee = Employee(position_id=position_id, department_id=department_id, name=name, surname=surname,
                                    email=email, phone=phone, birth_date=birth_date, start_work_date=start_work_date,
                                    is_department_leader=is_department_leader)
                db.session.add(employee)
                db.session.commit()
            except Exception as e:
                return {'error': 'failed to create employee: {}'.format(e)}

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
        employee_id = request.form.get('employee_id')
        if not employee_id:
            return {'error': 'employee_id is required'}, 400
        else:
            try:
                employee = Employee.query.filter_by(id=employee_id).first()
                if not employee:
                    return {'error': 'employee with specified id not found'}, 404
                else:
                    db.session.delete(employee)
                    db.session.commit()
                    return {'success': 'employee deleted'}
            except DataError:
                return {'error': 'employee_id must be string'}, 400


api.add_resource(DepartmentApi, '/api/department/')
api.add_resource(PositionApi, '/api/position/')
api.add_resource(VacancyApi, '/api/vacancy/')
api.add_resource(EmployeeApi, '/api/employee/')


if __name__ == '__main__':
    app.run(debug=True)
