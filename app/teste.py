from fastapi import FastAPI, File, UploadFile
import face_recognition
import shutil
import mysql.connector
import numpy as np
import io

app = FastAPI()

@app.post("/compare-faces/")
async def compare_faces(known: UploadFile = File(...), unknown: UploadFile = File(...)):
    with open("known.jpg", "wb") as f:
        shutil.copyfileobj(known.file, f)
    with open("unknown.jpg", "wb") as f:
        shutil.copyfileobj(unknown.file, f)

    known_image = face_recognition.load_image_file("known.jpg")
    unknown_image = face_recognition.load_image_file("unknown.jpg")

    known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
    match = distance < 0.6  # padrão do face_recognition

    # Converte a distância para uma "porcentagem de similaridade"
    similarity_percentage = max(0, (1 - distance)) * 100

    return {
        "match": bool(match),
        "similarity": round(similarity_percentage, 2)
    }
