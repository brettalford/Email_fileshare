import time
import smtplib
import email
import imaplib

#global password to change for every user so it can be customized
password=123456
#global email
program_address=""
#global email password
program_mail_password=""
#imap server
Imap="imap.gmail.com"


#check email for new commands
def checkmail():
    print("checking mail")
    

    try:
        #logging into email and navigating to inbox
        connection = imaplib.IMAP4_SSL(Imap)
        connection.login(program_address, program_mail_password)
        connection.select('inbox')

        #retrieving status and messages
        status, messages = connection.search(None, '(UNSEEN)')
        #if status is not okay
        if status != 'OK':
            #error message
            print("Failed to retrieve emails.")
            return

        #ids for unread messages
        mail_ids = messages[0].split()
        #number of messages
        mail_quantity = len(mail_ids)
        #printing number of messages
        print(f"{mail_quantity} unread emails found.")


        #for all unread mail
        for mail_id in mail_ids:
            # Fetch the email by ID
            res, msg_data = connection.fetch(mail_id, '(RFC822)')
            if res != 'OK':
                print(f"Failed to fetch message {mail_id}")
                continue

            # Get raw email content
            raw_email = msg_data[0][1]

            # Convert to structured email object
            msg = email.message_from_bytes(raw_email)

            # Pass the structured email to your extractor
            extract_info(msg)
            #make email marked as read
            connection.store(mail_id, '+FLAGS', '\\Seen')

    #in case of error
    except Exception as e:
        print(f'an error occured in message retrieval: {e}')
    #log out after cycle complete
    try:
        connection.logout()
    except:
        pass
    

    return

#expect info to be in this format:[Get, 87952, example.txt, none] if it was push the file name would become the name the attachment is given
def extract_info(msg):
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
        return 
    

    #get the filename, sender email, and attchment now that password has been verified

    #calling list command
    if code==1:
        list_command(sender_email)
    #get command
    elif code==2:
        get_command([command,message_password,filename,sender_email,None])
    #push command
    elif code==3:
        push_command([command,message_password,filename,sender_email,attachment])

    #something wrong
    else:
        print("somethin went wrong")
        return 0

    return

#will return 1 if valid 0 if invalid so that theres no risk of downloading malicious attachments
def checkpassword(email_info):
    print("checking password")
    #if the password recieved is the same as the password
    if email_info[1]==(password) :
        #depending on command return command code, listed in expected use order
        #if the command is get return 2
        if email_info[0]=="Get":
            print("get command recieved")
            return 2
        #if the command is list return 1
        elif email_info[0]=="List":
            print("list command recieved")
            return 1
        #if the command is push return 3
        elif email_info[0]=="Push":
            print("Push command received")
            return 3
        #no command found return 0 because its an error
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


if __name__ == '__main__':
    while True:
        #check for new commands
        checkmail()
        #every time interval:
        time.sleep(30)