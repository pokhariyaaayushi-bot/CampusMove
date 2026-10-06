-- ====================================================================
-- CampusMove — Seed Dataset for Testing, Demonstrations & Viva
-- ====================================================================

-- 1. SEED STUDENTS / USERS (Password for all test accounts is 'CampusPass123!')
INSERT OR IGNORE INTO users (user_id, student_id, name, email, phone, department, password_hash, role) VALUES
(1, 24022832, 'Aayushi Pokhariya', 'aayushi@geu.ac.in', '+91-9876543201', 'CSE - Data Science', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'admin'),
(2, 24022541, 'Sharanya Rawat', 'sharanya@geu.ac.in', '+91-9876543202', 'CSE - Data Science', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'admin'),
(3, 24021866, 'Pushpesh Pandey', 'pushpesh@geu.ac.in', '+91-9876543203', 'CSE - Core', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'admin'),
(4, 24021990, 'Rohan Verma', 'rohan.v@student.geu.ac.in', '+91-9876543204', 'Computer Applications', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'student'),
(5, 24021995, 'Sneha Joshi', 'sneha.j@student.geu.ac.in', '+91-9876543205', 'Information Technology', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'student'),
(6, 24021998, 'Dr. Amit Saxena', 'amit.saxena@geu.ac.in', '+91-9876543206', 'Computer Science & Eng', 'scrypt:32768:8:1$uH3jX8wQn7mK$b411d355cf3bc4726e3c048c1aefb27d4ee79f64c62d05ea07ce11e3b6e792f6d671be68bdf4fcaae3a08d248b1bfcb03212871ad2f0c7e2d93e89542cbbdf99', 'student');

-- 2. SEED VEHICLES
INSERT OR IGNORE INTO vehicles (vehicle_id, registration_number, registration_no, model, vehicle_type, capacity, owner_type, availability_status, maintenance_status) VALUES
(1, 'UK-07-CM-1001', 'UK-07-CM-1001', 'Tata Starbus 40-Seater', 'Bus', 40, 'college', 'available', 'good'),
(2, 'UK-07-CM-1002', 'UK-07-CM-1002', 'Force Traveller 20-Seater', 'Mini Bus', 20, 'college', 'available', 'good'),
(3, 'UK-07-CM-1003', 'UK-07-CM-1003', 'Mahindra Bolero Electric Shuttle', 'Electric Shuttle', 8, 'college', 'available', 'good'),
(4, 'UK-07-CM-1004', 'UK-07-CM-1004', 'Swaraj Mazda Emergency Van', 'Van', 10, 'college', 'available', 'good'),
(5, 'UK-07-CM-1005', 'UK-07-CM-1005', 'Ashok Leyland 50-Seater', 'Heavy Bus', 50, 'college', 'maintenance', 'under_repair'),
(6, 'UK-07-PV-2001', 'UK-07-PV-2001', 'Maruti Suzuki Swift', 'Car', 4, 'private', 'available', 'good');

-- 3. SEED PRIVATE VEHICLES (Schema Completion)
INSERT OR IGNORE INTO private_vehicles (private_id, student_id, vehicle_id, available_seats) VALUES
(1, 4, 6, 3);

-- 4. SEED VEHICLE MAINTENANCE (Historical / Active)
INSERT OR IGNORE INTO maintenance (maintenance_id, vehicle_id, issue, start_date, end_date, status) VALUES
(1, 5, 'Brake pad replacement and transmission overhaul', '2026-09-20', '2026-09-25', 'in_progress'),
(2, 1, 'Routine engine oil and coolant replacement', '2026-09-10', '2026-09-11', 'completed');

-- 5. SEED DRIVERS
INSERT OR IGNORE INTO drivers (driver_id, name, phone, license_number, license_no, availability_status) VALUES
(1, 'Rajesh Kumar', '+91-9876543210', 'DL-UK07-2018-00987', 'DL-UK07-2018-00987', 'available'),
(2, 'Manoj Singh', '+91-9876543211', 'DL-UK07-2019-01123', 'DL-UK07-2019-01123', 'available'),
(3, 'Vikram Negi', '+91-9876543212', 'DL-UK07-2020-02345', 'DL-UK07-2020-02345', 'available'),
(4, 'Harish Rawat', '+91-9876543213', 'DL-UK07-2021-03456', 'DL-UK07-2021-03456', 'on_trip'),
(5, 'Suresh Chandra', '+91-9876543214', 'DL-UK07-2017-00543', 'DL-UK07-2017-00543', 'off_duty');

-- 6. SEED ROUTES
INSERT OR IGNORE INTO routes (route_id, route_name, origin, source, destination, distance_km, distance, estimated_duration_mins, estimated_time) VALUES
(1, 'Route 1: Central Hostel Express', 'Hostel Block A/B', 'Hostel Block A/B', 'Central Academic Complex', 2.8, 2.8, 12, 12),
(2, 'Route 2: Tech Campus Shuttle', 'Central Academic Complex', 'Central Academic Complex', 'Hillside Research Park', 4.5, 4.5, 20, 20),
(3, 'Route 3: Sports Arena Connector', 'Student Activity Center', 'Student Activity Center', 'North Sports Complex', 3.2, 3.2, 15, 15),
(4, 'Route 4: Medical Emergency Link', 'Campus Health Dispensary', 'Campus Health Dispensary', 'District Medical Center', 6.0, 6.0, 18, 18),
(5, 'Route 5: Main Gate Transit', 'Main Gate Bus Bay', 'Main Gate Bus Bay', 'Hostel Block C/D', 2.1, 2.1, 10, 10);

-- 7. SEED ROUTE STOPS
INSERT OR IGNORE INTO stops (stop_id, route_id, stop_name, sequence_no) VALUES
(1, 1, 'Hostel Block A Gate', 1),
(2, 1, 'Girls Hostel Junction', 2),
(3, 1, 'Central Academic Complex Bay', 3),
(4, 2, 'Central Library Roundabout', 1),
(5, 2, 'Mechanical Workshops Stop', 2),
(6, 2, 'Hillside Research Park Gate', 3);

-- 8. SEED CARPOOLS (Schema Completion)
INSERT OR IGNORE INTO carpools (carpool_id, driver_student_id, route_id, capacity, departure_time) VALUES
(1, 4, 1, 3, '08:45:00');

-- 9. SEED SCHEDULES
INSERT OR IGNORE INTO schedules (schedule_id, route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, status) VALUES
(1, 1, 1, 1, '08:30:00', '08:45:00', 'Morning Peak (08:30 - 08:45)', 'scheduled'),
(2, 2, 2, 2, '09:00:00', '09:20:00', 'Morning Session (09:00 - 09:20)', 'scheduled'),
(3, 3, 3, 3, '13:15:00', '13:30:00', 'Afternoon Transit (13:15 - 13:30)', 'scheduled'),
(4, 5, 2, 2, '17:30:00', '17:45:00', 'Evening Hostel Return (17:30 - 17:45)', 'scheduled');

-- 10. SEED TRANSPORT REQUESTS
INSERT OR IGNORE INTO transport_requests (request_id, student_id, route_id, requested_time, priority, purpose, status) VALUES
(1, 4, 1, '08:30:00', 'P3', 'Daily commute for 9 AM DBMS Lecture', 'allocated'),
(2, 5, 2, '09:00:00', 'P3', 'Lab session at Research Park', 'allocated'),
(3, 6, 2, '09:00:00', 'P2', 'Faculty inspection for ABET accreditation', 'allocated'),
(4, 4, 4, '11:00:00', 'P1', 'Emergency trip for severe sports sprain', 'pending');

-- 11. SEED BOOKINGS (Fulfilling Schedules & Requests)
INSERT OR IGNORE INTO bookings (booking_id, request_id, student_id, route_id, schedule_id, vehicle_id, seat_no, priority_level, purpose, requested_date, status) VALUES
(1, 1, 4, 1, 1, 1, 12, 'P3', 'Daily commute for 9 AM DBMS Lecture', '2026-09-23', 'confirmed'),
(2, 2, 5, 2, 2, 2, 5, 'P3', 'Lab session at Research Park', '2026-09-23', 'confirmed'),
(3, 3, 6, 2, 2, 2, 1, 'P2', 'Faculty inspection for ABET accreditation', '2026-09-23', 'confirmed'),
(4, 4, 4, 4, NULL, NULL, NULL, 'P1', 'Emergency trip for severe sports sprain', '2026-09-23', 'pending');
