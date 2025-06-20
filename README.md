# 🚗 RentWheels – Car Rental Web Application

**RentWheels** is a modern and user-friendly car rental management system developed using **Flask**, **SQL Server**, and a sleek **HTML/CSS/JS frontend**. It allows users to browse, book, and manage car rentals while providing an admin dashboard for managing listings, users, messages, and bookings.

> 🔐 All sensitive credentials have been removed for security. Replace with your local database/server values to run.


📌 Key Features

👤 User Side
- 🔐 User registration & login
- 🚘 Browse available cars with images
- 📝 Book cars with selected dates
- 💳 Dummy payment gateway & payment summary
- 📄 Download invoice in PDF format
- 📅 View booking history
- 📩 Contact form (saved to database)

🛠️ Admin Side
- 📥 Login as admin
- 🚗 Add / Edit / Delete car listings
- 👥 View & delete non-admin users
- 📬 View messages from contact form
- 📊 View bookings
- 🔧 Basic dashboard tools


🧰 Tech Stack

| Tech | Description |
|------|-------------|
| 🐍 Python (Flask) | Backend framework |
| 🧾 SQL Server (SSMS 19) | Database management |
| 🎨 HTML5 / CSS3 | Web page design |
| 🧠 JavaScript | Interactivity |
| 🧩 Jinja2 | Template rendering |
| 🖨️ REPORTLab | Invoice generation |
| 🔗 PyODBC | Python to SQL connection |


📁 Project Structure

📂 RentWheels/
│── 📂 templates/
│   │── about.html
│   │── add_car.html
│   │── base.html
│   │── admin.html
│   │── book_car.html
|   │── car_listings.html
│   │── contact.html
│   │── edit_car.html
│   │── faq.html
│   │── index.html
│   │── login.html
│   │── manage_cars.html
│   │── manage_users.html
│   │── my_bookings.html
│   │── payment_success.html
│   │── payment_summary.html
│   │── register.html
│   │── view_bookings.html
│   │── view_messages.html
│
│── 📂 static/
│   │── 📂 images/
│   │   │── 📂 cars/
│   │   |   │── (car images)
│   │   │── 📂 invoices/
│   │   |   │── (invoice pdfs)
│   │── 📂 js/
│   │   │── script.js
│   │── 📂 css/
|       |──style.css
|
│── 📂 _pycache_/
│   │── app.cpython-39.pyc
│   │── app_routes.cpython-39.pyc
│   │── db_connection.cpython-39.pyc
|
│── app.py
│── app_routes.py
│── db_connection.py
│── models.py
│── test_db.py
│── rentwheels_db.sql
│── requirements.txt
│── README.md   


🚀 How to Run the Project Locally

1. **Clone this repository**
   ```bash
   
   git clone https://github.com/YOUR_USERNAME/RentWheels.git
   cd RentWheels
   
2.Set up virtual environment (optional)

python -m venv venv
venv\Scripts\activate

3.Install required packages

pip install -r requirements.txt

4.Update DB credentials

Open db_connection.py
Replace placeholder values (abc123, etc.) with your actual SQL Server name

5.Run the application

python app.py

6.Open in browser

http://127.0.0.1:5000


🛠️ Database Setup
Open rentwheels_db.sql in SQL Server Management Studio
Execute the SQL script to create tables and dummy data
Ensure Trusted_Connection=yes if you're using Windows Authentication

SCREENSHOTS:

You can find all the screenshots of output in the "screenshots" folder, thank you:}


📄 License
This project is licensed under the MIT License
Free to use, modify, and distribute with credit.


🙋‍♂️ About the Developer

👨‍💻 Mahesh Vyas

🎓 First Year MCA Student

💼 Passionate about Web Development, Python Full Stack

📫 LinkedIn https://www.linkedin.com/in/vyasmahesh

📧 vyasmahesh@gmail.com 

⭐ Support & Feedback
If you like this project, consider giving it a ⭐ star on GitHub.
Have suggestions or issues? Open an issue or reach out!
