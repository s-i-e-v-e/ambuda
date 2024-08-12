from pathlib import Path
from ambuda.ocr import backend_google_ocr as google_ocr
from unstd import os
from ambuda.std import id


def exec_google_ocr(image_path: Path):
    ocr_response = google_ocr.run(image_path)
    ocr_bounding_boxes = google_ocr.serialize_bounding_boxes(ocr_response.bounding_boxes)
    return ocr_response.text_content, ocr_bounding_boxes


def exec_tesseract_ocr(image_path: Path):
    f = f"/tmp/{id.random_string()}"
    xs = ["tesseract", "-l", "san", image_path.as_posix(), f]
    os.run(xs)
    return os.read_file_as_string(f"{f}.txt"), ""
