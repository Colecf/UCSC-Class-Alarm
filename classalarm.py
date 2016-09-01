#!/usr/bin/python

import re;
import mechanize;
import json;
from bs4 import BeautifulSoup
import urllib2;
import datetime
import time;
import sys;
import os;
import smtplib

#For jsonifying python dates to javascript format
#http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, Class):
        return obj.__dict__;
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))



class Class:
    def __init__(self):
        self.classLink = ""
        self.classNum = 1
        self.classID = ""
        self.classTitle = ""
        self.classType = ""
        self.classNotes = ""
        self.fullName = ""
        self.enrollmentReqs = ""
        self.days = []
        self.startTime = datetime.time(8, 0);
        self.endTime = datetime.time(9, 45);
        self.instructor = ""
        self.status = ""
        self.capacity = 0
        self.enrolled = 0
        self.location = ""
        self.materialsLink = ""
        self.credits = 0
        self.ge = ""
        self.description = ""
        self.startDate = ""
        self.endDate = ""
        self.labs = [];
        
    def __str__(self):
        return str(self.classNum)+' '+self.classID+' '+self.classTitle+' '+self.classType+' '+\
            self.instructor+' '+self.status+' '+str(self.capacity)+' '+str(self.enrolled)+' '+self.location+\
            ' credits:'+str(self.credits) +' '+self.ge

def readClasses(response):
    classes = []
    soup = BeautifulSoup(response)

    if "returned no matches." in response:
        return []
           
    container = soup.select('.center-block > .panel-body')[0]
    for row in container.find_all('div', class_="panel"):
        collumn = 0
        c = Class()
        repeat = False
        heading = row.find('div', class_='panel-heading')
        c.classLink = "https://pisa.ucsc.edu/class_search/"+heading.find('a')['href'];
        c.classID = heading.find('a').getText()
        c.classTitle = heading.find_all('a')[1].getText()
        c.status = heading.find('span').getText()

        bodyrows = row.select('.panel-body > .row > div')
        c.classNum = bodyrows[0].find('a').getText()
        c.instructor = bodyrows[1].find(text=True, recursive=False).strip()
        typeAndLoc = bodyrows[2].find(text=True, recursive=False).strip()
        if typeAndLoc and ":" in typeAndLoc:
            split = typeAndLoc.split(': ')
            c.classType = split[0]
            c.location = split[1]

        peopleStr = bodyrows[4].getText().strip()
        peopleStrSpace = peopleStr.find(' ')
        peopleStrSpace2 = peopleStr.find(' ', peopleStrSpace+1)
        c.enrolled = int(peopleStr[0:peopleStrSpace])
        c.capacity = int(peopleStr[peopleStrSpace2+1:peopleStr.find(' ', peopleStrSpace2+1)])
        c.materialsLink = bodyrows[5].find('a')['href']
            
        if not repeat:
            classes.append(c)
    return classes


config = {}
if(not os.path.isfile('classalarm.cfg')):
    f = open('classalarm.cfg', 'w')
    f.write('''\
{
    "subject": "CMPS",
    "catalog_nbr": "101",
    "secsBetweenChecks": 10,

    "toaddrs": "destination@example.com",
    "smptServer": "smtp.gmail.com:587"
    "fromaddr": "sender@gmail.com",
    "password": "password"
}
''')
    f.close()
    print "Config file generated. Please edit it and then retry."
    sys.exit(1)
else:
    f = open('classalarm.cfg', 'r')
    config = json.loads(f.read())
    f.close()

count = 0

while True:
    br = mechanize.Browser()
    sucessfullyRead = False
    while not sucessfullyRead:
        try:
            br.open('https://pisa.ucsc.edu/class_search/')
            sucessfullyRead = True
        except:
            print "Couldn't load ucsc website! Is your internet or the ucsc website down? Retrying in 30 secs"
            time.sleep(30)
        
    br.select_form(name='searchForm')
    br['binds[:reg_status]'] = ['all'];
    br['binds[:subject]'] = [config['subject']];
    br['binds[:catalog_nbr]'] = config['catalog_nbr'];

    #Use if you want all subjects
    #br.find_control('binds[:subject]').get(nr=1).selected = True;

    response = br.submit().read()
    classes = readClasses(response)
    count = count+1;

    print "Attempt "+str(count)

    for i in range(0, len(classes)):
        if (classes[i].status == "Open"):
            print classes[i].classID + " AVAILABLE!!!"
            sys.stdout.write('\a')
            sys.stdout.flush()
            fromaddr = config['fromaddr']
            toaddrs  = config['toaddrs']
            msg = 'Subject: Enroll in '+classes[i].classID+'\n\nDetected an opening at '+str(datetime.datetime.now())
            username = fromaddr[:fromaddr.find('@')]
            password = config['password']
            server = smtplib.SMTP(config['smtpServer'])
            server.starttls()
            server.login(username,password)
            server.sendmail(fromaddr, toaddrs, msg)
            server.quit()

            while 1:               # Hang, because keepalive would keep sending
                time.sleep(100)    # emails if we quit.

        else:
            print classes[i].classID + " " + classes[i].status
    time.sleep(config['secsBetweenChecks'])
