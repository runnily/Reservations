import psycopg2
from flask import Flask, session, request, flash, render_template
import os

class StudentClass(object):
    """This class is built to aid the main website, it runs in the back-ground and controll all the actions
    of the user, such as canceling a reservation, reserving, loggin regis-tering all the process are definied in this
    python module."""
    def __init__(self, options):
        """this would intilize the funtion, also here it starts connection with the database"""
        self.options = options #would pass the options here
        self.conn_string = "host='localhost' dbname='ExlExample' us-er='postgres' password='Chimdalu2009'" #A connection string to allow me to connect to the database
        self.conn = psycopg2.connect(self.conn_string) #get a connection if it cannot be retrived an error would arrive here
        self.cursor = self.conn.cursor() #this would return a cursos object so the user can peform queries on the data using this
        self.getOptions() #calls function

    def getOptions(self):
        '''This would validate the option choosen by the program, to ini-tialize the class'''
        if self.options == 'login':
            self.username = str(request.form['username']).upper() #would request the form username in the html 
            self.password = str(request.form['password']) #would request the input from html
            with open('example.txt', 'w') as self.currentUser: #would store the current user later used for when inserting details into database
                self.currentUser.write(self.username)
            return self.username, self.password #returns self.username and self.password to be done again.
        elif self.options == 'reg':
           self.password=request.form['password'] #request the forms from the html
           self.email=request.form['email']
           return self.email, self.password
        elif self.options == 'forget':
           self.email = request.form['email']
           self.username = request.form['username']
           return self.email, self.username
        elif self.options == 'reserve':
           self.time = request.form['time']
           self.date = request.form['date']
           self.amountoftime = request.form['amountoftime'] 
           self.computername = request.form['computer']
           return self.time, self.date, self.amountoftime ,self.computername
        elif self.options == 'cancel':
           self.pin = request.form['pin']
           self.cancel = request.form['cancel']
           print(self.cancel)
           return self.pin, self.cancel
        elif self.options == 'check':
           self.choice = request.form['choice']
           return self.choice
        else:
           pass


    def validateLogin(self):
        '''this would validate whether or not the information given is cor-rect'''
        self.cursor.execute("SELECT * FROM student WHERE username = %s AND  pin = %s ", (self.username, self.password)) #searches database for username and password
        self.records = self.cursor.fetchall() #fetches all
        if self.records: #if empty 
            return True #returns true
        else: #or else it returns false
            return False

    def validateEmail(self):
        #this is used to check if the student is using there exeter college email.
        self.email.strip() #would remove whitespacing
        self.required = 'exe-coll.ac.uk' #this is the string which is re-quired in there email
        if self.required in self.email: #when the string is there...
            return True #true..
        else:
            return False #else false
    def CreateUsername(self):
        #This would create a username for the user
        self.findindex = self.email.index('@') #find the index of @ 
        self.username = self.email[0:self.findindex]
        return self.username
    def addDetails(self):
        self.CreateUsername()
        try: #this would try to inset username into the database, if fails that probaly mean the username already exists. so in a way this is validat-ing the username exsits
            self.cursor.execute("INSERT INTO student(email, pin, username) VALUES (%s, %s, %s)" ,(self.email.upper(), self.password, self.username.upper()))
            self.conn.commit()
            self.cursor.execute("SELECT * FROM student") #testing purposes
            self.records = self.cursor.fetchall()
            print(self.records)
            self.sendDetails(self.email, self.password, self.username)#call function sendDetails
            return True
        except:
            return False
    def sendDetails(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username
        import smtplib
        '''this function here will be used
        to send the users there details'''
        self.emailContent = r"Here's your Details" + "\nPassword: " + self.password + "\nUsername: " + self.username + "\nEmail: " + self.email
        #mail server and port we want to use
        self.mail = smtplib.SMTP('smtp.gmail.com',587) #might change in fu-ture
        #identify me to the server
        self.mail.ehlo()
        #start tls mode add security any smtsp command is going to be erypted because were going to login
        self.mail.starttls()
        self.mail.login('reserve114@gmail.com','passwordispassword')
        self.mail.sendmail('reserve114@gmail.com',self.email, self.emailContent)
        self.mail.close() #closes connection
    def forget(self):
        self.cursor.execute("SELECT * FROM student WHERE username = %s AND  email = %s ", (self.username.upper(), self.email.upper()))
        self.records = self.cursor.fetchall()
        if self.records: #check if records is empty
            self.password = self.records[0][2] #would get user password from database
            self.sendDetails(self.email, self.password,self.username) #send details to user
        else:
            return False #else returns false
    def reserve(self):
        import datetime
        self.cursor.execute("SELECT * FROM reservations WHERE starttime = %s AND  reservationday = %s AND amountoftime = %s AND computername = %s ", (self.time, self.date, self.amountoftime, self.computername.upper()))
        self.records = self.cursor.fetchall()
        print(self.records)
        today = datetime.datetime.now()
        if self.records: #checks to see if its empty
            return False #if not returns false, as the user should not book when there is an already existing reservation
        self.todayDate = str(datetime.date(today.year, today.month, to-day.day))
        self.minTime = str(datetime.time(today.hour, today.minute))
        if self.date == self.todayDate and self.time <= self.minTime:
            return False
        else:
            self.endtime = self.caculateEndtime()
            with open('example.txt', 'r') as self.findUser: #this would get the username of who just logged in
             self.username = self.findUser.read() #saves current user
            self.starttime = self.createStartTime() #gets start time
            self.resNumber = self.createRandomPin() #get random pin
            #add a try here // - if reservation number already exists //username
            self.cursor.execute("INSERT INTO reservations(starttime, end-time, username,  reservationday, amountoftime, computername, reservation-number ) VALUES (%s, %s, %s, %s, %s, %s, %s)" ,(self.starttime, self.endtime, self.username, self.date, self.amountoftime, self.computername.upper(), self.resNumber))
            self.conn.commit()
            self.sendReservation(self.resNumber, self.username)#will send reservation to person
            self.cursor.execute("SELECT * FROM reservations")
            self.records = self.cursor.fetchall() #testing purposes
            print(self.records)
            return True
    def displayComputers(self):
        '''this function is used to display the list of computers from the database into the 
        website template'''
        self.cursor.execute("SELECT computername FROM computers")
        self.computers = self.cursor.fetchall()
        self.computers = [l[0] for l in self.computers] #removes brackets
        return self.computers 
    def createStartTime(self):
        #the form which was used to get the time inputed by the user is currently stored as a string
        #this function is used convert it back into time.
        import datetime
        self.timeHour = int(self.time[0:2]) #converts them into integers
        self.timeMinute = int(self.time[3:5]) #convert into integers
        self.starttime = datetime.time(self.timeHour,self.timeMinute)
        return self.starttime
    def caculateEndtime(self):
        #this function caculated the endtime for the user
        import datetime 
        self.starttime = self.createStartTime()
        self.endtime = datetime.datetime.combine(datetime.date.today(), self.starttime) + datetime.timedelta(minutes=int(self.amountoftime))#combines amount of time to time
        self.endtime = self.endtime.time()
        return self.endtime
    def createRandomPin(self):
       #this function would create a random pin 
       #which the user needs to later on cancel a reservation
       import random 
       self.pin = [] 
       for lengthOfpen in range(5):
        self.pin.append(random.randint(0,9))
       self.pin = '%d%d%d%d%d' % (self.pin[0],self.pin[1],self.pin[2],self.pin[3],self.pin[4])
       return self.pin
   def sendReservation(self, number, username):
       #this function would search the username on the database to find
       #there email, it would then then the reservation number to their email
       #this number would be used to cancel the reservation they have in the future

       self.number = number            #declaring variables here
       self.username = username
       
       self.cursor.execute("SELECT * FROM student WHERE username = '%s'  " % (self.username.upper()), ) 
       self.email = self.cursor.fetchall()                                                #finding the email
       self.email = self.email[0][1]                                                      #which belongs to the  username
       
       '''below I am going to send the email'''

       import smtplib #to send emails
        #login in from google serve to send email
       self.content = 'Hey ' + self.username.lower() + '\nYou recently re-served a computer' + '\nHere is your reservation pin: ' + self.number #con-tents I want to send
        #mail server and port we want to use
       self.mail = smtplib.SMTP('smtp.gmail.com',587) #might change in fu-ture
        #identify your self to the server
       self.mail.ehlo()
        #start tls mode add security any smtsp command is going to be ecryted
        #we login
       self.mail.starttls()
       self.mail.login('reserve114@gmail.com','passwordispassword')
       self.mail.sendmail('reserve114@gmail.com',self.email, self.content)
       self.mail.close() #closes connection

    def showBooking(self):
        #this function here would be used to show
        #the user the reservation they have
        with open('example.txt', 'r') as self.findUser: #this would get the username of who just logged in
            self.username = self.findUser.read()
        self.cursor.execute("SELECT computername FROM reservations WHERE username = '%s'"  % (self.username,))
        self.bookings = self.cursor.fetchall()
        self.bookings = [l[0] for l in self.bookings] #removes brackets
        print(self.bookings)
        return self.bookings
    def validateCancel(self):
        #this function would check if the computer selected corresponds to the pin
        self.cursor.execute("SELECT * FROM reservations WHERE computername = %s AND reservationnumber = %s" , (self.cancel.upper(), self.pin))
        self.valid = self.cursor.fetchall()
        print(self.valid) #this purposes
        if self.valid: #if this is valid
            return True #it retunrs true
        else:
            return False
    def cancelReservation(self):
        #this function deletes the reservation from the pin and tries and then returns true.
        self.cursor.execute("SELECT * from reservations")
        self.records = self.cursor.fetchall()                      #testing purposes
        print(self.records)
        if self.validateCancel():
            self.cursor.execute("DELETE from reservations where reserva-tionnumber = %s;" , (self.pin,))
            self.conn.commit()
            return True
        else:
            return False
    def findAvailable(self):
        #this function is used to find all the availanble computers.
            import datetime
            self.today = datetime.datetime.now()
            self.currentDay = datetime.date(self.today.year, self.today.month, self.today.day)
            ##this function tries to find all the computers which are available
            ##it does this by...
            self.cursor.execute("SELECT computername FROM reservations WHERE reservationday = '%s'" %
                                 (self.currentDay))                  #1) find all the reserveations
            self.reservation = self.cursor.fetchall()
            self.reservation = [l[0] for l in self.reservation] #turns to a list
            self.cursor.execute("SELECT computername FROM inuse") #2) find all the computers in use
            self.inuse = self.cursor.fetchall()
            self.inuse = [l[0] for l in self.inuse] #turns this into the list
            self.notavailable = self.inuse + self.reservation #joins the two list together 
            self.cursor.execute("SELECT computername FROM computers")  #find all the computers in the database
            self.available = self.cursor.fetchall()
            self.available = [l[0] for l in self.available] #turns to a list
            self.results = []
            for a in self.available:
                if a in self.notavailable:         #3) checks where all the computers are in the list not available
                    pass                        #if so it will return false
                else:
                    self.results.append(a)                #else it would append the results into the table
            return self.results

    def validateCheck(self):
        #would get all the computers status
        if self.choice == 'Available':
            self.available = self.findAvailable()
            return self.available

        elif self.choice == 'Reserved':
            #would get all reservations
            self.cursor.execute("SELECT computername FROM reservations")
            self.results = self.cursor.fetchall()
            self.results = [l[0] for l in self.results]
            return self.results
        elif self.choice == 'Inuse':
            #would get all the computers in use
            self.cursor.execute("SELECT computername FROM inuse")
            self.results = self.cursor.fetchall()
            self.results = [l[0] for l in self.results]
            return self.results
        elif self.choice == 'Available and Reserved':
            #would get all the computers where its available
            self.available = self.findAvailable()
            self.cursor.execute("SELECT computername FROM reservations")
            self.reservation = self.cursor.fetchall()
            self.reservation = [l[0] for l in self.reservation]
            self.results = self.reservation + self.available #combines list
            return results
        elif self.choice == 'Available and Inuse':
            self.available = self.findAvailable()
            self.cursor.execute("SELECT computername FROM inuse")
            self.inuse = self.cursor.fetchall()
            self.inuse = [l[0] for l in self.inuse]
            self.results = self.inuse + self.available
            return self.results
        elif self.choice == 'Reserved and Inuse':
            self.cursor.execute("SELECT computername FROM reservations")
            self.reservation = self.cursor.fetchall()
            self.reservation = [l[0] for l in self.reservation]
            self.cursor.execute("SELECT computername FROM inuse")
            self.inuse = self.cursor.fetchall()
            self.inuse = [l[0] for l in self.inuse]
            self.results = self.inuse + self.reservation
            return self.results
        else:
            pass
class computer(StudentClass):

    def getTime(self):
        #get the list of times available
        import datetime
        self.tableTime = [(datetime.time(8,0),),
                     (datetime.time(9,0),),
                     (datetime.time(10,0),),
                     (datetime.time(11,0),),
                     (datetime.time(12,0),),
                     (datetime.time(13,0),),
                     (datetime.time(14,0),),
                     (datetime.time(15,0),),
                     (datetime.time(16,0),)]
        self.GetComputers()
        return self.tableTime
    def GetComputers(self):
        #this function will get the computer from the database
        #it will then turn it into a dictionary
        self.cursor.execute("SELECT computername FROM computers") #executes whats in the table
        self.computers = self.cursor.fetchall() #would fetchall the comput-er within the table
        self.computers = [l[0] for l in self.computers] #would firt turn into a list
        self.computers = {k: v for v, k in enumerate(self.computers)} #woould allow the list into a dictionary
        print(self.computers)
        return self.computers #calls function getComputersTime to add values to the list
  def getComputersTime(self):
        #this would add values to the keys for the dictionary I made
        import datetime
        today = datetime.datetime.now()
        self.currentDate = datetime.date(today.year,today.month,today.day)
        for self.comp in self.computers: #would loop throup each key within the dictionary
            self.cursor.execute("SELECT starttime FROM reservations WHERE computername = '%s' and reservationday = '%s';" %  (self.comp, self.currentDate)) #execute to find start time
            self.reservation = self.cursor.fetchall() #would fetch all the reservations times
    
            self.cursor.execute("SELECT logintime FROM inuse WHERE com-putername = '%s' ;"  % (self.comp)) #find all computers inuse
            self.inuse = self.cursor.fetchall() #contains list of all com-puters in use
            self.computers[self.comp] = self.inuse  + self.reservation #adds the values to the dictionary
        print(self.computers)
        return self.computers #returns dictionary
