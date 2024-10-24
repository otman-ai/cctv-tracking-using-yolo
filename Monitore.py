import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime
from constant import *

class Monitor:
    def __init__(self, image_width=IMAGE_WIDTH, image_height=IMAGE_HEIGHT, 
                 model_name=YOLO_MODEL,object_count_id=OBJECT_COUNT_ID
                 ) -> None:
        self.image_width = image_width
        self.image_height = image_height
        self.model_name = model_name
        self.model = None
        self.object_count_id = object_count_id
        self.track_history = []
        self.track_canvas = np.ones((self.image_height, self.image_width, 3), np.uint8) * 255  # White background

    def load_model(self):
        print(f"Loading the model {self.model_name}")
        self.model = YOLO(self.model_name)
        print("model loaded succeffully")

    def add_text(self, frame:np.ndarray, text:str, position:tuple, color=(0, 0, 0), thikness=1, font_scale=1) -> None:
            cv2.putText(frame, text, 
                        position, 
                        cv2.FONT_HERSHEY_PLAIN, font_scale, color, thikness)

    def predict(self, frame:np.ndarray, show_count=True, 
                show_time=True, limits=PEOPLE_COUNT_LIMIT, 
                animal_allowed=ANIMAL_ALLOWED, annotation=False, track_plot=False) -> tuple[np.ndarray,int]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(rgb_frame, (self.image_width, self.image_height))

        if not annotation and not track_plot:
            return resized_frame, None

        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = self.model.track(resized_frame, persist=True)

        # Get class predictions and count occurrences of class 0
        class_predictions = results[0].boxes.cls
        class_0_count = list(class_predictions).count(self.object_count_id)

        # Annotate the frame with YOLO detections
        annotated_frame = results[0].plot()
        if track_plot:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box in boxes:
                x, y, w, h = box
                tracks = (float(x), float(y))
                self.track_history.append(tracks)
                # Draw the tracking lines on the blank canvas
                if len(tracks) > 1:
                    points = np.array(self.track_history, dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(self.track_canvas, [points], isClosed=False, color=(0, 0, 255), thickness=2)
            return self.track_canvas, None
        # Put the count of class 0 in the frame
        if show_count:
            self.add_text(annotated_frame, f"People count :{class_0_count}",(int(self.image_width * 0.03), int(self.image_height * 0.05)), thikness=2)

        if show_time:
            self.add_text(annotated_frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),(int(self.image_width * 0.03), int(self.image_height * 0.96)), thikness=2)

        if limits != 0:
             # you can play sound if you want
             if class_0_count >= limits:
                self.add_text(annotated_frame, "Alert Capacity exceeded",(int(self.image_width * 0.03), int(self.image_height * 0.88)), (255, 0, 0))

        if not animal_allowed:
            animal_detected = False
            for i in range(15, 24): # animals class
                if i in class_predictions:
                    animal_detected = True
            if animal_detected:
                # you can play sound if you want
                self.add_text(annotated_frame, "Animal deteced Alert",(int(self.image_width * 0.03), int(self.image_height * 0.76)), (255, 0, 0))
        
        return annotated_frame, class_0_count