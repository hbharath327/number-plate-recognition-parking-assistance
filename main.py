import cv2
import pytesseract
import sqlite3
import datetime
import re
from tkinter import Tk, filedialog, Label, Button, messagebox, Frame, Text, Scrollbar
from PIL import Image, ImageTk

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'

class LicensePlateDetector: 
    def __init__(self):
        self.root = Tk()
        self.root.title("License Plate Detector")
        self.root.geometry("1200x700")  # Increased window size to accommodate new views

        # Controls
        self.label = Label(self.root, text="Select an image file:")
        self.label.pack()

        self.button = Button(self.root, text="Browse", command=self.select_image)
        self.button.pack()

        # self.view_records_button = Button(self.root, text="View Previous Records", command=self.display_exited_cars)
        # self.view_records_button.pack()

        # Frame for image display
        self.image_frame = Frame(self.root)
        self.image_frame.pack(side="left", fill="both", expand=True)

        # Frame for parking slots
        self.parking_slots_frame = Frame(self.root)
        self.parking_slots_frame.pack(side="top", fill="both", expand=True)

        # Frame for exited cars
        self.exited_cars_frame = Frame(self.root)
        self.exited_cars_frame.pack(side="bottom", fill="both", expand=True)

        self.display_parking_slots()  # Display parking slots on startup
        self.display_exited_cars()    # Display exited cars on startup

        self.root.mainloop()

    def get_db_connection(self):
        conn = sqlite3.connect('car_database.db', timeout=10)
        return conn

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", ".jpg .jpeg .png .bmp")]
        )
        if self.image_path:
            self.process_image()

    def calculate_duration(self, entry_time, exit_time):
        format = "%Y-%m-%d %H:%M:%S"
        entry = datetime.datetime.strptime(entry_time, format)
        exit = datetime.datetime.strptime(exit_time, format)
        duration = exit - entry
        return str(duration)

    def display_parking_slots(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()

            # Clear previous parking slots
            for widget in self.parking_slots_frame.winfo_children():
                widget.destroy()

            # Retrieve parking slots information
            c.execute("SELECT slot_number, occupied FROM parking_slots")
            slots = c.fetchall()

            # Display parking slots
            for slot_number, occupied in slots:
                color = "green" if not occupied else "yellow"
                label = Label(self.parking_slots_frame, text=f"Slot {slot_number}", bg=color, width=20, height=2, borderwidth=2, relief="groove")
                label.grid(row=(slot_number - 1) // 5, column=(slot_number - 1) % 5, padx=5, pady=5)

    def process_image(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()

            # Create tables if they don't exist
            c.execute('''CREATE TABLE IF NOT EXISTS cars
                         (license_plate text, timestamp text, parking_slot integer)''')

            c.execute('''CREATE TABLE IF NOT EXISTS parking_slots
                         (slot_number integer PRIMARY KEY, occupied boolean)''')

            c.execute('''CREATE TABLE IF NOT EXISTS exited_cars
                         (license_plate text, time_in text, time_out text, duration text)''')

            # Initialize parking slots if empty
            c.execute('SELECT COUNT(*) FROM parking_slots')
            if c.fetchone()[0] == 0:
                for i in range(1, 21):  # Example: 20 parking slots
                    c.execute("INSERT INTO parking_slots (slot_number, occupied) VALUES (?, ?)", (i, False))
                conn.commit()

            # Read the image file
            image = cv2.imread(self.image_path)

            # Convert to Grayscale Image
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Canny Edge Detection
            canny_edge = cv2.Canny(gray_image, 170, 200)

            # Find contours based on Edges
            contours, _ = cv2.findContours(canny_edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

            # Initialize license Plate contour and x,y,w,h coordinates
            contour_with_license_plate = None
            license_plate = None
            x, y, w, h = None, None, None, None

            # Find the contour with 4 potential corners and create ROI around it
            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
                if len(approx) == 4:  # see whether it is a Rect
                    contour_with_license_plate = approx
                    x, y, w, h = cv2.boundingRect(contour)
                    license_plate = gray_image[y:y + h, x:x + w]
                    break
            
            if license_plate is not None:
                (thresh, license_plate) = cv2.threshold(license_plate, 127, 255, cv2.THRESH_BINARY)

                # Removing Noise from the detected image
                license_plate = cv2.bilateralFilter(license_plate, 11, 17, 17)
                (thresh, license_plate) = cv2.threshold(license_plate, 150, 180, cv2.THRESH_BINARY)

                # Text Recognition
                text = pytesseract.image_to_string(license_plate).strip()

                # Filter out only alphanumeric characters
                text = re.sub(r'[^A-Za-z0-9]', '', text)

                # Draw License Plate and write the Text
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
                image = cv2.putText(image, text, (x - 100, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                print("License Plate :", text)

                # Get current timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Check if the license plate is already in the database
                c.execute("SELECT parking_slot, timestamp FROM cars WHERE license_plate = ? ORDER BY timestamp DESC LIMIT 1", (text,))
                existing_record = c.fetchone()

                if existing_record:
                    # Car is exiting, free up the parking slot
                    slot_number, entry_time = existing_record
                    c.execute("UPDATE parking_slots SET occupied = 0 WHERE slot_number = ?", (slot_number,))
                    c.execute("DELETE FROM cars WHERE license_plate = ? AND parking_slot = ?", (text, slot_number))

                    # Record exit information
                    duration = self.calculate_duration(entry_time, timestamp)
                    c.execute("INSERT INTO exited_cars (license_plate, time_in, time_out, duration) VALUES (?, ?, ?, ?)",
                              (text, entry_time, timestamp, duration))
                    conn.commit()

                    parking_info = f"Parking Slot {slot_number} is now available. Car has exited.\nDuration: {duration}"
                else:
                    # Car is entering, assign a new parking slot
                    c.execute("SELECT slot_number FROM parking_slots WHERE occupied = 0 LIMIT 1")
                    available_slot = c.fetchone()

                    if available_slot:
                        slot_number = available_slot[0]
                        # Mark slot as occupied
                        c.execute("UPDATE parking_slots SET occupied = 1 WHERE slot_number = ?", (slot_number,))
                        c.execute("INSERT INTO cars (license_plate, timestamp, parking_slot) VALUES (?, ?, ?)", (text, timestamp, slot_number))
                        conn.commit()
                        parking_info = f"Parking Slot Assigned: {slot_number}"
                    else:
                        parking_info = "Parking is full"
                        # Optionally, you can still insert the record with NULL or a special value for parking_slot
                        c.execute("INSERT INTO cars (license_plate, timestamp, parking_slot) VALUES (?, ?, ?)", (text, timestamp, None))
                        conn.commit()

                # Display output in the same window
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                label = Label(self.image_frame, image=image)
                label.image = image
                label.pack()

                # Show parking information
                messagebox.showinfo("Parking Information", f"License plate detected and saved to database!\n{parking_info}")

                # Display parking slots availability
                self.display_parking_slots()

                # Ask user for the next action
                user_response = messagebox.askyesno("Continue?", "Do you want to scan another image?")
                if user_response:
                    # Clear previous image
                    for widget in self.image_frame.winfo_children():
                        widget.destroy()
                    self.select_image()
                else:
                    self.root.quit()

    def display_exited_cars(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()

            # Clear previous exited cars list
            for widget in self.exited_cars_frame.winfo_children():
                widget.destroy()

            # Retrieve exited cars information
            c.execute("SELECT license_plate, time_in, time_out, duration FROM exited_cars ORDER BY time_out DESC LIMIT 10")
            exited_cars = c.fetchall()

            # Create and configure Text widget with Scrollbar
            text_widget = Text(self.exited_cars_frame, height=10, width=100)
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar = Scrollbar(self.exited_cars_frame, command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.config(yscrollcommand=scrollbar.set)

            # Insert exited cars information into Text widget
            for record in exited_cars:
                text_widget.insert("end", f"License Plate: {record[0]}\nTime In: {record[1]}\nTime Out: {record[2]}\nDuration: {record[3]}\n\n")

if __name__ == "__main__":
    detector = LicensePlateDetector()
