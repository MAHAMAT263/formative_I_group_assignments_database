Database Design

Project Overview
We built a complete database system that brings together both SQL and MongoDB. The goal was to design a database, set up MongoDB collections, and created a FastAPI-powered backend for seamless CRUD operations. On top of that, we developed a script to fetch and prepare data for machine learning predictions.

What We Did
- Designed and Implemented a Database: Built a well-structured relational database with at least three tables, including primary/foreign keys, stored procedures, and triggers.
- Integrated MongoDB: Created equivalent NoSQL collections to complement our relational database.
- Developed a FastAPI Backend: Implemented RESTful endpoints for creating, reading, updating, and deleting records.
- Set Up an ML Prediction Pipeline: Retrieved the latest database entry, processed the data, and ran predictions using a pre-trained machine learning model.

How It Works
1. The SQL database holds structured student data, while MongoDB manages complementary NoSQL records.
2. The FastAPI backend enables CRUD operations for managing data.
3. A script fetches the latest entry from the database and prepares it for ML predictions.
4. The ML model processes the data and generates predictions.
