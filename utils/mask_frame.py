import threading
import time
from appwrite.client import Client
from appwrite.services.database import Database
from appwrite.services.functions import Functions

from utils.video_clip_buffer import VideoClipBuffer



class AWFrameBuffer():
    frame_queue = []
    buffer_time: int = 1
    frame_threshold: int = 15
    notification_rate: int = 15
    last_notification: float = (time.time() - notification_rate)
    client = Client()
    organization_id: str
    ping_rate: int = 120
    last_ping: int = (time.time() - ping_rate)
    device_id: str = "defaultDevice"
    functions = Functions(client)
    video_clip_buffer : VideoClipBuffer




    def __init__(self, endpoint, project_id, api_key, organization_id, device_id, video_clip_buffer: VideoClipBuffer, buffer_time=1, frame_threshold=5, notification_rate=15, ping_rate=120):
        self.buffer_time = buffer_time
        self.frame_threshold = frame_threshold
        self.notification_rate = notification_rate
        self.last_notification = time.time() - notification_rate
        self.ping_rate = ping_rate
        self.last_ping = time.time() - ping_rate
        self.organization_id = organization_id
        (self.client
        .set_endpoint(endpoint) # Your API Endpoint
        .set_project(project_id) # Your project ID
        .set_key(api_key) # Your secret API key
        )
        self.database = Database(self.client)
        self.device_id = device_id
        self.functions = Functions(self.client)
        self.video_clip_buffer = video_clip_buffer

    def insert_frame(self):
        self.frame_queue.append(time.time())

    def empty_queue(self):
        # Send ping
        self.send_ping()
        # Empty queue
        while (self.frame_queue and self.frame_queue[0] < (time.time() - self.buffer_time)):
            self.frame_queue.pop(0)

    def check_queue(self):
        if (len(self.frame_queue) > self.frame_threshold):
            # Send notification
            self.send_notification()


    def send_notification(self):
        if (self.last_notification < (time.time() - self.notification_rate)):
            clip = self.video_clip_buffer.save_buffer()
            if clip is None:
                return
            print("No mask threshold reached. Notifying.")
            result = self.database.create_document('61871d8957bbc', {'timestamp': time.time(), 'organizationId': self.organization_id, 'deviceId': self.device_id, 'fileId': clip}, read=["*"], write=["*"])
            print(result)
            result = self.functions.create_execution('618d9b5104d7c', 'NO MASK DETECTED | DEVICE: ' + self.device_id)
            print(result)
            # Save clip
            self.last_notification = time.time()

    
    def send_ping(self):
        if (self.last_ping < (time.time() - self.ping_rate)):
            self.last_ping = time.time()
            print("Sending health ping")
            # List documents for this device ID
            result = self.database.list_documents('61896dfa87e44', filters=['deviceId={}'.format(self.device_id), 'organizationId={}'.format(self.organization_id)])
            # If there is no document for this device, create it
            if (not result["documents"]):
                result = self.database.create_document('61896dfa87e44', {'deviceId': self.device_id, 'organizationId': self.organization_id, 'healthTimestamp': time.time()}, read=["*"], write=["*"])
            # Else, update the document with the correct timestamp
            else:
                document_id = result["documents"][0]["$id"]
                document = self.database.get_document('61896dfa87e44', document_id)
                result = self.database.update_document('61896dfa87e44', document_id, {'deviceId': document["deviceId"], 'organizationId': document["organizationId"], 'healthTimestamp': time.time()}, read=["*"], write=["*"])
