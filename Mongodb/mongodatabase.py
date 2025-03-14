import os
from pymongo import MongoClient 
from dotenv import load_dotenv 

# Load environment variables from .env file 
load_dotenv() 

# Get credentials securely from environment variables 
mongo_user = os.getenv("DBM_USER") 
mongo_password = os.getenv("DBM_PASSWORD") 

# Ensure credentials are loaded if not mongo_user or not mongo_password: raise ValueError("MongoDB credentials not found. Check your .env file.") # Correct MongoDB URI MONGO_URI = f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.a6aoh.mongodb.net/StudentPerformance?retryWrites=true&w=majority" # Connect to MongoDB client = MongoClient(MONGO_URI) db = client["StudentPerformance"] # Database name # Collections gender_collection = db["Gender"] education_collection = db["ParentalEducation"] students_collection = db["Students"] # Insert Gender Data (Ensuring uniqueness) genders = [{"_id": 1, "Gender": "Male"}, {"_id": 2, "Gender": "Female"}] try: gender_collection.insert_many(genders, ordered=False) except Exception as e: print(f"Gender collection insertion error: {e}") # Insert Parental Education Data education_levels = [ {"_id": 1, "EducationLevel": "High School"}, {"_id": 2, "EducationLevel": "Associate Degree"}, {"_id": 3, "EducationLevel": "Bachelor's Degree"}, {"_id": 4, "EducationLevel": "Master's Degree"}, {"_id": 5, "EducationLevel": "Doctorate"}, ] try: education_collection.insert_many(education_levels, ordered=False) except Exception as e: print(f"Education collection insertion error: {e}") # Insert Sample Student Data students = [ { "Age": 22, "Gender": "Female", "EducationLevel": "Bachelor's Degree", "PreviousExamScore": 78.76, "AttendancePercentage": 50.57, "StudyHoursPerWeek": 3.24, "StressLevel": 5.36, "Outcome": "Pass", }, { "Age": 20, "Gender": "Male", "EducationLevel": "High School", "PreviousExamScore": 65.45, "AttendancePercentage": 70.20, "StudyHoursPerWeek": 2.8, "StressLevel": 6.1, "Outcome": "Fail", }, { "Age": 25, "Gender": "Female", "EducationLevel": "Master's Degree", "PreviousExamScore": 88.32, "AttendancePercentage": 90.5, "StudyHoursPerWeek": 4.5, "StressLevel": 4.0, "Outcome": "Pass", }, ] try: students_collection.insert_many(students) except Exception as e: print(f"Students collection insertion error: {e}") # Retrieve and Print Student Data for student in students_collection.find(): print(student) print("\nDatabase setup complete!")
