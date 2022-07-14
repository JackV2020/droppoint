#!/usr/bin/python3
import json
import os
import sys
import shutil
import argparse
import glob
import time

#----------------------------------------------------------------------

def amail(  recipient
            ,sender         = 'defaultsendername@gmail.com'
            ,password       = 'defaultsenderpassword'
            ,ccrecipient    = ''
            ,bccrecipient   = ''
            ,subject        = 'No Subject'
            ,body           = ''
            ,bodyfile       = ''
            ,attachments    = ''
            ,smtpserver     = 'smtp.gmail.com'
            ,port           = '465'
            ,use_ssl        = 'yes'
            ,fromname       = 'droppoint'
            ):

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    import os.path
    from os import path
    import socket

    recipient = recipient.replace(';',',')
    msg = MIMEMultipart()
    msg['From']    = fromname+'<'+fromname+'>'
    msg['To']      = recipient
    msg["Cc"]      = ccrecipient
    msg["Bcc"]     = bccrecipient
    msg['Subject'] = subject

    recipients = recipient + ',' + ccrecipient + ',' + bccrecipient
    
    if attachments != '':
        for attach in attachments.split(',') :
            attach=attach.strip()
            filename = os.path.basename(attach)
            attachment = open(attach, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                        f'attachment; filename= {filename}' )
            msg.attach(part)

    if body != '' :
        if body.find('<html>') == 0:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

    if bodyfile != '' :
        if path.exists(bodyfile):
            if body != '' :
                print(f'body text already in use so send {bodyfile} as attachment')
            with open(bodyfile, 'r') as myfile:
                filebody = myfile.read()
            if filebody.find('<html>') == 0:
                msg.attach(MIMEText(filebody, 'html'))
            else:
                msg.attach(MIMEText(filebody, 'plain'))
        else:
            print('bodyfile does not exist :'+bodyfile)

    status = 'ok'
    socket.setdefaulttimeout(10)
    if use_ssl == 'yes':
        try:
            context = ssl.create_default_context()
# for smtp.gmail.com port 465
            with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
                server.login(sender, password )
                server.sendmail(sender, recipients.split(','), msg.as_string())
                server.quit()
        except:
            status = 'error'

    else:
        try:
# for smtp.gmail.com port 587
            server = smtplib.SMTP(smtpserver, port)
            server.ehlo()
            server.starttls()
            server.login(sender, password )
            server.sendmail(sender, recipients.split(','), msg.as_string())
            server.quit()
        except:
            status = 'error'
            print("SMPT server connection error")

    return status
    
#----------------------------------------------------------------------

if len(sys.argv) == 1 :
    print('Usage : -phase inbox|error')
# ----- the inbox folder is either the real inbox or the error folder.
# ----- the error folder is handy while working on a new type ;-)
else:
    parser=argparse.ArgumentParser()

    parser.add_argument('-phase', help='Required: inbox|error')

    args=parser.parse_args()

    phase = str(args.phase)

    print('------------------------------------------------------------')
    print('Phase :' + phase)
    if phase in ['inbox', 'error']:
        root = '/var/www/html/droppoint/data/'
# ----- inbox is either the real inbox or the error folder
        inbox = root + phase + '/'
        stage = root +'stage/'
        error = root +'error/'
        done = root +'done/'
        
        now = time.time()
        
        requestTypes = ['mail', 'test', 'any']
        
# ----- Move files from inbox|error to stage

        print('Read from inbox '+inbox)
        for file in os.listdir(inbox):
            current = os.path.join(inbox, file)

            if os.path.isfile(current):
                prefix=file[:file.find('.')]
                if prefix in requestTypes:
                    print('Move to stage : ' + file)
                    shutil.move(inbox + file , stage + file)
                elif os.stat(current).st_mtime < now - 7 * 24 * 60 * 60 :
                    print('Delete unsupported old file from inbox : ' + current)
                    os.remove(current)
                else:
                    print('Found unsupported file in inbox : ' + current)
            else:
                print('Found something strange : ' + file)
        
# ----- process staged files
        
        print('Read from stage '+stage)
#        for filename in os.listdir(stage):
#            print('process : ' +filename)
#            current = os.path.join(stage, filename)

# ----- process mail files
# content like below : 
# ( note there are double quotes in the main json and single quotes in the json of the payload )
# [{"requestType":"mail","payload":"{'m_ena':'yes' , 'm_ssl':'yes' , 'a_id':'barometer' , 'm_prt':'465' , 'm_to':'reveiver1@gmail.com;receiver2@gmail.com' , 'm_usr':'sender@gmail.com' , 'm_hst':'smtp.gmail.com' , 'm_pwd':'senderpassword' , 'm_dp':'https:\/\/pi41.home\/droppoint\/droppoint.php' , 'm_su':'Temperature Alarm reached' , 'm_msg':'Saturday 2022-06-04 20:35:21 Temperature 25.25 limit : 6.70'}"}]

        for current in sorted(glob.glob(stage+'mail.*')):
#            print ("Current mail File Being Processed is: " + current)
            if os.path.isfile(current):
                filename=current[len(stage):]
                print('Process file  : ' + filename)
                if (True):
                    with open(current, 'r') as file:
                        try:
# remove the '[' at the begininning and the ']' at the end
                            data = file.read().replace('\n', '')[1:-1]
# d contains the 2 json elements requestType and payload
                            d = json.loads(data)
# e contains all the json elements of payload
                            e = json.loads(d['payload'].replace("'",'"'))
# when m_usr is not in the file we use default sender name and default password
                            if e['m_usr'] == '':
                                status = amail(
                                     smtpserver     = e['m_hst']
                                    ,port           = e['m_prt']
                                    ,use_ssl        = e['m_ssl']
                                    ,recipient      = e['m_to']
                                    ,subject        = e['m_su']
                                    ,body           = e['m_msg']
                                    ,fromname       = e['a_id']
                                    )
                            else:
                                status = amail(
                                     sender         = e['m_usr']
                                    ,password       = e['m_pwd']
                                    ,smtpserver     = e['m_hst']
                                    ,port           = e['m_prt']
                                    ,use_ssl        = e['m_ssl']
                                    ,recipient      = e['m_to']
                                    ,subject        = e['m_su']
                                    ,body           = e['m_msg']
                                    ,fromname       = e['a_id']
                                    )
                            if status == 'ok':
                                print('Move to done  : ' + filename)
                                shutil.move(stage + filename , done + filename)
                            else:
                                print('Move to error1: ' + filename)
                                shutil.move(stage + filename , error + filename)
                        except:
                            print('Move to error : ' + filename)
                            shutil.move(stage + filename , error + filename)
# sending multiple files very fast may cause them to arrive in the wrong order
                    time.sleep(1)

# ----- process test files
# ( just move them to the done folder )

        for current in sorted(glob.glob(stage+'test.*')):
            print ("Current test File Being Processed is: " + current)
            if os.path.isfile(current):
                filename=current[len(stage):]
                print('Process file  : ' + filename)
                if (True):
                    with open(current, 'r') as file:
                        try:
                            status = 'ok'
                            if status == 'ok':
                                print('Move to done  : ' + filename)
                                shutil.move(stage + filename , done + filename)
                            else:
                                print('Move to error1: ' + filename)
                                shutil.move(stage + filename , error + filename)
                        except:
                            print('Move to error : ' + filename)
                            shutil.move(stage + filename , error + filename)
# sending multiple files very fast may cause them to arrive in the wrong order
                    time.sleep(1)

# ----- Delete old processed files

        print('Delete old files from done '+done)
        for file in os.listdir(done):
            current = os.path.join(done, file)

            if os.stat(current).st_mtime < now - 4 * 7 * 24 * 60 * 60 :
                if os.path.isfile(current):
                    print('Delete old file  from done : ' + current)
                    os.remove(current)
