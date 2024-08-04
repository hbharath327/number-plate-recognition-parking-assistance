# Number Plate Recognition and Parking Assistance

## Overview
This project is designed to recognize vehicle number plates using Optical Character Recognition (OCR) technology and assist in parking management by allotting parking slots and tracking the duration of parking.

![Project Demo](link_to_video)  
*Watch the demo video to see the system in action.*

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
├── static/                # Static files (CSS, JS, images)
├── README.md              # Project documentation
└── demo_video.mp4         # Project demonstration video
