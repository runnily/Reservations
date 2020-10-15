from tkinter import *
import psycopg2
import platform
import tkinter.messagebox as box
import socket #would be use later to get computer name
from tkinter.ttk import * #extra for layout


class Accesssystem(object): 
    '''A class which will allow the staff to enter 
            the system and view the amount of computers
                available'''

    LABEL_TEXT = [
        "Click here!",
        "Welcome.",
        "You can remove a computer which is faulty.",  #An arrray to be used for later 
        "And add new computers",
        "However you must login to do that.",]


    def __init__(self, master, connection, cursor):
        '''connection strings to inilize '''
        self.master = master
        self.connection = connection #Added extra attributes
        self.cursor = cursor #connection



        master.title("Exeter College|Maths and Science") #defines the title
        self.master.geometry("1600x800") #Geomtry of screen is set, to al-low it to be full screen

        '''I am going to create a label frame to allow the password inside it'''
        self.Main = LabelFrame(self.master, text= 'Enter password: ', width = 100)
        self.Main.pack(pady=250)

        #this would create a drop down menu
        self.VarAbout = StringVar(self.master)
        self.DropChoices = {'','About','Help','Forgot Password'}
        self.VarAbout.set('Help') 
        self.popUpMenu = OptionMenu(self.master, self.VarAbout, *self.DropChoices)
        self.popUpMenu.pack()
        self.VarAbout.trace('w', self.change_dropdown)

        #for wrap around
        self.label_index = 0
        self.label_text = StringVar()
        self.label_text.set(self.LABEL_TEXT[self.label_index])
        self.label = Label(self.Main, textvariable=self.label_text)
        self.label.bind("<Button-1>", self.cycle_label_text)
        self.label.pack()

        self.entryPass = Entry(self.Main) #Create an Entry Button for pass-word
        self.loginBtn = Button(self.Main, text= 'Enter', command = self.access)
        self.loginBtn.pack()
        self.entryPass.pack()

    def change_dropdown(self, *args):
        '''this functions looks at the what the user choosen
        in the option value to determine the message box to display'''

        if self.VarAbout.get() == 'About':
            box.showinfo('About' , 'This program allows you to add and re-move computers')
        if self.VarAbout.get() == 'Help':
            box.showinfo('Help' , 'To add computers selects the add button located on the Add computer tab. To remove a computer first select a com-puter from the list, then click on the remove tab  then select the remove button')
        if self.VarAbout.get() == 'Forgot Password':
            box.showinfo('Forgot passowrd' , 'Address the admin, to gain access')

    def cycle_label_text(self, event):
        '''this function is to wrap around the function'''
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT) # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])

    def access(self):
        '''this is to read from the file to get password
        required to enter the software'''
        with open('Password.txt', 'r') as self.pinFile:
            self.password = self.pinFile.read()
        print(self.password)
        self.Validate() #Calls the validate function in order the input which was entered

    def Validate(self):
        '''this would test the password which the user has input in'''
        if self.entryPass.get() == self.password :
            box.showinfo('Correct Password', 'Welcome')
            self.Main.pack_forget()
            self.displayComputers()
        else:
            box.showwarning('Incorrect Password','Incorrect Pin, Please Try Again ')  
    def displayComputers(self):
        '''this would display list of computers
        available'''
   
        self.ListFrame = LabelFrame(self.master, text = 'List of computers: ')
        self.ListFrame.pack()

        self.listOfComputers = Listbox(self.ListFrame, width = 220)

        self.listOfComputers.grid(row = 0)#place at centre

        self.OpenListOfComputers() 

    def ButtonsMapWindows(self):
        '''this function would display the buttons and map label frame'''

        #I am creating a note book for the add and label buttons

        self.edit = Notebook(self.master, width = 700, height = 600)
        self.addPage = Frame(self.edit) #this would create an add tab
        self.removePage = Frame(self.edit) #this would create an remove tab
        self.edit.add(self.addPage, text = 'Add Computer') #will add page to function
        self.edit.add(self.removePage, text = 'Remove Computer')
        self.edit.pack(side = RIGHT) #will keep it to the right

        '''here I am adding my widgets on to the add page'''

        self.labelAdd = Label(self.addPage, text = 'Click button to add a computer')
        self.addBtn = Button(self.addPage,text='Add' , command= self.createFile)

        self.labelAdd.pack()
                               #Packing widgets
        self.addBtn.pack()

        '''Creating widgits to add to the remove page'''
        self.labelRemove = Label(self.removePage,text='Click button to re-move a computer \n *Remember to select on the list first')
        self.RemoveBtn = Button(self.removePage,text='Remove' , command= self.checkEmpty)

        self.labelRemove.pack()
                                #placing widgts
        self.RemoveBtn.pack()

        '''code below will allow a picture to be shown'''

        self.Map = LabelFrame(self.master, text = 'Locations of computers')
                                            #allow a frame to display
        self.Map.pack(side = RIGHT)

        self.hubMap = PhotoImage(file = 'map.gif')
        
        self.canvas = Canvas(self.Map, width=700, height=600)

        # put gif image on canvas
        self.canvas.create_image(0, 0, image= self.hubMap ,anchor=NW)

        # pack the canvas into a frame/form

        self.canvas.pack()
    def OpenListOfComputers(self):
        '''creates a cvs file and writes the contents of the 
        database into the file'''
        with open('getComputers.csv', 'w') as self.file:
            self.cursor.copy_to(self.file , 'computers' , sep=' ')#will copy contents of database of table computers in this file
                                                                  #seperat-ed by ' '
        self.createListBox() #this functions would be called to read from the file, and create a list of computers

    def createListBox(self):
        '''this will create a loop which will insert the contents from the file
        into the database'''
        self.listPosistion = 0
        with open('getComputers.csv', 'r') as self.file: #opens file to READ contents
            for self.line in self.file: #loops over each line
                self.listPosistion = self.listPosistion + 1 #add one to po-sistion
                self.listOfComputers.insert(self.listPosistion , self.line) #insert data into the list box
        self.ButtonsMapWindows()
        return self.listPosistion

    def createFile(self):
        '''would create a new csv file and write into it
        this is to prepare the database to read from the file,
        as it would need these header'''
        '''this file is used later on when the computer is adding new com-puters to the database,
        in which is for the listbox to display the new value'''
        with open('data.csv', 'w') as file: #when this is called it overi-des file.
            file.write('computerName,location,sys')
            #self.connection.commit() #add this later to commit
        self.addComputersWindow()

        #-----------------next code below is for adding computers------------------#
    def addComputersWindow(self):
        '''this would create another window (child window)
        and this would also create a list box'''
        self.addComputer = Toplevel() #To create a child window
        self.addComputer.title('Computers')
        self.addComputer.geometry("400x400") #set size

        '''adding 3 frames for the child window
        these will be to keep the entries within the frame'''

        self.computerNameFrame = Frame(self.addComputer)
        self.locationFrame = Frame(self.addComputer)
        self.sysFrame = Frame(self.addComputer)

        '''This label will appear at the end'''
        self.labelDone = Label(self.addComputer, text = 'Computer Added!')

        for inputs in range(3): #this would allow repeat to ask 4 questions
            if inputs in [0]: #ask for first input when inputs is 0
                self.computerName = Entry(self.computerNameFrame)
                self.computerNameLabel = Label(self.computerNameFrame , text = 'Input Computer name: \nThe defaul the name for this computer is al-ready inserted \nIf this is not the correct name please change')
                self.computerName.insert(END, socket.gethostname())
                self.computerName.pack()
                self.enterComputerBtn = Button(self.computerNameFrame, text = 'Enter', command = self.entryComputer)
                self.enterComputerBtn.pack()
                self.computerNameLabel.pack()
                self.computerNameFrame.pack()              
                with open('data.csv','a') as file: #in this case it would append on the file
                    file.write('\n'+self.computerName.get() + ',')
            if inputs in [1]:
                self.location= Entry(self.locationFrame)
                self.locationLabel = Label(self.locationFrame , text = 'In-put Computer location: \n.e.g. C5\nLook at the location of computers for help')
                self.location.insert(END, 'e.g C5') #to add to default item
                self.location.pack()
                self.enterLocationBtn = Button(self.locationFrame, text = 'Enter', command = self.entryLocation)
                self.enterLocationBtn.pack()
                self.locationLabel.pack()
                with open('data.csv','a') as file: #in this case it would APPEND from file
                    file.write(self.location.get() + ',')
            if inputs in [2]:
                self.sys = Entry(self.sysFrame)
                self.sysLabel = Label(self.sysFrame, text = 'Input Computer system: \nThe default operating system is already inserted \nHowever you can change it if its not correct ')
                self.sys.insert(END, platform.platform())
                self.sys.pack()
                self.enterSysBtn = Button(self.sysFrame, text = 'Enter', command = self.entrySys)
                self.enterSysBtn.pack()
                self.sysLabel.pack()
                with open('data.csv','a') as file: #Append from file
                     file.write(self.sys.get()+',')
        '''The 3 functions will unpack so user is entering
        a value, once they finished adding in the values it remove
        the other entry'''

        '''the 3 next function will also allow validation to be per-formed'''

    def entryComputer(self):
        import re
        if len(self.computerName.get()) == 0 or not re.match("^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$", self.computerName.get()): #if statement check its not empty
            box.showerror('Invalid Input', 'Your input is invalid. Please try again')
            self.addComputer.destroy() #gets rids of window

        else: 
            self.computerNameFrame.pack_forget()
            self.locationFrame.pack()
    def entryLocation(self):
        if len(self.location.get()) == 0 or len(self.location.get()) > 2 or len(self.location.get()) <= 1 or not re.match("^[A-Za-z0-9]*$", self.location.get()): #if statement check its not empty
            box.showerror('Invalid Input', 'Your input is invalid. Please try again')
            self.addComputer.destroy()
        else: 
            self.locationFrame.pack_forget()
            self.sysFrame.pack()
    def entrySys(self):
        if len(self.sys.get()) == 0: #if statement check its not empty
            box.showerror('Invalid Input', 'Your input is invalid. Please try again')
        else:
            self.validateInput()
        
    def validateInput(self):
        '''this function would validate the input 
        that has just been executed into the program. it would validate to check
        if the computer name they input exists within the on the database '''
        try:
            '''first part of the function would try to execute the in-puts'''
            self.cursor.execute("INSERT INTO computers(computername, loca-tion, sys) VALUES (%s, %s, %s)" ,(self.computerName.get().upper(), self.location.get().upper(), self.sys.get().upper()))
            self.connection.commit()
            self.cursor.execute("SELECT * FROM computers")

            self.sysFrame.pack_forget() #to allow the frame to dispear
            self.labelDone.pack()

            '''code below would add the input from the user into the list box'''
            self.newListboxValue = self.sys.get() + ' ' + self.computerName.get() + ' '  + self.location.get() #this would get the inputs from the user and store it together
            self.newListboxValue = self.newListboxValue.upper() #makes it an upper case valye
            self.listOfComputers.insert(self.listPosistion+1, self.newListboxValue) #adds 1 to posistion and add new value

            #self.connection.commit()
            #this is for later
            self.records = self.cursor.fetchall()
 

        except psycopg2.IntegrityError as msg:
             '''the last part would mean that the table has not been exe-cuted as the computer name is a key
                in the database so cannot add the same computer name twice'''
             box.showerror('Error', msg) 
             self.master.destroy() #closes window, when the error occurs.

    #-------------------------------next code will be for removing a computer--------------------------------#
  def checkEmpty(self):

        '''this would check if the selection
        made is empty or not'''

        selection = self.listOfComputers.curselection() #would get what was selected
        if selection: #when there something inside selection
            self.displayWarning() 
        else:
            #else returns nothings
            box.showerror('Error', 'No computer was selected')#shows error

    def displayWarning(self):
        '''this would ensure that the user want to delete the computer'''

        self.warningMsg = box.askyesno('Warning','Are you sure you want to remove this computer?')
        '''this get the users input'''
        if self.warningMsg == 1:
            self.deleteSelected = self.listOfComputers.curselection() #re-turns index of selection
            self.computerSelected = self.listOfComputers.get(self.listOfComputers.curselection()) #returns in-puts selected
            self.computerSelected = str(self.computerSelected)
            print(self.computerSelected) #testing purposes
            self.computer1 = self.computerSelected.split() #get the first 2nd string element of computer slected
   
            print(self.computer1[1]) #testing purposes
            self.remove(self.computer1[1], self.deleteSelected) #a function which takes in the deleted computers
        return self.computer1 #returns to be used in the validate remove function

    def remove(self, computername, deletion): 

        self.computername = computername #stores computer name, will be used for query
        self.deletion = deletion #returns an index of selections to be de-leted

        if self.validateRemove():
            box.showerror('Invalid', 'The computer your trying to remove is either currently reserved or inuse, Please try again later')
            self.master.destroy()
        else:
            try:
                '''command below deletes computer'''
                self.cursor.execute("DELETE FROM computers WHERE computer-name = '%s';" % (self.computername))
                self.connection.commit() 

                '''this would delete what was currently selected'''
                self.listOfComputers.delete(self.deletion)
                
                #deleted later just for testing...
                box.showinfo('Removed', 'Computer removed!') #to indicate to the user that the computer has been removed

                self.cursor.execute("SELECT * FROM reservations")

                self.records = self.cursor.fetchall()
                print(self.records)
            except psycopg2.IntegrityError as msg:
                box.showerror('Error' , 'The computer your trying to remove is currently reserved or in-use, Please try again later')
                self.master.destroy()

    def validateRemove(self):
        '''this function would validate wether the computer is reserved or not. if its is
        reserved it would not allow the user to remove the computers until its available '''
        self.cursor.execute("SELECT * from reservations") #executes sql query
        self.recordsOfComputers = cursor.fetchall() #would fetch what was executed and store it into this variables
        self.cursor.execute('SELECT COUNT(*) FROM reservations') #this querys the number of rows within the database
        self.numberOfRows = cursor.fetchone() #this would fetch one item that was return from the query

        self.cursor.execute("SELECT * from inuse")
        self.recordsOfComputersInuse = cursor.fetchall() #would fetch all the computers which is inus
        self.cursor.execute('SELECT COUNT(*) FROM inuse') #this querys the number of rows within the database
        self.numberOfRowsInuse = cursor.fetchone() #this would fetch one item that was return from the query

        self.listComputers = [ ] #list

        for num in range(self.numberOfRowsInuse[0]): 
            '''this will append ONLY the computers name in reservations ta-ble into
            the list'''
            print(self.recordsOfComputersInuse[num][1])
            self.listComputers.append(self.recordsOfComputersInuse[num][1]) 

        for num in range(self.numberOfRows[0]): 
            '''this will append ONLY the computers name in reservations ta-ble into
            the list'''
            print(self.recordsOfComputers[num][4])
            self.listComputers.append(self.recordsOfComputers[num][4]) 
       
        for self.computer in self.listComputers:
            '''check if computer in resevations table is equal to the com-puter selected'''
            if self.computer == self.computer1[1]:
                return True
            else:
                return False

if __name__ == '__main__':
    root = Tk()
    conn_string = "host='localhost' dbname='ExlExample' user='postgres' password='1111111'" #A connection string to allow me to connect to the database
    conn = psycopg2.connect(conn_string) #get a connection if it cannot be retrived an error would arrive here
    cursor = conn.cursor() #this would return a cursos object so the user can peform queries on the data using this
    my_gui = Accesssystem(root, conn, cursor)
    root.mainloop()
