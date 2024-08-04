# Number Plate Recognition and Parking Assistance

## Overview
This project is designed to recognize vehicle number plates using Optical Character Recognition (OCR) technology and assist in parking management by allotting parking slots and tracking the duration of parking.

## Abstract
This project presents a comprehensive solution for parking management through the integration of Number Plate Recognition (NPR) and Parking Assistance systems. Utilizing Optical Character Recognition (OCR) technology, the system accurately detects and reads vehicle number plates upon entry and exit, automating the process of parking slot allocation. The system records the entry and exit times, calculates the duration of the stay, and assists in efficient parking management.

## Features
- **Number Plate Detection**: Captures and detects number plates from images or video feeds.
- **OCR Processing**: Extracts text from the detected number plates using advanced OCR algorithms.
- **Parking Slot Allocation**: Automatically assigns available parking slots based on recognized number plates.
- **Time Tracking**: Tracks the in/out time of vehicles and calculates the duration of parking.
- **User Interface**: Provides an intuitive interface for image uploads and real-time detection.

## Technologies Used
- **Programming Language**: Python
- **Libraries**: 
  - OpenCV for image processing
  - Pytesseract for OCR
  - Flask for the web interface
- **Tools**: 
  - Jupyter Notebooks for development
  - GitHub for version control

## Project Structure
```plaintext
├── main.py                # Main script for number plate recognition and parking management
├── templates/             # HTML templates for web interface
└── README.md              # Project documentation

