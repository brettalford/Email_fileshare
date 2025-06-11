import time
import smtplib
import email
import imaplib
import os
import io
import zipfile

#global password to change for every user so it can be customized
password=123456
#global email
program_address=""
#global email password
program_mail_password=""
#imap server
Imap="imap.gmail.com"
#root folder
root_folder = "shared_files"

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
    attachment=None
    sender_email=msg.get("From")

    #get subject line
    subject=msg.get("Subject","")

    #getting parts of subject line
    parts = [p.strip() for p in subject.split(',')]
    #if you at least have command and password (because list only has two)
    if len(parts) >=2:
        #command is first
        command = parts[0]
        #password
        message_password = parts[1]
        if len(parts)>2:
            #filename
            filename = parts[2] 
    else:
        print("inproper format")
        return
    #check password before attachment is ever even looked at for security reasons
    code=checkpassword([command,message_password,"filler","filler"])
    #if code is zero end
    if code==0:
        print("invalid message")
        return 
    #calling list command
    if code==1:
        list_command(sender_email)
    #get command
    elif code==2:
        get_command([command,message_password,filename,sender_email,None])
    #push command
    elif code==3:
        #get attachment now that verified
        #go through all parts
        for part in msg.walk():
            #if part is an attachment
            if part.get_content_disposition() == "attachment":
                #get the attachment
                attachment = part.get_payload(decode=True)
                #stop because only one attachment allowed
                break
        #call the push command now that everything is set up
        push_command([command,message_password,filename,sender_email,attachment])
    #something wrong
    else:
        print("somethin went wrong")
        return 
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
    try:
        #empty tree
        tree=""
        #for directory paths and names and file names in the root folder
        for dirpath, dirnames, filenames in os.walk(root_folder):
                #file depth
                level = dirpath.replace(root_folder, "").count(os.sep)
                #indenting
                indent = "│   " * (level - 1) + ("├── " if level > 0 else "")
                #foldername
                folder_name = os.path.basename(dirpath) + "/"
                #starting at base level
                if level == 0:
                    tree += f"{folder_name}\n"
                #if not currently at base level
                else:
                    tree += f"{indent}{folder_name}\n"
                sub_indent = "│   " * level + "├── "
                #for all files in the directory/folder
                for f in filenames:
                    tree += f"{sub_indent}{f}\n"
    except Exception as e:
        tree=f"error detected in listing {e}"
    print(tree)
    #now send it to the response email function
    response_email(return_address,subject_line,tree,attachment=None)

#get
def get_command(email_info):
    print("retrieving file/folder")
    subject_line = "Requested file/folder"
    content = ""
    filename = email_info[2]
   

    # Walk through root_folder recursively
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Check for file match
        if filename in filenames:
            found_file_path = os.path.join(dirpath, filename)
            break
        # Check for directory match
        if filename in dirnames:
            found_dir_path = os.path.join(dirpath, filename)
            break



    #if you find it
    if found_file_path:
        #try 
        try:
            #open file
            with open(found_file_path, "rb") as f:
                #red file
                attachment = f.read()
            #file found message
            content = f"The file '{filename}' was found and attached."
            #sending email
            response_email(email_info[3], subject_line, content, attachment=attachment)
        #exception
        except Exception as e:
            content = f"Error reading file: {str(e)}"
            response_email(email_info[3], subject_line, content, attachment=None)


    #if you find the folder
    elif found_dir_path:
        try:
            # Create an in-memory ZIP file
            zip_buffer = io.BytesIO()
            #zip up the folder
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for foldername, _, files in os.walk(found_dir_path):
                    for file in files:
                        file_path = os.path.join(foldername, file)
                        arcname = os.path.relpath(file_path, start=found_dir_path)
                        zipf.write(file_path, arcname=arcname)
            zip_buffer.seek(0)
            #make the zip the attachment
            attachment = zip_buffer.read()
            #set content to success message
            content = f"The folder '{filename}' was zipped and attached."
            #send to response email
            response_email(email_info[3], subject_line, content, attachment=attachment)
        except Exception as e:
            content = f"Error zipping folder: {str(e)}"
            response_email(email_info[3], subject_line, content, attachment=None)



    #if you cant find it
    else:
        content = f"File '{filename}' not found in shared directory."
        response_email(email_info[3], subject_line, content, attachment=None)

#push
def push_command(email_info):
    print("pushing file to folder")
    file_name=email_info[2]
    #subject line
    subject_line=f"File {email_info[2]} writing to folder"
    #change if file push fails
    content="File push successful"
    #making full file
    full_file_path=os.path.abspath(os.path.join(root_folder,file_name))

    #making sure malicious file cant be inserted in wider system
    if not full_file_path.startswith(os.path.abspath(root_folder)):
        content = "Security error: Invalid file path."
        response_email(email_info[3], subject_line, content, attachment=None)
        return


    #trying to write file
    try:
        #open file location
        with open(full_file_path, 'wb') as f:
            #write attachment
            f.write(email_info[4])
    #if theres a fialure
    except Exception as e:
        content=f"error pushing file {str(e)}"

    #send it to response email function
    response_email(email_info[3],subject_line,content,attachment=None)



#compiling return email
def response_email(return_email,subject,content,attachment):
    print("sending return email")
    #sending file


if __name__ == '__main__':
    while True:
        #check for new commands
        checkmail()
        #every time interval:
        time.sleep(30)