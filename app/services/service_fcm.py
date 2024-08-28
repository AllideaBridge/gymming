import logging

from firebase_admin import messaging


class FcmService:
    def send_message(self, title, body, token, data=None):
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                token=token
            )
            if data is not None:
                message.data = data
            response = messaging.send(message)
            return True, response
        except Exception as e:
            logging.error(f'fcm-error: {str(e)}')
            return False, None
