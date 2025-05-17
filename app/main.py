from fastapi import FastAPI, UploadFile, File, Form
import face_recognition
import mysql.connector
import numpy as np
import io
import base64

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host="", user="", password="", database=""
    )

@app.post("/register")
async def register(file: UploadFile = File(...), user_id: int = Form(...)):
    
    image = await file.read()  # Lê a imagem binária

    # Carregar e gerar a codificação facial da imagem
    image = face_recognition.load_image_file(io.BytesIO(image))
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return {"error": "No face detected in the image"}

    encoding = face_encodings[0]  # Codificação da face

    # Salvar a codificação facial no banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE user SET image = %s WHERE id = %s",
        (encoding.tobytes(), user_id)  # Armazenar os bytes da codificação
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "face registered"}

@app.post("/face_id")
async def face_id(file: UploadFile = File(...)):
     # Identificação
    image = await file.read()  # Lê a imagem binária para comparação

    # Carregar a imagem e gerar a codificação
    image = face_recognition.load_image_file(io.BytesIO(image))
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return {"error": "No face detected in the image"}

    unknown_encoding = face_encodings[0]

    # Recuperar as codificações faciais armazenadas
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, image FROM user")
    faces = cursor.fetchall()

    for face in faces:
        known_encoding = np.frombuffer(face['image'], dtype=np.float64)
        
        # Comparar as codificações faciais com uma tolerância de 0.6
        match = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.6)[0]

        if match:
            return {"user_id": face['id']}  # Retorna o id do usuário

    return {"message": "user not found"}  # Nenhuma correspondência encontrada
