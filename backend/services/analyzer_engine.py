# backend/services/analyzer_engine.py
import cv2
import numpy as np
import mediapipe as mp
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Any

def download_preview(video_id: str, fallback: bool = True) -> np.ndarray | None:
    """
    Скачивает превью с YouTube по video_id.
    Пытается скачать в порядке: maxresdefault -> hqdefault -> mqdefault.
    Возвращает изображение в формате OpenCV (BGR) или None, если ни одно не загрузилось.
    """
    resolutions = ["maxresdefault", "hqdefault", "mqdefault"]
    for res in resolutions:
        url = f"https://i.ytimg.com/vi/{video_id}/{res}.jpg"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                # Конвертируем байты в изображение OpenCV
                img_array = np.frombuffer(resp.content, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    return img
        except Exception:
            continue
    return None

def analyze_preview(video_id: str) -> Dict[str, Any]:
    """
    Анализирует превью и возвращает признаки кликабельности.
    Возвращаемый словарь:
        {
            "face_closeup": bool,
            "high_contrast": bool,
            "text_area": bool,
            "center_object": bool,
            "score_sum": int (0–4)
        }
    """
    # 1. Скачиваем изображение
    img = download_preview(video_id)
    if img is None:
        # Если картинка не загрузилась, возвращаем все False и score_sum=0
        return {
            "face_closeup": False,
            "high_contrast": False,
            "text_area": False,
            "center_object": False,
            "score_sum": 0
        }

    h, w = img.shape[:2]
    if h == 0 or w == 0:
        return {
            "face_closeup": False,
            "high_contrast": False,
            "text_area": False,
            "center_object": False,
            "score_sum": 0
        }

    # 2. Обнаружение лица через MediaPipe (площадь ≥ 12% кадра)
    face_detected = False
    try:
        mp_face = mp.solutions.face_detection
        with mp_face.FaceDetection(min_detection_confidence=0.5) as face_detection:
            # MediaPipe ожидает RGB
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb)
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    area = bbox.width * bbox.height
                    if area >= 0.12:
                        face_detected = True
                        break
    except Exception:
        # Если MediaPipe упал, просто пропускаем
        pass

    # 3. Контраст (стандартное отклонение яркости) – порог ≥ 55
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contrast = float(np.std(gray))
    high_contrast = contrast >= 55.0

    # 4. Текстовая зона (оцениваем через градиенты Собеля)
    # Упрощённый метод: выделяем области с высоким градиентом
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    # Порог отсечения (можно подбирать)
    text_mask = magnitude > 30
    text_ratio = np.sum(text_mask) / (h * w)
    has_text = text_ratio >= 0.08

    # 5. Центр объекта (анализируем градиенты в центральной зоне)
    # Если центральная часть имеет высокие градиенты, считаем, что там есть объект
    center_h_start = h // 4
    center_h_end = 3 * h // 4
    center_w_start = w // 4
    center_w_end = 3 * w // 4
    center_crop = gray[center_h_start:center_h_end, center_w_start:center_w_end]
    if center_crop.size > 0:
        center_grad = np.std(center_crop)
        center_object = center_grad > 50   # эмпирический порог
    else:
        center_object = False

    # 6. Суммируем баллы
    score_sum = (1 if face_detected else 0) + \
                (1 if high_contrast else 0) + \
                (1 if has_text else 0) + \
                (1 if center_object else 0)

    return {
        "face_closeup": face_detected,
        "high_contrast": high_contrast,
        "text_area": has_text,
        "center_object": center_object,
        "score_sum": score_sum
    }