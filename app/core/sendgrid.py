import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

def send_email(to, subject, html_content, file_path):
    message = Mail(
        from_email=os.getenv('EMAIL_FROM'),
        to_emails=to,
        subject=subject,
        html_content=html_content)
    if os.getenv('EMAIL_BCC'):
        message.add_bcc(os.getenv('EMAIL_BCC'))
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        if file_path != None:
            with open(file_path, 'rb') as f:
                data = f.read()
                f.close()
            encoded_file = base64.b64encode(data).decode()
            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName(file_path.split('/')[-1]),
                FileType('application/file'),
                Disposition('attachment')
            )
            message.attachment = attachedFile
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(e)
        return False



