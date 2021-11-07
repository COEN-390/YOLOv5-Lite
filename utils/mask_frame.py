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
    organization_id: str



    def _init_(self, endpoint, project_id, api_key, organization_id, buffer_time=1, frame_threshold=5, notification_rate=15):
        self.buffer_time = buffer_time
        self.frame_threshold = frame_threshold
        self.notification_rate = notification_rate
        self.last_notification = time.time() - notification_rate
        self.organization_id = organization_id
        (self.client
        .set_endpoint(endpoint) # Your API Endpoint
        .set_project(project_id) # Your project ID
        .set_key(api_key) # Your secret API key
        )
        self.database = Database(self.client)

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
            result = self.database.create_document('61871d8957bbc', {'timestamp': time.time(), 'organizationId': self.organization_id})
            print(result)
            self.last_notification = time.time()
