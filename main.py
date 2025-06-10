import time
import smtplib
import email
import imaplib


#global password to chnge every user
password=123456

def checkmail():
    print("checking mail")
    #every time interval:
    time.sleep(20)
    #check unread emails
    print("checking unread")

#expect info to be in this format:[Get, 87952, example.txt, none] if it was push the file name would become the name the attachment is given
def extract_info(mail):
    print("extracting info")
    #initial values
    command=""
    message_password=""
    filename=""
    attachment=""
    sender_email=""

    #code to gather info for command and password will be here

    #check password before attachment is ever even looked at for security reasons
    code=checkpassword([command,message_password,"filler","filler"])
    #if code is zero end
    if code==0:
        print("invalid message")
        return 0
    

    #get the filename, sender email, and attchment now that password has been verified

    #caalling list command
    if code==1:
        list_command(sender_email)
    #get command
    elif code==2:
        get_command([command,message_password,filename,sender_email,None])
    #push command
    elif code==3:
        push_command([command,message_password,filename,sender_email,attachment])
    else:
        print("somethin went wrong")
        return 0

    return 0


#will return 1 if valid 0 if invalid so that theres no risk of downloading malicious attachments
def checkpassword(email_info):
    print("checking password")
    if email_info[1]==(password) :
        if email_info[0]=="Get":
            print("get command recieved")
            return 2
        elif email_info[0]=="List":
            print("list command recieved")
            return 1
        elif email_info[0]=="Push":
            print("Push command received")
            return 3
        else:
            print("incorrect or unknown command")
            return 0
    else:
        print("incorrect password")
        return 0
    


#list
def list_command(return_address):
    print("printing files and folders")
    #basic subject line and holder for body content
    subject_line="file directory"
    content=""

    #here the body content (file director) will be made

    #now send it to the response email function
    response_email(return_address,subject_line,content)

#get
def get_command(email_info):
    print("retrieving file/folder")
    subject_line="Requested file/folder"
    content=""

    #implement get command logic

    #send it to response email function
    response_email(email_info[3],subject_line,content)

#push
def push_command(email_info):
    print("pushing file to folder")
    subject_line="File push info"

    #change if file push fails
    content="File push successful"


    #implement push command logic


    #send it to response email function
    response_email(email_info[3],subject_line,content)

#compiling return email
def response_email(return_email,subject,content):
    print("sending return email")
    #sending file