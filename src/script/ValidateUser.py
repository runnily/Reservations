import psycopg2
import datetime 
import socket
import os
import time
import subprocess  
conn_string = "host='localhost' dbname='ExlExample' user='postgres' pass-word='Chimdalu2009'" #A connection string to allow me to connect to the da-tabase
conn = psycopg2.connect(conn_string) #get a connection if it cannot be retrived an error would arrive here
cursor = conn.cursor() #this would return a cursos object so the user can peform queries on the data using this
class validateLogin(object):
    '''A class created to check if the current computer logged in
    is reserved or not. '''
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.today = datetime.datetime.now() #this would get the current date
        print(self.today) 
        self.time = datetime.time(self.today.hour, 0) #this would get the hour of the date
        self.date = datetime.date(self.today.year, self.today.month, self.today.day) #this would store the current date.
        #This will look check if the computer currently being used has a reservation based on the current day and time.
        self.cursor.execute("SELECT * FROM reservations WHERE reserva-tionday = %s AND  starttime = %s AND computername = %s ", (self.date, self.time,socket.gethostname(),  )) #will get all the computer times.

        self.records = cursor.fetchall() #this would store what was fetched into the database.
        
        print(self.records) 

    def checkReserved(self):

        #--this function checks if the tuple is empty or not--#
        #--if its empty it means the computer is currently not reserved--#
        #--if its is it means that the computer is currently reserved--#
        try: #use a try and except as records by empty which would result in an error
            self.starttime = self.records[0][0] #will store the starttime in the database
            print(self.starttime)
            self.endtime = self.records[0][1] #will store the end tme from the database
            print(self.endtime)
            self.username = os.getlogin().upper()  #will get the current user name of the database
            print(self.username)
            self.databaseusername = self.records[0][2] #will get the data-base user name
            print(self.databaseusername)
            #the if statement checks that:
            #and current time is more than starttime but less than end time
            #this means its checking if the starttime is inbetwen both cur-rent date and time
            self.today = datetime.datetime.now()
            if self.starttime <= datetime.time(self.today.hour, self.today.minute) and self.endtime >= datetime.time(self.today.hour, self.today.minute):  
                print('Computer Reserved')
                if self.username == self.databaseusername: #will check if the current user on the computer matches the corresponding username on the database.
                    self.getDate() #a call function to remove expired res-ervations
                    print('correct')
                    return True
                else: 
                    print('incorrect') #when this condition is not met it moves to the if statement which means the wrong user is logged on
                    self.getDate()  #a call function to remove expired res-ervations
                    subprocess.call(["shutdown", "-f", "-r", "-t", "60"]) #this would shut down computer in 60 seconds
                    
            else:
                return False  #would returns false, when start time is not between the current time.
        except:
            return False #when it moves the the exeception statement this conforms that the computer is not reserved

    def createRandomid(self):
       #this function would create a random pin 
       #to create a unique id for the inuse table
       import random 
       self.id = [] 
       for lengthOfid in range(4): #would create a 4 digit pin for used as a primary key for the in use table.
        self.id.append(random.randint(0,9))
       self.id = '%d%d%d%d' % (self.id[0],self.id[1], self.id[2],self.id[3]) #ressagins the key to turn it into a string
       return self.id

    def timeLeft(self):
        #--this function would set a timer to run until it reaches the res-ervation end time where--#
        #--it would close--#
        import time
        if self.checkReserved():
            self.endTime = self.records[0][1] #stored endtime
            self.amountTime = self.records[0][3] #stores amount of time
            self.today = datetime.datetime.now()
            self.cancelRes = str(datetime.time(self.today.hour, 0)) #would store when there reservation has reached the end
            print(self.endTime)
            print(self.amountTime)
            #self.endTime = datetime.datetime.strptime(self.endTime, '%H:%M:%S').time()
            self.now = datetime.datetime.now() #stores the current date

            self.cancelTime = datetime.datetime.combine(self.now.date(), self.endTime) #to cancel the time

            time.sleep((self.cancelTime - self.now).total_seconds()) #would allow the time to terminate the reservation, it basically acts like 
                                                                     #an alarm, which triggers when the reservation time has come to an end.
            self.reservationnumber = self.records[0][6] #would get the res-ervation number
            self.reservationnumber = str(self.reservationnumber) #stores as a string
            self.cursor.execute("DELETE from reservations where reserva-tionnumber = %s;" , (self.reservationnumber,)) #delets from database
            self.conn.commit()
            print('end')
            subprocess.call(["shutdown", "-f", "-s", "-t", "60"]) #would give the user 60's seconds, and then it loggs out
            

        #when the condition is not met it goes to the else statment the else statement does conforms 
        #the computer is not reserved but is in fact currently being used
        #as its 'currently being used' its stored into the inuse table.
        else:
            print('not reserved') 
            self.cursor.execute("INSERT INTO inuse(logintime, computername, id) VALUES (%s, %s, %s)" ,(datetime.time(self.today.hour, self.today.minute), socket.gethostname(), self.createRandomid())) #inserts inuse
            self.conn.commit()
            self.getDate()

    def getDate(self):
    #this would be used to get the date of all the existing reservations within the database, to check if their
    #still valid
        self.cursor.execute("SELECT reservationday FROM reservations") #finds all the reservation dated
        self.dates = self.cursor.fetchall() #would stores what was executed on the database into the variable
        self.dates = [l[0] for l in self.dates] #turns to a list

        self.today = datetime.datetime.now() #stores date now
        self.currentDate = datetime.date(self.today.year, self.today.month, self.today.day)
        for self.date in self.dates: #would validate is the date has ex-pired.
            if self.currentDate > self.date: #compares the dates.
                self.date = str(self.date) #turns into a string
                print(self.date)
                self.cursor.execute("DELETE from reservations where reser-vationday = '%s';" % (self.date)) #allows the expired date to be reserved
                self.conn.commit()

        self.getTime()

    def getTime(self):
        #this function is used to find the end time in computer reserva-tions
        #this function would be used to check and see if the time of a res-ervaton has expired
        self.cursor.execute("SELECT endtime FROM reservations") #select all from end time
        self.times = self.cursor.fetchall() #would fetch all the times
        self.times = [l[0] for l in self.times] #would tuen to a list

        self.today = datetime.datetime.now() #takes the time of day
        self.currentTime = datetime.time(self.today.hour, self.today.minute) #would store the current time 
        self.currentDate = datetime.date(self.today.year, self.today.month, self.today.day) #would store the current date
        for self.time in self.times:
            if self.currentTime > self.time : #if current time is greater than the reserved time then...
                self.time = str(self.time) #turns to string to allow in-dextation
                self.cursor.execute("DELETE from reservations where endtime = '%s' and reservationday ='%s' ;" % (self.time, self.currentDate,)) #de-letes
                self.conn.commit()                                                                                   #ensures all the end time is deleted for that day
                #to update database 
                #should delete the current time which corresponds with


class delete(validateLogin):
#class would be used to delete the current user from their reservation, or current user from their the in-use table.
    def deleteUser(self):
        #this function delete the computer from the inuse table and allows for others to use it.
        #this script will be run when the user tries to shut down
        self.cursor.execute("SELECT * FROM reservations WHERE reserva-tionday = %s AND  starttime = %s AND computername = %s ", (self.date, self.time,socket.gethostname(),  )) #will get all the computer times.
        self.reservationpin = self.cursor.fetchall()
        try: 
            self.reservationpin = self.reservationpin[0][6]
            self.cursor.execute("DELETE from reservations where reserva-tionnumber = %s;" , (self.reservationpin,))
            self.conn.commit()
        except:
            self.cursor.execute("DELETE from inuse where computername = '%s';" % ( socket.gethostname(),))
            self.conn.commit()
        
def runValidateLogin():
    validate = validateLogin(conn, cursor)
    #this function will create an instance and call validate timeleft
    #when timeleft is called the program can then begin to function
    validate.timeLeft()
    recall() #calls upon recall to run a timer


def recall():
    import time
    #this function would allow the program to be ran every 15 minutes to validate the user
    time.sleep(900) #timer to run
    runValidateLogin() #calls runValidatelogin to acts as a loop, allowing the program to be run every 15 minutes.

if __name__ == "__main__":
    runValidateLogin() #starts program
