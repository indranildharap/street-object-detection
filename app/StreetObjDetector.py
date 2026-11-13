from pathlib import Path

import cv2
from ultralytics import YOLO


class StreetObjDetector:
    model_path = Path(__file__).resolve().parent.parent / "yolo11n.pt"

    def __init__(self) -> None:
        self.model = YOLO(str(self.model_path))

    def detect_objects(self, image_path: str):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("The uploaded file is not a valid image.")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.model.predict(image_rgb)

    def visualize_results(self, results):
        if not results:
            raise ValueError("The object detector returned no results.")

        annotated_bgr = results[0].plot()
        return cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
