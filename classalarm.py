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

def readClasses(html):
    soup = BeautifulSoup(html)
    tbody = soup.find('td', class_='even').parent.parent
    classes = []
    for tr in tbody.find_all('tr'):
        collumn = 0
        c = Class()
        for td in tr.find_all('td'):
            if collumn==0:
                c.classLink = "https://pisa.ucsc.edu/class_search/"+td.a['href'];
                c.classNum = int(td.a.getText());
            elif collumn==1:
                c.classID = td.getText();
            elif collumn==2:
                c.classTitle = td.a.getText();
            elif collumn==3:
                c.classType = td.getText();
            elif collumn==4:
                #Split by capital letters
                c.days = re.findall(r'[A-Z][^A-Z]*', td.getText());
            elif collumn==5:
                times = td.getText().split("-")
                startTimes = times[0].split(":")
                endTimes = times[1].split(":")
                hour = int(startTimes[0])
                if times[0][-2] == "A" and hour == 12:
                    hour = 0
                elif times[0][-2] == "P" and hour != 12:
                    hour = hour + 12
                    c.startTime = datetime.time(hour, int(startTimes[1][:2]))
                    hour = int(endTimes[0])
                if times[1][-2] == "A" and hour == 12:
                    hour = 0
                elif times[1][-2] == "P" and hour != 12:
                    hour = hour + 12
                c.endTime = datetime.time(hour, int(endTimes[1][:2]))
            elif collumn==6:
                c.instructor = td.getText();
            elif collumn==7:
                c.status = td.center.img['alt'];
            elif collumn==8:
                c.capacity = int(td.getText());
            elif collumn==9:
                c.enrolled = int(td.getText());
            #skip 10 because available seats can be calculated
            elif collumn==11:
                c.location = td.getText();
            elif collumn==12:
                c.materialsLink = td.input['onclick'][13:-12]
            collumn=collumn+1


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
    "comment1": "Sender must be a valid gmail account",
    "fromaddr": "sender@gmail.com",
    "username": "sender",
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
    br.open('https://pisa.ucsc.edu/class_search/')

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
        if (classes[i].status != "Closed"):
            print classes[i].classID + " AVAILABLE!!!"
            sys.stdout.write('\a')
            sys.stdout.flush()
            fromaddr = config['fromaddr']
            toaddrs  = config['toaddrs']
            msg = 'Subject: Enroll in '+classes[i].classID+'\n\nDetected an opening at '+str(datetime.datetime.now())
            username = config['username']
            password = config['password']
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(username,password)
            server.sendmail(fromaddr, toaddrs, msg)
            server.quit()

            while 1:    # Hang, because keepalive would keep sending
                time.sleep(100)    # emails if we quit.

        else:
            print classes[i].classID + " unavailable"
    time.sleep(config['secsBetweenChecks'])
