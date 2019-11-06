"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import datetime
from StudentClass import *
from wtforms import Form, TextField, TextAreaField, validators, String-Field, SubmitField, DateTimeField, DateField, IntegerField,  validators
from wtforms.fields import DateField, BooleanField
from wtforms_components import DateRange, TimeField
from jinja2 import Template
from flask import Flask, render_template, session, request, flash
import psycopg2
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


conn_string = "host='localhost' dbname='ExlExample' user='postgres' pass-word='Chimdalu2009'" #A connection string to allow me to connect to the da-tabase
conn = psycopg2.connect(conn_string) #get a connection if it cannot be retrived an error would arrive here
cursor = conn.cursor() #this would

@app.route('/') #The first page for the user
def Home():
    """This would be the main home page for the user"""
    return render_template('Homelayout.html') #This would render the home.html onto this design

@app.route("/login")
def home():
    if not session.get('logged_in'): #if not logged in
        return render_template('Loginlayout.html') #it would render this page
    else:
        return main()
 
@app.route('/vlogin', methods=['POST'])
def validate():
    login = StudentClass('login')
    if login.validateLogin():
        session['logged_in'] = True
    else:
        flash('wrong password!') #would make the user repeat to try pass-word a key
    return home() #when this function is finished it would return home function which checks to see if the user is logged in or not.

class ReserveForm(Form):
    computer = TextField('Computer: ',validators=[validators.required()])
    date = DateField(validators=[DateRange(min=datetime.date.today(),max = datetime.date.today() + datetime.timedelta(365),message='not valid date')])
    amountoftime = IntegerField(validators =[validators.NumberRange(min=30,max=80, message ='must be either 30 or 80 minutes')])
    time = TimeField(validators=[DateRange(min= datetime.time(8,0),max= datetime.time(18,0), message ='choose a valid time')])

class RegForm(Form):
    #This class would be used to make the forms for the registry to the site.
    email = TextField('Email:', validators=[validators.required(), valida-tors.Length(min=6, max=35)])
    password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
class LoginForm(Form):
    username = TextField('Username:', validators=[validators.required()])
    email = TextField('Email:', validators=[validators.required(), valida-tors.Length(min=6, max=35)])
class CancelForm(Form):
    cancel = TextField('cancel : ', validators=[validators.required()])
    pin = TextField('Pin :', validators=[validators.required(), valida-tors.Length(min=5)])
class FilterForm(Form):
    choice = TextField('Choice: ',validators=[validators.required()])

@app.route('/reg', methods=['GET', 'POST'])
def register():
    form = RegForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        reg = StudentClass('reg') #would make a new instance with reg which would go through the registery of the class
        '''The function validateEmail would validate the user input to check if they excluded 'exe-coll.ac.uk' into their 
        email address. This function returns a boolean variable depending if the validation if met'''
        if not reg.validateEmail():  #if false
            flash('Error: Please register with your exeter college email') #this would display an error on the html page
        else:
            if form.validate(): #this would validate the forms which were given
                # Save the comment here.
                if reg.addDetails() == False : #would validate if the de-tails exists
                    flash('Error: email appears to already exists ') #would print this on to the site
                else:
                    flash("Thanks for registration") #would return succss when all details are matched.
            else:
                flash('Error: All the form fields are required. ')#when the user fails to give an input
 
    return render_template('Reglayout.html', form=form) #would render this to the screen.
@app.route('/forget', methods = ['GET', 'POST'])
def forget():
    form = LoginForm(request.form)
    if request.method == 'POST':
        forget = StudentClass('forget')
        if form.validate():
            if forget.forget() == False:
                flash('Error: Details provided do not exsists')
            else:
                flash('Your details were sent! ')
        else:
            flash('Error: the form fields are required. ')
    return render_template('Forgetlayout.html', form=form )

@app.route('/reserve', methods = ['GET', 'POST'])
#@login_required("ref='/login'")
def reserve():
    form = ReserveForm(request.form)
    comp = StudentClass('comp')
    computers = comp.displayComputers()

    if request.method == 'POST':
        res = StudentClass('reserve')
        if form.validate():
            if res.reserve() == False:
                flash('Error: This computer appears to be already reserved, or you reservation time is invalid. \n Please try again')
            else: 
                flash('Reserved')
        else:
            flash("Error: %s" % (form.errors))

    return render_template('Reservelayout.html', form=form, comput-ers=computers)

@app.route('/bookings', methods =['GET' , 'POST'])
def bookings():
    form = CancelForm(request.form)
    listOfreservarion = StudentClass('get')
    reservations = listOfreservarion.showBooking()

    if request.method == 'POST':
        cancel = StudentClass('cancel')
        if form.validate():
            if cancel.cancelReservation():
                flash('Canceled !')
            else:
                flash('Error: wrong pin')
        else:
            flash("Error: %s" % (form.errors))

    return render_template('Bookinglayout.html', form=form, reserva-tions=reservations)   

@app.route('/main')
def main():
    avail = computer('avail')
    tableTime = avail.getTime()
    today = datetime.datetime.today()
    date = datetime.date(today.year, today.month, today.day)
    computers = avail.getComputersTime() #holds a dictionary
    return render_template('Mainlayout.html', date=date, tableTime = tab-leTime, computers = computers)

@app.route('/filter', methods = ['GET', 'POST']) #methods of html
def filter():
    form = FilterForm(request.form) #create a new form class
    if request.method == 'POST':
        filter = StudentClass('check')
        if form.validate():
            flash(str(filter.validateCheck()).replace('[','').replace(']',''))
    
    return render_template('Filterlayout.html', form=form)

@app.route("/logout")
def logout(): #this function checks turns the sessions  logged in into false, allowing the user to logout.
    session['logged_in'] = False
    open('example.txt', 'w')
    return Home()

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return Home(), 500

if __name__ == '__main__':
    import os
    app.secret_key = os.urandom(12) #used for the session
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)


