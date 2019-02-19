"""
Flask application to accept some details, generate, display, and email a QR code to users
"""
import base64
import os
from flask import Flask, request
from sendgrid.helpers.mail import Email, Content, Mail, Attachment
import sendgrid
import qrcode

# pylint: disable=invalid-name
app = Flask(__name__)
sg = sendgrid.SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY', None))

@app.route('/submit', methods=['POST'])
def stuff():
    """
    Accept data from the form, generate, display, and email QR code to user
    """
    name = request.form['name']
    email = request.form['email']
    roll_number = request.form['roll_number']
    img = qrcode.make("Name: {}\nEmail: {}\nRoll Number: {}\n".format(name, email, roll_number))
    img.save('qr.png')
    img_data = open('qr.png', 'rb').read()
    encoded = base64.b64encode(img_data).decode()

    from_email = Email('script.mailus@gmail.com')
    to_email = Email(email)
    subject = 'Registration for {}'.format(roll_number)
    content = Content('text/plain', 'QR code attached below!')
    mail = Mail(from_email, subject, to_email, content)

    attachment = Attachment()
    attachment.type = 'image/png'
    attachment.filename = 'qr.png'
    attachment.content = encoded

    mail.add_attachment(attachment)

    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

    return 'Please save this QR Code. It has also been emailed to you.<br><img src=\
            "data:image/jpeg;base64, {}"/>'.format(encoded)

@app.route('/')
def root():
    """
    Main endpoint. Display the form to the user.
    """
    with open('form.html', 'r') as file:
        data = file.read()
    return data

if __name__ == '__main__':
    app.run()