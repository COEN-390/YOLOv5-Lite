import os
import time
from typing import List
from utils.video_clip_frame import VideoClipFrame
import string
import random
import cv2
from appwrite.client import Client
from appwrite.services.storage import Storage


class VideoClipBuffer():
    frame_queue:List[VideoClipFrame] = []
    buffer_length: int
    random_name: str
    client = Client()
    storage = Storage(client)

    def __init__(self, endpoint, project_id, api_key, organization_id, device_id, buffer_length=15):
        (self.client
        .set_endpoint(endpoint) # Your API Endpoint
        .set_project(project_id) # Your project ID
        .set_key(api_key) # Your secret API key
        )
        self.storage = Storage(self.client)
        self.buffer_length = buffer_length
        self.random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

    def save_buffer(self):
        fps, w, h = 30, self.frame_queue[0].shape[1], self.frame_queue[0].shape[0]
        save_path = './' + self.random_name + '.mp4'
        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        while len(self.frame_queue) > 0:
            vid_writer.write(self.frame_queue.pop(0).frame)
        result = self.storage.create_file(open(save_path, 'rb'))
        os.remove(save_path)
        print("Placeholder")

    def add_frame(self, im0):
        frame_object = VideoClipFrame(im0, time.time())
        self.frame_queue.append(frame_object)
        self.empty_queue()

    def empty_queue(self):
        while (self.frame_queue and self.frame_queue[0] < (time.time() - self.buffer_length)):
            self.frame_queue.pop(0)

