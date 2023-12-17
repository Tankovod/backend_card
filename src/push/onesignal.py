# Конфигурация OneSignal API
import requests


class OneSig:
    def __init__(self):
        self.api_url = 'https://onesignal.com/api/v1/notifications'
        self.headers = {'Authorization': f'Basic ZmU4NTI1ODctZDc1ZC00NzJjLTk4OTktYTE1ODgwMDE4MTMw',
                        "Content-Type": "application/json"}

    def send_notify(self, message, title):
        data = {
            "app_id": '41fecdf7-3f5d-45ea-a80a-e59448b3bc17',
            "target_channel": 'push',
            'headings': {"ru": title},
            "contents": {"en": message, "ru": message},
            "included_segments": ["All"]
        }

        response = requests.post(self.api_url, headers=self.headers, json=data)
        return response.json()
