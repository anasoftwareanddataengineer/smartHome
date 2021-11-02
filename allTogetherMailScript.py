import urllib.request
import time
import requests
from threading import Thread
import serial
from datetime import datetime
import smtplib
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from matplotlib import pyplot as plt
import imaplib

# PORT = 'COM7'
# BAUD_RATE = 9600

serialCommuncation = serial.Serial('COM7')

sourceEmail = 'iotsingidunumstudent@gmail.com'
destinationEmail = 'iotsingidunumstudent@gmail.com'

CHANEL_ID = '1546154'
API_KEY_WRITE = 'UZ3RLQT01FILW3C4'
API_KEY_READ = '5448636BX3U2R7RM'

BASE_URL = 'https://api.thingspeak.com'

WRITE_URL = '{}/update?api_key={}'.format(BASE_URL, API_KEY_WRITE)
READ_CHANNEL_URL = '{}/channels/{}/feeds.json?api_key={}'.format(BASE_URL, CHANEL_ID, API_KEY_READ)
READ_FIELD1_URL = '{}/channels/{}/fields/{}.json?api_key={}'.format(BASE_URL, CHANEL_ID, 1, API_KEY_READ)
READ_FIELD2_URL = '{}/channels/{}/fields/{}.json?api_key={}'.format(BASE_URL, CHANEL_ID, 2, API_KEY_READ)
READ_FIELD3_URL = '{}/channels/{}/fields/{}.json?api_key={}'.format(BASE_URL, CHANEL_ID, 3, API_KEY_READ)
READ_FIELD4_URL = '{}/channels/{}/fields/{}.json?api_key={}'.format(BASE_URL, CHANEL_ID, 4, API_KEY_READ)
READ_FIELD5_URL = '{}/channels/{}/fields/{}.json?api_key={}'.format(BASE_URL, CHANEL_ID, 5, API_KEY_READ)

#function for sending the gathered data to ThingSpeak
def sendAll(temp,illu,movn,dalm,dsec):
    urllib.request.urlopen("{}&field1={}&field2={}&field3={}&field4={}&field5={}".format(WRITE_URL, temp, illu, movn, dsec,dalm))
"""
def sendTemp(temp):
    urllib.request.urlopen("{}&field1={}".format(WRITE_URL, temp))
    print('temp: ',temp)
def sendIllu(illu):
    urllib.request.urlopen("{}&field2={}".format(WRITE_URL, illu))
    print('illu: ',illu)
def sendMovn(movn):
    urllib.request.urlopen("{}&field3={}".format(WRITE_URL, movn))
    print('movn: ',movn)
def sendDalm(dalm):
    urllib.request.urlopen("{}&field5={}".format(WRITE_URL, dalm))
    print('dalm: ',dalm)
def sendDsec(dsec):
    urllib.request.urlopen("{}&field4={}".format(WRITE_URL, dsec))
    print('dsec: ',dsec)
    """

#sending notification via email
def sendNotification(notificationMessage):
    notification = MIMEMultipart()
    notification['Subject'] = notificationMessage
    notification['From'] = sourceEmail
    notification['To'] = destinationEmail
    #sending mail notification
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    r = server.login(sourceEmail, 'iot2018230140')
    r = server.sendmail(sourceEmail, destinationEmail, notification.as_string())
    server.quit()

#processing the data recieved from arduino
someData = []
def processData(recievedMessage):
    #all of my messages are according to the following structure:
    #first four letters: type of the measurments(temperature, luminocity, number of motions etc)
    #followed by a -
    #followed by the measured value, so the data type will always take first four letters, and the value will take space after -
    #hence [:4] and [5:], - is on the 4th position

    #when all measures are taken, they are sent to ThingSpeak
    if(len(someData)==5):
        print('sending data ',someData)
        #sending data to ThingSpeak
        sendAll(someData[0],someData[3],someData[4],someData[1],someData[2])
        someData.clear()
    
    #when data is recieved from arduino it is being processed - type and value
    dataType = recievedMessage[:4]
    dataValue = recievedMessage[5:]

    #matching the data
    if(dataType == 'temp'):
        temp = float(dataValue)
        # Thread(target=sendTemp, args=(temp, )).start()
        someData.append(temp)
    if(dataType == 'illu'):
        illu = float(dataValue)
        # Thread(target=sendIllu, args=(illu, )).start()
        someData.append(illu)
    if(dataType == 'movn'):
        movn = int(dataValue)
        # Thread(target=sendMovn, args=(movn, )).start()
        someData.append(movn)
    if(dataType == 'dalm'):
        dalm = int(dataValue)
        # Thread(target=sendDalm, args=(dalm, )).start()
        someData.append(dalm)
    if(dataType == 'dsec'):
        dsec = int(dataValue)
        # Thread(target=sendDsec, args=(dsec, )).start()
        someData.append(dsec)
    
    #motion detected - send email
    if(dataType == 'noti'):
        sendNotification('Motion detected')

#recieving message from Arduino
def recieve(serialCom):
    while True:
        if serialCom.in_waiting > 0:
            receivedMessage = serialCom.readline().decode('utf-8').strip()
            processData(receivedMessage)
        time.sleep(0.1)

#retrieving data from ThingSpeak
def doData(data,fieldNumber):
    #separating time and value from recieved json file, from dict to lists
    dataList = []
    timeList = []
    for i in range(len(data)): #data is a dictionary atm
        newData = data[i][fieldNumber] #accessing feeds in dict, values gathered
        if(newData!=None):#if there is data
            dataList.append(float(newData)) #add that data to data list
            timeList.append(datetime.strftime(datetime.strptime(data[i]['created_at'],"%Y-%m-%dT%H:%M:%SZ"),'%H:%M:%S'))#extract the time for the given data
    return dataList, timeList

respTemp = requests.get(READ_FIELD1_URL)
dataTempJson = respTemp.json()
dataTemp = dataTempJson["feeds"]
tempTime = []
tempData = []
tempData, tempTime = doData(dataTemp,'field1')
respIllu = requests.get(READ_FIELD2_URL)
dataIlluJson = respIllu.json()
dataIllu = dataIlluJson["feeds"]
illuTime = []
illuData = []
illuData, illuTime = doData(dataIllu,'field2')
respMotion = requests.get(READ_FIELD3_URL)
dataMotionJson = respMotion.json()
dataMotion = dataMotionJson["feeds"]
motionTime = []
motionData = []
motionData, motionTime = doData(dataMotion,'field3')
respSecurity = requests.get(READ_FIELD4_URL)
dataSecurityJson = respSecurity.json()
dataSecurity = dataSecurityJson["feeds"]
securityTime = []
securityData = []
securityData, securityTime = doData(dataSecurity,'field4')
respAutoLight = requests.get(READ_FIELD5_URL)
dataAutoLightJson = respAutoLight.json()
dataAutoLight = dataAutoLightJson["feeds"]
autoLightTime = []
autoLightData = []
autoLightData , autoLightTime = doData(dataAutoLight,'field5')
"""
print(tempData[0])
print(tempData[-1])
print(len(tempData))
print(len(tempTime))

print(illuData[0])
print(illuData[-1])
print(len(illuData))
print(len(illuTime))

print(motionData[0])
print(motionData[-1])
print(len(motionData))
print(len(motionTime))

print(securityData[0])
print(securityData[-1])
print(len(securityData))
print(len(securityTime))

print(autoLightData[0])
print(autoLightData[-1])
print(len(autoLightData))
print(len(autoLightTime))
"""
#Temperature calculations
minTemp = min(tempData)
#print(minTemp)

maxTemp = max(tempData)
#print(maxTemp)

dailyAvgTemp = sum(tempData)/len(tempData)
#print(dailyAvgTemp)

#per hour
def hourlyMeasurments(data):
    tempMeasurments = []
    averageHourlyMeasurment = []
    for i in range(len(data)):
        tempMeasurments.append(data[i])
        if i % 6 == 0:
            tempMes = sum(tempMeasurments)/len(tempMeasurments)
            averageHourlyMeasurment.append(tempMes)
            tempMeasurments.clear()
    #print(averageHourlyMeasurment)
    return averageHourlyMeasurment
"""
def hourlyMeasurments(measurement):
    if measurement == 'temperature':
        tempMeasurments = []
        averageHourlyTemperature = []
        for i in range(len(tempData)):
            tempMeasurments.append(tempData[i])
            if i % 6 == 0:
                tempMes = sum(tempMeasurments)/len(tempMeasurments)
                averageHourlyTemperature.append(tempMes)
                tempMeasurments.clear()
        #print(averageHourlyTemperature)
        return averageHourlyTemperature
    elif measurement == 'illumination':
        illuMeasurments = []
        averageHourlyIllumination = []
        for i in range(len(illuData)):
            illuMeasurments.append(illuData[i])
            if i % 6 == 0:
                illuMes = sum(illuMeasurments)/len(illuMeasurments)
                averageHourlyIllumination.append(illuMes)
                illuMeasurments.clear()
        #print(averageHourlyIllumination)
        return averageHourlyIllumination
    elif measurement == 'motion':
        motionMeasurments = []
        averageHourlyMotion = []
        for i in range(len(motionData)):
            motionMeasurments.append(motionData[i])
            if i % 6 == 0:
                motionMes = sum(motionMeasurments)/len(motionMeasurments)
                averageHourlyMotion.append(motionMes)
                motionMeasurments.clear()
        #print(averageHourlyMotion)
        return averageHourlyMotion
"""

averageHourlyTemperatures = hourlyMeasurments(tempData)
averageHourlyTemperature = sum(averageHourlyTemperatures)/len(averageHourlyTemperatures)

plt.ioff()
fig = plt.figure(figsize=(100,60))
plt.title("Daily Temperature")
plt.xlabel('hours')
plt.ylabel('temperature')
plt.plot(tempTime, tempData)
temperatureGraph = 'report-temperatrure.png'
plt.savefig('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + temperatureGraph)
imageFileTemperature = open('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + temperatureGraph, 'rb') 
msgImageTemperature = MIMEImage(imageFileTemperature.read())
imageFileTemperature.close()
msgImageTemperature.add_header('Content-ID', '<image1>')

#Illumination calculations
minIllu = min(illuData)
#print(minIllu)

maxIllu = max(illuData)
#print(maxIllu)

dailyAvgIllu = sum(illuData)/len(illuData)
#print(dailyAvgIllu)

#per hour
averageHourlyIlluminations = hourlyMeasurments(illuData)
averageHourlyIllumination = sum(averageHourlyIlluminations)/len(averageHourlyIlluminations)


fig = plt.figure(figsize=(100,60))
plt.title("Daily Illumination")
plt.xlabel('hours')
plt.ylabel('illumination')
plt.plot(illuTime, illuData)
illuminationGraph = 'report-illumination.png'
plt.savefig('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + illuminationGraph)
imageFileIllumination = open('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + illuminationGraph, 'rb') 
msgImageIllumination = MIMEImage(imageFileIllumination.read())
imageFileIllumination.close()
msgImageIllumination.add_header('Content-ID', '<image2>')

#motion

#Sum of motions
sumOfMotions = len(motionData)

#motions per hour
averageHourlyMotions = hourlyMeasurments(motionData)
averageHourlyMotion = sum(averageHourlyMotions)/len(averageHourlyMotions)

#extracting the hours
motionHours = []
for i in range(len(motionTime)):
    if i % 6 == 0:
        motionHours.append(motionTime[i])

#scale the graph, hours are too small
fig = plt.figure(figsize=(20,6))
plt.title("Motions per hour")
plt.xlabel('hours')
plt.ylabel('number of motions')
plt.plot(motionHours, averageHourlyMotions)
motionGraph = 'report-motions.png'
plt.savefig('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + motionGraph)
imageFileMotion = open('C:\\Users\\Ana\\Desktop\\IoT\graphs\\' + motionGraph, 'rb') 
msgImageMotion = MIMEImage(imageFileMotion.read())
imageFileMotion.close()
msgImageMotion.add_header('Content-ID', '<image3>')

#Sum of motions
sumOfAutoLight = sum(autoLightData)

#Sum of motions
sumOfSecurityMode = sum(securityData)

def sendReport():
    message = MIMEMultipart()
    message['Subject'] = 'Daily report'
    message['From'] = sourceEmail
    message['To'] = destinationEmail

    message.preamble = '====================================================='

    htmlText = """\
        <html>
        <head></head>
        <body>
            <h1>Daily report on</h1>
            <p>
                Temperature measurement is performed every 10 minutes. The minimum daily temperature was: <strong>{:.2f} °C</strong> and maximum was: <strong>{:.2f} °C</strong>. The average daily temperature was: <strong>{:.2f} °C</strong>. The average temperature per hour is: <strong>{}</strong>.
                The average temperatures per hour are: <strong>{}</strong>.
            </p>
            <br><img src="cid:image1">
            <p>
                Illumination measurement is performed every 10 minutes. The minimum daily illumination was: <strong>{:.2f} °C</strong> and maximum was: <strong>{:.2f} °C</strong>. The average daily illumination was: <strong>{:.2f} °C</strong>. The average illumination per hour is: <strong>{}</strong>.
                The average illuminations per hour are: <strong>{}</strong>.
            </p>
            <br><img src="cid:image2">

            <p> The total number of motion detections is <strong>{}</strong>. The average number of detections per hour is: <strong>{:.2f}</strong></p>
            <br><img src="cid:image3">
            <p>
                Home security mode was on for <strong>{}</strong>.
            </p>
            <p>
                Auto light mode was on for <strong>{}</strong>.
            </p>
        </body>
        </html>
    """.format(minTemp, maxTemp, dailyAvgTemp, averageHourlyTemperature, averageHourlyTemperatures, minIllu, maxIllu, dailyAvgIllu, averageHourlyIllumination, averageHourlyIlluminations, sumOfMotions, averageHourlyMotion, sumOfSecurityMode, sumOfAutoLight)

    mimeText = MIMEText(htmlText, 'html')
 
    message.attach(mimeText)
    message.attach(msgImageTemperature)
    message.attach(msgImageIllumination)
    message.attach(msgImageMotion)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    r = server.login(sourceEmail, 'iot2018230140')
    r = server.sendmail(sourceEmail, destinationEmail, message.as_string())
    server.quit()

#sendReport()

#ser = serial.Serial('COM7')
#PORT = 'COM7'
#BAUD_RATE = 9600

def recieve(serialCom):
    receivedMessage = ""
    while True:
        if serialCom.in_waiting > 0:
            receivedMessage = serialCom.read(size=serialCom.in_waiting).decode('ascii')
            
        time.sleep(0.1)


#read the emails, because if they're left unread, the functions will be called again and again, as long as the email is unread
#call the functions, switch the mode by the email title
def checkMail(email, serialCommuncation):
    email.select('inbox')

    while True:
        retcode, responseTurnOnLight = email.search(None, '(SUBJECT "light_on" UNSEEN)')
        retcode, responseTurnOffLight = email.search(None, '(SUBJECT "light_off" UNSEEN)')
        retcode, responseTurnOnAutoLight = email.search(None, '(SUBJECT "auto light mode" UNSEEN)')
        retcode, responseTurnOnSecureMode = email.search(None, '(SUBJECT "SECURE_MODE" UNSEEN)')
        retcode, responseTurnOffSecureMode = email.search(None, '(SUBJECT "SECURE_MODE_OFF" UNSEEN)')
        retcode, responseReport = email.search(None, '(SUBJECT "REPORT" UNSEEN)')
        
        if len(responseTurnOnLight[0]) > 0:
            text = "light_on"
            serialCommuncation.write("light_on".encode('ascii'))
            emailIds = responseTurnOnLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOffLight[0]) > 0:
            text = "light_off"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOffLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseTurnOnAutoLight[0]) > 0:
            text = "auto light mode"
            serialCommuncation.write("auto light mode".encode('ascii'))
            emailIds = responseTurnOnAutoLight[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseTurnOnSecureMode[0]) > 0:
            text = "SECURE_MODE"
            serialCommuncation.write("SECURE_MODE".encode('ascii'))
            emailIds = responseTurnOnSecureMode[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        
        if len(responseTurnOffSecureMode[0]) > 0:
            text = "SECURE_MODE_OFF"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseTurnOffSecureMode[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseReport[0]) > 0:
            text = "REPORT"
            serialCommuncation.write(text.encode('ascii'))
            emailIds = responseReport[0].split()
            sendReport()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
        time.sleep(3)

"""
dayToday = datetime.now()
while True:
    if dayToday.hour != datetime.now().hour:
        sendNotification("REPORT")
        dayToday = datetime.now()
    time.sleep(10)
"""
#serialCommuncation = serial.Serial(PORT, BAUD_RATE)

email = imaplib.IMAP4_SSL('imap.gmail.com')
email.login('iotsingidunumstudent@gmail.com', 'iot2018230140')


receivingThread  = Thread(target=recieve, args=(serialCommuncation, ))
receivingThread.start()
checkEmailThread  = Thread(target=checkMail, args=(email, serialCommuncation, ))
checkEmailThread.start()

dayToday = datetime.now()
while True:
    if dayToday.hour != datetime.now().hour:
        sendNotification("REPORT")
        dayToday = datetime.now()
    time.sleep(10)