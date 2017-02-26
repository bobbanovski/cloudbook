import time
import boto3

def utc_now_ts():
    return int(time.time())
    
#use amazon to send emails
def email(to_email, subject, body_html, body_text):
    client = boto3.client('ses')
    return client.send_email(
        Source = 'robert.coleman1@uqconnect.edu.au',
            Destination = {
                'ToAddresses': [
                    to_email,
                    ]
            },
            Message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    },
                }
            }
        )