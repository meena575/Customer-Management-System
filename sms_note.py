import os
from twilio.rest import Client

from twilio.rest import Client

def send_sms_notification(to, message):
    # Your Twilio account SID and Auth Token
    account_sid = 'ACe60f9d116abaa8c2bdc10ffca500a06b'
    auth_token = 'd85768ddc47415e4667848856aacdeee'
    client = Client(account_sid, auth_token)

    # Send SMS
    message = client.messages.create(
        body=message,
        from_='+12569801271',
        to=to
    )

    print(f"Message sent to {to}: {message.sid}")
def send_sms_notification_multi(to_numbers, message):
    # Your Twilio account SID and Auth Token
    account_sid = 'ACe60f9d116abaa8c2bdc10ffca500a06b'
    auth_token = 'd85768ddc47415e4667848856aacdeee'
    client = Client(account_sid, auth_token)

    # Send SMS to each number in the list
    for to in to_numbers:
        message = client.messages.create(
            body=message,
            from_='+12569801271',
            to=to
        )
        print(f"Message sent to {to}: {message.sid}")
