import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import BaseModel, Field
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import joblib  # For loading the scaler if needed
from tensorflow.keras.models import load_model # Ensure correct import
import uvicorn



# Load the pre-trained model using joblib





# Load environment variables
load_dotenv()

# Database connection details
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}


# Load the trained model
MODEL_PATH = "model/student_model.h5"  # Ensure correct path
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model: {e}")

# Load scaler if it was used during training
SCALER_PATH = "scaler.pkl"  # Ensure correct scaler path
try:
    scaler = joblib.load(SCALER_PATH)
except FileNotFoundError:
    scaler = None 



# Function to get a new database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection error: {err}")

app = FastAPI()

# Data Model
class Student(BaseModel):
    age: int
    gender: str
    education: str
    previous_exam_score: float
    attendance_percentage: float
    study_hours: float
    stress_level: float
    outcome: str

@app.post("/students/")
def create_student(student: Student):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get Foreign Keys
        cursor.execute("SELECT GenderID FROM Gender WHERE Gender = %s", (student.gender,))
        gender_id = cursor.fetchone()
        if not gender_id:
            raise HTTPException(status_code=400, detail="Invalid gender")

        cursor.execute("SELECT EducationID FROM ParentalEducation WHERE EducationLevel = %s", (student.education,))
        education_id = cursor.fetchone()
        if not education_id:
            raise HTTPException(status_code=400, detail="Invalid education level")

        gender_id = gender_id[0]
        education_id = education_id[0]

        # Insert Student
        query = """
            INSERT INTO Students (Age, GenderID, EducationID, PreviousExamScore, AttendancePercentage, StudyHoursPerWeek, StressLevel, Outcome)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (student.age, gender_id, education_id,
                               student.previous_exam_score, student.attendance_percentage,
                               student.study_hours, student.stress_level, student.outcome))
        conn.commit()
        student_id = cursor.lastrowid

        cursor.close()
        conn.close()
        return {"message": "Student added successfully", "StudentID": student_id}
    
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

# Encoding mappings (ensure these match training data)
gender_mapping = {"Male": 0, "Female": 1}  
education_mapping = {"High School": 0, "Associate Degree": 1, "Bachelor's Degree": 2, "Master's Degree": 3, "Doctorate": 4} 

@app.get("/students/last-predict")
def predict_last_student():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Ensure compatible with MySQL client

    query = """
        SELECT s.StudentID, s.Age, g.Gender, pe.EducationLevel, 
               s.PreviousExamScore, s.AttendancePercentage, 
               s.StudyHoursPerWeek, s.StressLevel , s.Outcome
        FROM Students s
        JOIN Gender g ON s.GenderID = g.GenderID
        JOIN ParentalEducation pe ON s.EducationID = pe.EducationID
        ORDER BY s.StudentID DESC
        LIMIT 1
    """
    
    cursor.execute(query)
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student:
        raise HTTPException(status_code=404, detail="No students found")

    # Convert categorical variables
    try:
        gender = gender_mapping[student["Gender"]]
        education = education_mapping[student["EducationLevel"]]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid categorical values")

    # Prepare input array
    features = np.array([
        [student["Age"], student["PreviousExamScore"],
         student["AttendancePercentage"], student["StudyHoursPerWeek"], student["StressLevel"]]
    ], dtype=np.float32)  # Ensure correct dtype

    # Scale features if the scaler exists
    if scaler is not None:
        features = scaler.transform(features)

    # Make prediction
    prediction = model.predict(features)
    predicted_class = int(np.round(prediction)[0][0])  # Robust classification

    return {
        "extracted_data": student,
        "processed_features": features.tolist(),
        "prediction": "Pass" if predicted_class == 1 else "Fail"
    }


@app.get("/students/last")
def read_last_student():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT s.Age, g.Gender, pe.EducationLevel, 
               s.PreviousExamScore, s.AttendancePercentage, 
               s.StudyHoursPerWeek, s.StressLevel, s.Outcome
        FROM Students s
        JOIN Gender g ON s.GenderID = g.GenderID
        JOIN ParentalEducation pe ON s.EducationID = pe.EducationID
        ORDER BY s.StudentID DESC
        LIMIT 1
    """
    cursor.execute(query)
    student = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not student:
        raise HTTPException(status_code=404, detail="No students found")
    
    return student


@app.get("/students/{student_id}")
def read_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT s.StudentID, s.Age, g.Gender, pe.EducationLevel, 
               s.PreviousExamScore, s.AttendancePercentage, 
               s.StudyHoursPerWeek, s.StressLevel, s.Outcome
        FROM Students s
        JOIN Gender g ON s.GenderID = g.GenderID
        JOIN ParentalEducation pe ON s.EducationID = pe.EducationID
        WHERE s.StudentID = %s
    """
    cursor.execute(query, (student_id,))
    student = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student



@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get Foreign Keys
    cursor.execute("SELECT GenderID FROM Gender WHERE Gender = %s", (student.gender,))
    gender_id = cursor.fetchone()
    if not gender_id:
        raise HTTPException(status_code=400, detail="Invalid gender")
    
    cursor.execute("SELECT EducationID FROM ParentalEducation WHERE EducationLevel = %s", (student.education,))
    education_id = cursor.fetchone()
    if not education_id:
        raise HTTPException(status_code=400, detail="Invalid education level")
    
    gender_id = gender_id[0]
    education_id = education_id[0]

    query = """
        UPDATE Students 
        SET Age = %s, GenderID = %s, EducationID = %s, 
            PreviousExamScore = %s, AttendancePercentage = %s, 
            StudyHoursPerWeek = %s, StressLevel = %s, Outcome = %s
        WHERE StudentID = %s
    """
    cursor.execute(query, (student.age, gender_id, education_id,
                           student.previous_exam_score, student.attendance_percentage,
                           student.study_hours, student.stress_level, student.outcome, student_id))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Student updated successfully"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Students WHERE StudentID = %s", (student_id,))
    conn.commit()

    cursor.close()
    conn.close()
    
    return {"message": "Student deleted successfully"}