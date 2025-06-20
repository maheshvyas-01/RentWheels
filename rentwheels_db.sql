SELECT @@SERVERNAME;
SELECT name FROM sys.databases WHERE name = 'RentWheels';
SELECT name FROM sys.databases;

CREATE DATABASE RentWheels;
USE RentWheels;
select * from Users;

CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    phone NVARCHAR(20),
    password_hash NVARCHAR(255) NOT NULL,
    is_admin BIT DEFAULT 0,  -- 0 for normal user, 1 for admin
    created_at DATETIME DEFAULT GETDATE()
);
---admin---
UPDATE Users 
SET is_admin = 1 
WHERE email = 'abcde@gmail.com';

UPDATE Users 
SET phone = '1112223330'  
WHERE user_id = 3;  -- Change 1 to the actual user_id




CREATE TABLE Cars (
    car_id INT IDENTITY(1,1) PRIMARY KEY,
    car_name NVARCHAR(255) NOT NULL,
    brand NVARCHAR(255) NOT NULL,
    model NVARCHAR(255) NOT NULL,
    year INT NOT NULL,
    price_per_day DECIMAL(10,2) NOT NULL,
    image_url NVARCHAR(500),  -- Store image path
    is_available BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);

USE RentWheels;
SELECT * FROM Cars;
SELECT image_url FROM Cars;

select * from Cars;
INSERT INTO Cars (car_name, brand, model, year, price_per_day, image_url)  
VALUES ('Tata Nexon', 'Tata', 'Nexon XZ+', 2023, 2500, 'nexon.jpg');  

INSERT INTO Cars (car_name, brand, model, year, price_per_day, image_url, is_available)
VALUES 
('Maruti Suzuki', 'Maruti Suzuki', 'Baleno Zeta', 2023, 1600.00, 'baleno.jpg', 5),
('Hyundai Creta', 'Hyundai', 'Creta SX', 2023, 2200.00, 'creta.jpg', 5),
('Maruti Suzuki', 'Maruti Suzuki', 'Ertiga ZDI+', 2023, 1800.00, 'ertiga.jpg', 5),
('Honda City', 'Honda', 'City VX', 2023, 2200.00, 'hondacity.jpg', 5),
('Jeep', 'Jeep', 'Compass Limited', 2023, 3500.00, 'jeepcompass.jpg', 5),
('Mahindra', 'Mahindra', 'XUV500 W10', 2023, 3000.00, 'xuv500.jpg', 5);


CREATE TABLE Bookings (
    booking_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES Users(user_id) ON DELETE CASCADE,
    car_id INT FOREIGN KEY REFERENCES Cars(car_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status NVARCHAR(50) DEFAULT 'Pending', -- Pending, Confirmed, Cancelled
    created_at DATETIME DEFAULT GETDATE()
);
select * from Bookings;

CREATE TABLE Payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT FOREIGN KEY REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    tax DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status NVARCHAR(50) DEFAULT 'Pending', -- Pending, Paid, Failed
    created_at DATETIME DEFAULT GETDATE()
);
select * from Payments;


CREATE TABLE ContactUs (
    message_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    message NVARCHAR(1000) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
select * from ContactUs;
