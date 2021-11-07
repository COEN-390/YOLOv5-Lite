import time
from appwrite.client import Client
from appwrite.services.database import Database


class FrameBuffer():
    frame_queue = []
    buffer_time: int = 1
    frame_threshold: int = 15
    notification_rate: int = 15
    last_notification: float = (time.time() - notification_rate)
    client = Client()

    (client
    .set_endpoint('https://appwrite.orpine.net/v1') # Your API Endpoint
    .set_project('6137a2ef0d4f5') # Your project ID
    .set_key('6dee49d861f5d443d04065e321522967182b1c65e75cffcf3905e37ebb927e87e7c2a540385b561e3b3df91fcc775749275dc7922f480389b5d2712a25abb667f1a0595c4107685e0bf8d3be22364228c9b0725c0f60d3ffc4b0ef9decd10ce4fb50b574d76d6bc3f56a38393ab505b15bae29aa260511ee5078434117f7df23') # Your secret API key
    )

    database = Database(client)

    def _init_(self, buffer_time=1, frame_threshold=5, notification_rate=15):
        self.buffer_time = buffer_time
        self.frame_threshold = frame_threshold
        self.notification_rate = notification_rate
        self.last_notification = time.time() - notification_rate

    def insert_frame(self):
        self.frame_queue.append(time.time())

    def empty_queue(self):
        while (self.frame_queue and self.frame_queue[0] < (time.time() - 1)):
            self.frame_queue.pop(0)

    def check_queue(self):
        if (len(self.frame_queue) > self.frame_threshold):
            self.send_notification()

    def send_notification(self):
        if (self.last_notification < (time.time() - self.notification_rate)):
            print("No mask threshold reached. Notifying.")
            result = self.database.create_document('61871d8957bbc', {'timestamp': time.time(), 'organizationId': 'testOrganization'})
            print(result)
            self.last_notification = time.time()
