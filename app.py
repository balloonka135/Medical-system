from flask import Flask, render_template, request, redirect, url_for, flash
from wtforms import Form, FloatField, StringField, IntegerField, DateField, TimeField, validators
import pickle
import sqlite3
import mysql.connector
import os
import numpy as np


app = Flask(__name__)

# prepare the classifier
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
                                    'pkl_objects',
                                    'classifier.pkl'), 'rb'))
# db = os.path.join(cur_dir, 'hospital_db.sqlite')
mydb = mysql.connector.connect(
  host="localhost",
  # host="192.168.203.1",
  user="irina",
  passwd="qwerty123",
  database="projectdb"
)

mycursor = mydb.cursor()


def classify(values):
    label = {0: 'No diabetes', 1: 'Diabetes'}
    X = [values]
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    return label[y], proba


def train(values, y):
    X = [values]
    clf.partial_fit(X, [y])


def insert_doctor_data(*values):
    # conn = sqlite3.connect(path)
    # c = conn.cursor()
    # c.executemany("INSERT INTO hospital (pregnancy, glucose, blood, skin, insulin, bmi, dpf, age)" \
    #    " VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)
    # conn.commit()
    # conn.close()

   sql = "INSERT INTO doctor (name, department, position) VALUES (%s, %s, %s)"
   mycursor.executemany(sql, list(values))
   mydb.commit()


def insert_appoint_data(*values):
    sql = "INSERT INTO appoinment (doctor_id, patient_id, app_date, app_time) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, list(values))
    mydb.commit()

def insert_patient_data(*values):
    sql = "INSERT INTO patient (name, sex, date_of_birth, age, phone_number, address) VALUES (%s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, list(values))
    mydb.commit()

def insert_patient_card_data(*values):
    sql = "INSERT INTO patient_card (patient_id, test_id, diagnosis) VALUES (%s, %s, %s)"
    mycursor.executemany(sql, list(values))
    mydb.commit()

def insert_test_data(*values):
    sql = "INSERT INTO test (patient_id, test_date, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, pregnancies) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, list(values))
    mydb.commit()



# Flask
# class PatientForm(Form):
#     # outdated
#     preg = FloatField('Pregnancies', [validators.InputRequired()])
#     gluc = FloatField('Glucose', [validators.InputRequired()])
#     blood_pr = FloatField('Blood pressure', [validators.InputRequired()])
#     skin_th = FloatField('Skin thickness', [validators.InputRequired()])
#     insul = FloatField('Insulin', [validators.InputRequired()])
#     bmi = FloatField('BMI', [validators.InputRequired()])
#     dpf = FloatField('Diabetes pedigree function', [validators.InputRequired()])
#     age = FloatField('Age', [validators.InputRequired()])



class DoctorForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    department = StringField('Department', [validators.InputRequired()])
    position = StringField('Position', [validators.InputRequired()])


class AppointForm(Form):
    doctor_id = IntegerField('Doctor ID')
    patient_id = IntegerField('Patient ID')
    date_field = DateField('Date')
    time_field = TimeField('Time')


class PatientForm(Form):
    name = StringField('Name', [validators.InputRequired()])
    sex = StringField('Sex', [validators.InputRequired()])
    date_of_birth = DateField('Date of birth')
    age = IntegerField('Age', [validators.InputRequired()])
    phone_number = StringField('Phone number')
    address = StringField('Address', [validators.InputRequired()])


class TestForm(Form):
    patient_id = IntegerField('Patient ID')
    test_date = DateField('Test date')
    gluc = FloatField('Glucose', [validators.InputRequired()])
    blood_pr = FloatField('Blood pressure', [validators.InputRequired()])
    skin_th = FloatField('Skin thickness', [validators.InputRequired()])
    insul = FloatField('Insulin', [validators.InputRequired()])
    bmi = FloatField('BMI', [validators.InputRequired()])
    dpf = FloatField('Diabetes pedigree function', [validators.InputRequired()])

    preg = IntegerField('Pregnancies', [validators.InputRequired()])


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET'])
def result():
    return render_template('create.html')

# function for prediction
# change to correct fields
# @app.route('/results', methods=['GET', 'POST'])
# def results():
#     form = PatientForm(request.form)
#     if request.method == 'POST' and form.validate():
#         preg = request.form['preg']
#         gluc = request.form['gluc']
#         blood_pr = request.form['blood_pr']
#         skin_th = request.form['skin_th']
#         insul = request.form['insul']
#         bmi = request.form['bmi']
#         dpf = request.form['dpf']
#         age = request.form['age']

#         preg = float(preg)
#         gluc = float(gluc)
#         bmi = float(bmi)
#         dpf = float(dpf)

#         params = list([preg, gluc, bmi, dpf])
#         y, proba = classify(params)
#         return render_template('results.html',
#                                content=params,
#                                prediction=y,
#                                probability=round(proba * 100, 2))

#     return render_template('patient_form.html', form=form)


# # change for another form
# @app.route('/put', methods=['GET', 'POST'])
# def put_data():
#     form = PatientForm(request.form)
#     if request.method == 'POST' and form.validate():
#         preg = request.form['preg']
#         gluc = request.form['gluc']
#         blood_pr = request.form['blood_pr']
#         skin_th = request.form['skin_th']
#         insul = request.form['insul']
#         bmi = request.form['bmi']
#         dpf = request.form['dpf']
#         age = request.form['age']
#         params = tuple([preg, gluc, blood_pr, skin_th, insul, bmi, dpf, age])
#         # sqlite_entry(db, params)
#         return render_template('thanks.html')
#     return render_template('patient_form.html', form=form)


@app.route('/input_doctor', methods=['GET', 'POST'])
def input_doctor_data():
    form = DoctorForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        department = request.form['department']
        position = request.form['position']
        params = tuple([name, department, position])
        insert_doctor_data(params)
        # return render_template('create.html')
        return redirect(url_for('result'))
    return render_template('doctor.html', form=form)


@app.route('/input_patient', methods=['GET', 'POST'])
def input_patient_data():
    form = PatientForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        sex = request.form['sex']
        date_birth = request.form['date_birth']
        age = request.form['age']
        phone = request.form['phone']
        address = request.form['address']
        params = tuple([name, sex, date_birth, age, phone, address])
        insert_patient_data(params)
        # return render_template('create.html')
        return redirect(url_for('result'))
    return render_template('new_patient.html', form=form)


@app.route('/input_appoint', methods=['GET', 'POST'])
def input_appoint_data():
    form = AppointForm(request.form)
    if request.method == 'POST' and form.validate():
        doctor = request.form['doctor']
        patient = request.form['patient']
        date_field = request.form['date_field']
        time_field = request.form['time_field']
        params = tuple([doctor, patient, date_field, time_field])
        insert_appoint_data(params)
        # return render_template('create.html')
        return redirect(url_for('result'))
    return render_template('appoinment.html', form=form)


@app.route('/diagnosis', methods=['GET', 'POST'])
def get_diagnosis():
    form = TestForm(request.form)
    if request.method == 'POST' and form.validate():
        patient = request.form['patient']
        test_date = request.form['test_date']
        preg = request.form['preg']
        gluc = request.form['gluc']
        blood_pr = request.form['blood_pr']
        skin_th = request.form['skin_th']
        insul = request.form['insul']
        bmi = request.form['bmi']
        dpf = request.form['dpf']
        params = tuple([patient, test_date, gluc, blood_pr, skin_th, insul, bmi, dpf, preg])

        insert_test_data(params)

        preg = float(preg)
        gluc = float(gluc)
        bmi = float(bmi)
        dpf = float(dpf)

        params = list([preg, gluc, bmi, dpf])
        y, proba = classify(params)

        # retrieve patient id
        params_2 = tuple([patient, mycursor.lastrowid, y])
        insert_patient_card_data(params_2)

        return render_template('create_test.html',
                               content=params,
                               prediction=y,
                               probability=round(proba * 100, 2))
    return render_template('test.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)



# export FLASK_APP=app.py
# export FLASK_DEBUG=1
# export LANG=ru_RU.UTF-8
# export LC_CTYPE=ru_RU.UTF-8
# flask run





















