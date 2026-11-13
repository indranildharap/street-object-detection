import base64
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from .StreetObjDetector import StreetObjDetector

app = FastAPI(title="Street Object Detector")


class DetectionResponse(BaseModel):
    annotated_image: str
    counts: dict[str, int]


@lru_cache(maxsize=1)
def get_detector() -> StreetObjDetector:
    return StreetObjDetector()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile = File(...)) -> DetectionResponse:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    decoded = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), cv2.IMREAD_COLOR)
    if decoded is None:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    detector = get_detector()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "upload.png"
            if not cv2.imwrite(str(image_path), decoded):
                raise RuntimeError("Could not prepare the uploaded image for detection.")

            results = detector.detect_objects(str(image_path))
            annotated_rgb = detector.visualize_results(results)

        counts: Counter[str] = Counter()
        for result in results:
            class_ids = result.boxes.cls.int().tolist()
            for class_id in class_ids:
                counts[str(result.names[class_id])] += 1

        annotated_bgr = cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR)
        success, encoded_image = cv2.imencode(".png", annotated_bgr)
        if not success:
            raise RuntimeError("Could not encode the detection result.")

        return DetectionResponse(
            annotated_image=base64.b64encode(encoded_image.tobytes()).decode("ascii"),
            counts=dict(counts),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc