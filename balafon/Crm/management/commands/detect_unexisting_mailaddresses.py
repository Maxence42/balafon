import imaplib
import email
import getpass

from balafon.Crm import models

imapaddress = raw_input("Enter the imap server address : ")
mailaddress = raw_input("\n\nEnter your mail address : ")
passwd = getpass.getpass("\n\nEnter your mail password : ")

mail = imaplib.IMAP4(imapaddress, 143)
mail.login(mailaddress, passwd)
mail.select("inbox")
                    
(status, res) = mail.list()
(status, numberMessages) = mail.select('INBOX')
print status, 'Nombre de messages = ', numberMessages
search_critera = 'REVERSE DATE'
(status, searchRes) = mail.search(None, 'ALL')
ids = searchRes[0].split()
for i in range(len(ids)):
    (status, res) = mail.fetch(ids[i], '(BODY[])')
    for responsePart in res:
        if isinstance(responsePart, tuple):
            msg = email.message_from_string(responsePart[1])
            if "daemon" in msg['from'] or "DAEMON" in msg['from']:
                err = models.Error_MailAddress()
                err.address = msg['X-Failed-Recipients']
                err.date = msg['Delivery-date']
                err.error = str(msg).split("55")[1].split("\n")[0]
                err.save()