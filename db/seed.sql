-- ====================================================================
-- CampusMove — Seed Dataset for Testing, Demonstrations & Viva
-- ====================================================================

-- 1. SEED STUDENTS / USERS (Password for all test accounts is 'CampusPass123!')
INSERT IGNORE INTO users (user_id, student_id, name, email, phone, department, password_hash, role) VALUES
(1, 24022832, 'Aayushi Pokhariya', 'aayushi@geu.ac.in', '+91-9876543201', 'CSE - Data Science', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'admin'),
(2, 24022541, 'Sharanya Rawat', 'sharanya@geu.ac.in', '+91-9876543202', 'CSE - Data Science', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'admin'),
(3, 24021866, 'Pushpesh Pandey', 'pushpesh@geu.ac.in', '+91-9876543203', 'CSE - Core', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'admin'),
(4, 24021990, 'Rohan Verma', 'rohan.v@student.geu.ac.in', '+91-9876543204', 'Computer Applications', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(5, 24021995, 'Sneha Joshi', 'sneha.j@student.geu.ac.in', '+91-9876543205', 'Information Technology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(6, 24021998, 'Amit Saxena', 'amit.saxena@geu.ac.in', '+91-9876543206', 'Computer Science & Eng', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'faculty');

-- 2. SEED VEHICLES (15 Route Fleet + 3 Emergency Vehicles + 1 Private Car)
INSERT IGNORE INTO vehicles (vehicle_id, registration_number, registration_no, model, vehicle_type, capacity, owner_type, availability_status, maintenance_status) VALUES
(1, 'UK-07-CM-1001', 'UK-07-CM-1001', 'Tata Starbus 40-Seater', 'Bus', 40, 'college', 'available', 'good'),
(2, 'UK-07-CM-1002', 'UK-07-CM-1002', 'Force Traveller 20-Seater', 'Mini Bus', 20, 'college', 'available', 'good'),
(3, 'UK-07-CM-1003', 'UK-07-CM-1003', 'Mahindra Bolero Electric Shuttle', 'Electric Shuttle', 8, 'college', 'available', 'good'),
(4, 'UK-07-CM-1004', 'UK-07-CM-1004', 'Swaraj Mazda Medical Shuttle', 'Mini Bus', 14, 'college', 'available', 'good'),
(5, 'UK-07-CM-1005', 'UK-07-CM-1005', 'Ashok Leyland Campus Coach 45-Seater', 'Bus', 45, 'college', 'available', 'good'),
(6, 'UK-07-CM-1006', 'UK-07-CM-1006', 'Eicher Skyline City Bus 35-Seater', 'Bus', 35, 'college', 'available', 'good'),
(7, 'UK-07-CM-1007', 'UK-07-CM-1007', 'Force Urbania Shuttle 16-Seater', 'Mini Bus', 16, 'college', 'available', 'good'),
(8, 'UK-07-CM-1008', 'UK-07-CM-1008', 'Tata Winger Express 12-Seater', 'Van', 12, 'college', 'available', 'good'),
(9, 'UK-07-CM-1009', 'UK-07-CM-1009', 'BharatBenz Campus Transit 40-Seater', 'Bus', 40, 'college', 'available', 'good'),
(10, 'UK-07-CM-1010', 'UK-07-CM-1010', 'Mahindra Tourister 25-Seater', 'Mini Bus', 25, 'college', 'available', 'good'),
(11, 'UK-07-CM-1011', 'UK-07-CM-1011', 'Tata Marcopolo 32-Seater', 'Bus', 32, 'college', 'available', 'good'),
(12, 'UK-07-CM-1012', 'UK-07-CM-1012', 'Ashok Leyland Oyster 30-Seater', 'Bus', 30, 'college', 'available', 'good'),
(13, 'UK-07-CM-1013', 'UK-07-CM-1013', 'Force Citiline 10-Seater', 'Mini Bus', 10, 'college', 'available', 'good'),
(14, 'UK-07-CM-1014', 'UK-07-CM-1014', 'Tata Cityride 34-Seater', 'Bus', 34, 'college', 'available', 'good'),
(15, 'UK-07-CM-1015', 'UK-07-CM-1015', 'SML Isuzu Prestige 28-Seater', 'Bus', 28, 'college', 'available', 'good'),
-- Emergency Fleet for P1 Requests (Ambulance, Car, Van)
(16, 'UK-07-EM-3001', 'UK-07-EM-3001', 'Graphic Era LifeLine Ambulance', 'Ambulance', 2, 'college', 'available', 'good'),
(17, 'UK-07-EM-3002', 'UK-07-EM-3002', 'Campus Rapid Response Medical Car', 'Car', 4, 'college', 'available', 'good'),
(18, 'UK-07-EM-3003', 'UK-07-EM-3003', 'Campus Emergency Transit Van', 'Van', 8, 'college', 'available', 'good'),
-- Private Vehicle
(19, 'UK-07-PV-2001', 'UK-07-PV-2001', 'Maruti Suzuki Swift', 'Car', 4, 'private', 'available', 'good'),
-- Dedicated Unassigned Standby Fleet Vehicles (Not assigned to any path / route)
(20, 'UK-07-SB-4001', 'UK-07-SB-4001', 'Reserve Standby Coach 40-Seater', 'Bus', 40, 'college', 'available', 'good'),
(21, 'UK-07-SB-4002', 'UK-07-SB-4002', 'Campus Relief Shuttle 25-Seater', 'Mini Bus', 25, 'college', 'available', 'good'),
(22, 'UK-07-SB-4003', 'UK-07-SB-4003', 'Reserve Standby Starbus 32-Seater', 'Bus', 32, 'college', 'available', 'good');

-- 3. SEED PRIVATE VEHICLES (Schema Completion)
INSERT IGNORE INTO private_vehicles (private_id, student_id, vehicle_id, available_seats) VALUES
(1, 4, 19, 3);

-- 4. SEED VEHICLE MAINTENANCE (Historical / Active)
INSERT IGNORE INTO maintenance (maintenance_id, vehicle_id, issue, start_date, end_date, status) VALUES
(1, 5, 'Brake pad inspection and transmission tune-up', '2026-09-20', '2026-09-25', 'completed'),
(2, 1, 'Routine engine oil and coolant replacement', '2026-09-10', '2026-09-11', 'completed');

-- 5. SEED 15 DISTINCT DRIVERS FOR 15 ROUTES + 3 EMERGENCY DRIVERS
INSERT IGNORE INTO drivers (driver_id, name, phone, license_number, license_no, availability_status) VALUES
(1, 'Rajesh Kumar', '+91-9876543210', 'DL-UK07-2018-00987', 'DL-UK07-2018-00987', 'available'),
(2, 'Manoj Singh', '+91-9876543211', 'DL-UK07-2019-01123', 'DL-UK07-2019-01123', 'available'),
(3, 'Vikram Negi', '+91-9876543212', 'DL-UK07-2020-02345', 'DL-UK07-2020-02345', 'available'),
(4, 'Harish Rawat', '+91-9876543213', 'DL-UK07-2021-03456', 'DL-UK07-2021-03456', 'available'),
(5, 'Suresh Chandra', '+91-9876543214', 'DL-UK07-2017-00543', 'DL-UK07-2017-00543', 'available'),
(6, 'Ramesh Chauhan', '+91-9876543215', 'DL-UK07-2018-00654', 'DL-UK07-2018-00654', 'available'),
(7, 'Sunil Sharma', '+91-9876543216', 'DL-UK07-2019-00765', 'DL-UK07-2019-00765', 'available'),
(8, 'Deepak Joshi', '+91-9876543217', 'DL-UK07-2020-00876', 'DL-UK07-2020-00876', 'available'),
(9, 'Anil Bhatt', '+91-9876543218', 'DL-UK07-2021-00987', 'DL-UK07-2021-00987', 'available'),
(10, 'Pradeep Thapa', '+91-9876543219', 'DL-UK07-2022-01098', 'DL-UK07-2022-01098', 'available'),
(11, 'Sanjay Verma', '+91-9876543220', 'DL-UK07-2018-01109', 'DL-UK07-2018-01109', 'available'),
(12, 'Devendra Rana', '+91-9876543221', 'DL-UK07-2019-01210', 'DL-UK07-2019-01210', 'available'),
(13, 'Kuldeep Negi', '+91-9876543222', 'DL-UK07-2020-01321', 'DL-UK07-2020-01321', 'available'),
(14, 'Vijay Pal', '+91-9876543223', 'DL-UK07-2021-01432', 'DL-UK07-2021-01432', 'available'),
(15, 'Mahesh Bisht', '+91-9876543224', 'DL-UK07-2022-01543', 'DL-UK07-2022-01543', 'available'),
-- Emergency Drivers for P1 (Ambulance, Medical Car, Response Van)
(16, 'Mohan Ram (Ambulance)', '+91-9876543225', 'DL-UK07-2016-01654', 'DL-UK07-2016-01654', 'available'),
(17, 'Prakash Pant (Medical Car)', '+91-9876543226', 'DL-UK07-2017-01765', 'DL-UK07-2017-01765', 'available'),
(18, 'Naresh Thapa (Response Van)', '+91-9876543227', 'DL-UK07-2018-01876', 'DL-UK07-2018-01876', 'available'),
-- Dedicated Unassigned Standby Drivers (Not assigned to any path / route)
(19, 'Reserve Driver Ajay', '+91-9876543230', 'DL-UK07-2022-02001', 'DL-UK07-2022-02001', 'available'),
(20, 'Reserve Driver Sanjay', '+91-9876543231', 'DL-UK07-2022-02002', 'DL-UK07-2022-02002', 'available'),
(21, 'Reserve Driver Vijay', '+91-9876543232', 'DL-UK07-2022-02003', 'DL-UK07-2022-02003', 'available');

-- 6. SEED ALL 15 TRANSIT ROUTES
INSERT IGNORE INTO routes (route_id, route_name, origin, source, destination, distance_km, distance, estimated_duration_mins, estimated_time) VALUES
(1, 'Route 1: Premnagar Main Market ↔ Graphic Era Parking / Bus Stop', 'Premnagar Main Market', 'Premnagar Main Market', 'Graphic Era Parking / Bus Stop', 14.0, 14.0, 35, 35),
(2, 'Route 2: Clock Tower ↔ Graphic Era Parking / Bus Stop', 'Clock Tower (Ghanta Ghar)', 'Clock Tower (Ghanta Ghar)', 'Graphic Era Parking / Bus Stop', 8.5, 8.5, 25, 25),
(3, 'Route 3: Clement Town ↔ Graphic Era Parking / Bus Stop', 'Clement Town Market', 'Clement Town Market', 'Graphic Era Parking / Bus Stop', 6.0, 6.0, 18, 18),
(4, 'Route 4: Graphic Era Hospital (GEIMS) ↔ Graphic Era Parking / Bus Stop', 'Graphic Era Hospital (GEIMS)', 'Graphic Era Hospital (GEIMS)', 'Graphic Era Parking / Bus Stop', 4.5, 4.5, 15, 15),
(5, 'Route 5: Ballupur Chowk ↔ Graphic Era Parking / Bus Stop', 'Ballupur Chowk', 'Ballupur Chowk', 'Graphic Era Parking / Bus Stop', 8.0, 8.0, 23, 23),
(6, 'Route 6: Saharanpur Chowk ↔ Graphic Era Parking / Bus Stop', 'Saharanpur Chowk', 'Saharanpur Chowk', 'Graphic Era Parking / Bus Stop', 10.0, 10.0, 28, 28),
(7, 'Route 7: Patel Nagar ↔ Graphic Era Parking / Bus Stop', 'Patel Nagar', 'Patel Nagar', 'Graphic Era Parking / Bus Stop', 9.0, 9.0, 25, 25),
(8, 'Route 8: Rajpur Road ↔ Graphic Era Parking / Bus Stop', 'Rajpur Road', 'Rajpur Road', 'Graphic Era Parking / Bus Stop', 14.0, 14.0, 35, 35),
(9, 'Route 9: UPES Bidholi ↔ Graphic Era Parking / Bus Stop', 'UPES / Bidholi Junction', 'UPES / Bidholi Junction', 'Graphic Era Parking / Bus Stop', 20.0, 20.0, 50, 50),
(10, 'Route 10: IMA Main Gate ↔ Graphic Era Parking / Bus Stop', 'IMA Main Gate', 'IMA Main Gate', 'Graphic Era Parking / Bus Stop', 12.0, 12.0, 30, 30),
(11, 'Route 11: FRI (Forest Research Institute) ↔ Graphic Era Parking / Bus Stop', 'FRI Gate', 'FRI Gate', 'Graphic Era Parking / Bus Stop', 11.0, 11.0, 28, 28),
(12, 'Route 12: Mokhampur / Mohkampur ↔ Graphic Era Parking / Bus Stop', 'Mohkampur Chowk', 'Mohkampur Chowk', 'Graphic Era Parking / Bus Stop', 10.5, 10.5, 25, 25),
(13, 'Route 13: Jolly Grant (Airport) ↔ Graphic Era Parking / Bus Stop', 'Jolly Grant Airport', 'Jolly Grant Airport', 'Graphic Era Parking / Bus Stop', 28.0, 28.0, 55, 55),
(14, 'Route 14: ISBT Dehradun ↔ Graphic Era Parking / Bus Stop', 'ISBT Dehradun', 'ISBT Dehradun', 'Graphic Era Parking / Bus Stop', 4.5, 4.5, 12, 12),
(15, 'Route 15: Doiwala ↔ Graphic Era Parking / Bus Stop', 'Doiwala Chowk', 'Doiwala Chowk', 'Graphic Era Parking / Bus Stop', 22.0, 22.0, 45, 45);

-- Synchronize the primary route catalogue when seed data is re-applied to an
-- existing demonstration database. Every route is an external commuter corridor.
UPDATE routes SET route_name = 'Route 1: Premnagar Main Market ↔ Graphic Era Parking / Bus Stop', origin = 'Premnagar Main Market', source = 'Premnagar Main Market', destination = 'Graphic Era Parking / Bus Stop', distance_km = 14.0, distance = 14.0, estimated_duration_mins = 35, estimated_time = 35 WHERE route_id = 1;
UPDATE routes SET route_name = 'Route 2: Clock Tower ↔ Graphic Era Parking / Bus Stop', origin = 'Clock Tower (Ghanta Ghar)', source = 'Clock Tower (Ghanta Ghar)', destination = 'Graphic Era Parking / Bus Stop', distance_km = 8.5, distance = 8.5, estimated_duration_mins = 25, estimated_time = 25 WHERE route_id = 2;
UPDATE routes SET route_name = 'Route 3: Clement Town ↔ Graphic Era Parking / Bus Stop', origin = 'Clement Town Market', source = 'Clement Town Market', destination = 'Graphic Era Parking / Bus Stop', distance_km = 6.0, distance = 6.0, estimated_duration_mins = 18, estimated_time = 18 WHERE route_id = 3;
UPDATE routes SET route_name = 'Route 4: Graphic Era Hospital (GEIMS) ↔ Graphic Era Parking / Bus Stop', origin = 'Graphic Era Hospital (GEIMS)', source = 'Graphic Era Hospital (GEIMS)', destination = 'Graphic Era Parking / Bus Stop', distance_km = 4.5, distance = 4.5, estimated_duration_mins = 15, estimated_time = 15 WHERE route_id = 4;
UPDATE routes SET route_name = 'Route 5: Ballupur Chowk ↔ Graphic Era Parking / Bus Stop', origin = 'Ballupur Chowk', source = 'Ballupur Chowk', destination = 'Graphic Era Parking / Bus Stop', distance_km = 8.0, distance = 8.0, estimated_duration_mins = 23, estimated_time = 23 WHERE route_id = 5;
UPDATE routes SET route_name = 'Route 6: Saharanpur Chowk ↔ Graphic Era Parking / Bus Stop', origin = 'Saharanpur Chowk', source = 'Saharanpur Chowk', destination = 'Graphic Era Parking / Bus Stop', distance_km = 10.0, distance = 10.0, estimated_duration_mins = 28, estimated_time = 28 WHERE route_id = 6;
UPDATE routes SET route_name = 'Route 7: Patel Nagar ↔ Graphic Era Parking / Bus Stop', origin = 'Patel Nagar', source = 'Patel Nagar', destination = 'Graphic Era Parking / Bus Stop', distance_km = 9.0, distance = 9.0, estimated_duration_mins = 25, estimated_time = 25 WHERE route_id = 7;
UPDATE routes SET route_name = 'Route 8: Rajpur Road ↔ Graphic Era Parking / Bus Stop', origin = 'Rajpur Road', source = 'Rajpur Road', destination = 'Graphic Era Parking / Bus Stop', distance_km = 14.0, distance = 14.0, estimated_duration_mins = 35, estimated_time = 35 WHERE route_id = 8;
UPDATE routes SET route_name = 'Route 9: UPES Bidholi ↔ Graphic Era Parking / Bus Stop', origin = 'UPES / Bidholi Junction', source = 'UPES / Bidholi Junction', destination = 'Graphic Era Parking / Bus Stop', distance_km = 20.0, distance = 20.0, estimated_duration_mins = 50, estimated_time = 50 WHERE route_id = 9;
UPDATE routes SET route_name = 'Route 10: IMA Main Gate ↔ Graphic Era Parking / Bus Stop', origin = 'IMA Main Gate', source = 'IMA Main Gate', destination = 'Graphic Era Parking / Bus Stop', distance_km = 12.0, distance = 12.0, estimated_duration_mins = 30, estimated_time = 30 WHERE route_id = 10;

-- 7. SEED ROUTE STOPS (Complete coverage for all 15 university transit routes)
INSERT IGNORE INTO stops (stop_id, route_id, stop_name, sequence_no) VALUES
-- Route 1
(1, 1, 'Premnagar Main Market', 1),
(2, 1, 'Mandi Chowk', 2),
(3, 1, 'Graphic Era Parking / Bus Stop', 3),
-- Route 2
(4, 2, 'Clock Tower (Ghanta Ghar)', 1),
(5, 2, 'Paltan Bazaar Chowk', 2),
(6, 2, 'Graphic Era Parking / Bus Stop', 3),
-- Route 3
(7, 3, 'Clement Town Market Main Gate', 1),
(8, 3, 'Post Office Stop', 2),
(9, 3, 'Graphic Era Parking / Bus Stop', 3),
-- Route 4
(10, 4, 'Graphic Era Hospital (GEIMS) Emergency Bay', 1),
(11, 4, 'Subhash Nagar Emergency Cut', 2),
(12, 4, 'Graphic Era Parking / Bus Stop', 3),
-- Route 5
(13, 5, 'Ballupur Chowk Junction', 1),
(14, 5, 'GMS Road (Kamla Palace)', 2),
(15, 5, 'Graphic Era Parking / Bus Stop', 3),
-- Route 6
(16, 6, 'Saharanpur Chowk', 1),
(17, 6, 'Patel Nagar Crossing', 2),
(18, 6, 'ISBT Dehradun', 3),
(19, 6, 'Graphic Era Parking / Bus Stop', 4),
-- Route 7
(20, 7, 'Patel Nagar Market', 1),
(21, 7, 'Nehru Colony', 2),
(22, 7, 'Graphic Era Parking / Bus Stop', 3),
-- Route 8
(23, 8, 'Rajpur Road', 1),
(24, 8, 'Mussoorie Diversion', 2),
(25, 8, 'Graphic Era Parking / Bus Stop', 3),
-- Route 9
(26, 9, 'UPES / Bidholi Junction', 1),
(27, 9, 'Premnagar Junction', 2),
(28, 9, 'IMA North Gate', 3),
(29, 9, 'Graphic Era Parking / Bus Stop', 4),
-- Route 10
(30, 10, 'IMA Main Gate', 1),
(31, 10, 'Panditwari Crossing', 2),
(32, 10, 'Graphic Era Parking / Bus Stop', 3),
-- Route 11
(33, 11, 'FRI Main Gate', 1),
(34, 11, 'Kaulagarh Road', 2),
(35, 11, 'Graphic Era Parking / Bus Stop', 3),
-- Route 12
(36, 12, 'Mohkampur Chowk', 1),
(37, 12, 'Vidhan Sabha Crossing', 2),
(38, 12, 'Graphic Era Parking / Bus Stop', 3),
-- Route 13
(39, 13, 'Jolly Grant Airport Terminal', 1),
(40, 13, 'Bhaniawala Junction', 2),
(41, 13, 'Rispana Bridge Point', 3),
(42, 13, 'Graphic Era Parking / Bus Stop', 4),
-- Route 14
(43, 14, 'ISBT Dehradun Platform Bay', 1),
(44, 14, 'Transport Nagar Cut', 2),
(45, 14, 'Graphic Era Parking / Bus Stop', 3),
-- Route 15
(46, 15, 'Doiwala Chowk', 1),
(47, 15, 'Haridwar Highway Flyover', 2),
(48, 15, 'Graphic Era Parking / Bus Stop', 3);

-- Keep stops synchronized when this seed is applied to an existing database.
UPDATE stops SET stop_name = 'Premnagar Main Market' WHERE stop_id = 1;
UPDATE stops SET stop_name = 'Mandi Chowk' WHERE stop_id = 2;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 3;
UPDATE stops SET stop_name = 'Clock Tower (Ghanta Ghar)' WHERE stop_id = 4;
UPDATE stops SET stop_name = 'Paltan Bazaar Chowk' WHERE stop_id = 5;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 6;
UPDATE stops SET stop_name = 'Clement Town Market Main Gate' WHERE stop_id = 7;
UPDATE stops SET stop_name = 'Post Office Stop' WHERE stop_id = 8;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 9;
UPDATE stops SET stop_name = 'Graphic Era Hospital (GEIMS) Emergency Bay' WHERE stop_id = 10;
UPDATE stops SET stop_name = 'Subhash Nagar Emergency Cut' WHERE stop_id = 11;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 12;
UPDATE stops SET stop_name = 'Ballupur Chowk Junction' WHERE stop_id = 13;
UPDATE stops SET stop_name = 'GMS Road (Kamla Palace)' WHERE stop_id = 14;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 15;
UPDATE stops SET stop_name = 'Saharanpur Chowk' WHERE stop_id = 16;
UPDATE stops SET stop_name = 'Patel Nagar Crossing' WHERE stop_id = 17;
UPDATE stops SET stop_name = 'ISBT Dehradun' WHERE stop_id = 18;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 19;
UPDATE stops SET stop_name = 'Patel Nagar Market' WHERE stop_id = 20;
UPDATE stops SET stop_name = 'Nehru Colony' WHERE stop_id = 21;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 22;
UPDATE stops SET stop_name = 'Rajpur Road' WHERE stop_id = 23;
UPDATE stops SET stop_name = 'Mussoorie Diversion' WHERE stop_id = 24;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 25;
UPDATE stops SET stop_name = 'UPES / Bidholi Junction' WHERE stop_id = 26;
UPDATE stops SET stop_name = 'Premnagar Junction' WHERE stop_id = 27;
UPDATE stops SET stop_name = 'IMA North Gate' WHERE stop_id = 28;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 29;
UPDATE stops SET stop_name = 'IMA Main Gate' WHERE stop_id = 30;
UPDATE stops SET stop_name = 'Panditwari Crossing' WHERE stop_id = 31;
UPDATE stops SET stop_name = 'Graphic Era Parking / Bus Stop' WHERE stop_id = 32;

-- 8. SEED CARPOOLS (Schema Completion)
INSERT IGNORE INTO carpools (carpool_id, driver_student_id, route_id, capacity, departure_time) VALUES
(1, 4, 1, 3, '08:45:00');

-- 9. SEED SCHEDULES (Multiple Departures per Route, Inbound/Outbound Directions & Vehicle Chaining) + 3 Emergency Standbys
INSERT IGNORE INTO schedules (schedule_id, route_id, vehicle_id, driver_id, departure_time, arrival_time, time_window, direction, status) VALUES
-- Primary Morning Inbound Runs (Routes 1-15)
(1, 1, 1, 1, '08:30:00', '08:45:00', 'Morning Peak (08:30 - 08:45)', 'inbound', 'scheduled'),
(2, 2, 2, 2, '09:00:00', '09:20:00', 'Morning Session (09:00 - 09:20)', 'inbound', 'scheduled'),
(3, 3, 3, 3, '13:15:00', '13:30:00', 'Afternoon Transit (13:15 - 13:30)', 'inbound', 'scheduled'),
(4, 4, 4, 4, '10:00:00', '10:15:00', 'GEIMS Medical Corridor (10:00 - 10:15)', 'inbound', 'scheduled'),
(5, 5, 5, 5, '17:30:00', '17:55:00', 'Ballupur Evening Return (17:30 - 17:55)', 'outbound', 'scheduled'),
(6, 6, 6, 6, '08:00:00', '08:28:00', 'Saharanpur Morning Run (08:00 - 08:28)', 'inbound', 'scheduled'),
(7, 7, 7, 7, '08:15:00', '08:40:00', 'Patel Nagar Morning Run (08:15 - 08:40)', 'inbound', 'scheduled'),
(8, 8, 8, 8, '07:45:00', '08:20:00', 'Rajpur Road Morning Run (07:45 - 08:20)', 'inbound', 'scheduled'),
(9, 9, 9, 9, '07:30:00', '08:20:00', 'Bidholi Express (07:30 - 08:20)', 'inbound', 'scheduled'),
(10, 10, 10, 10, '07:40:00', '08:10:00', 'IMA Gate Morning Run (07:40 - 08:10)', 'inbound', 'scheduled'),
(11, 11, 11, 11, '07:50:00', '08:25:00', 'FRI Heritage Run (07:50 - 08:25)', 'inbound', 'scheduled'),
(12, 12, 12, 12, '08:00:00', '08:30:00', 'Mokhampur Link (08:00 - 08:30)', 'inbound', 'scheduled'),
(13, 13, 13, 13, '07:00:00', '08:15:00', 'Airport Express (07:00 - 08:15)', 'inbound', 'scheduled'),
(14, 14, 14, 14, '08:10:00', '08:30:00', 'ISBT Connector (08:10 - 08:30)', 'inbound', 'scheduled'),
(15, 15, 15, 15, '07:15:00', '08:15:00', 'Doiwala Superfast (07:15 - 08:15)', 'inbound', 'scheduled'),
-- 24x7 Emergency Standbys for P1 Priority
(16, 4, 16, 16, '00:00:00', '23:59:00', '24x7 Emergency Ambulance Link', 'inbound', 'scheduled'),
(17, 4, 17, 17, '00:00:00', '23:59:00', '24x7 Emergency Medical Car', 'inbound', 'scheduled'),
(18, 4, 18, 18, '00:00:00', '23:59:00', '24x7 Emergency Transit Van', 'inbound', 'scheduled'),
-- Multiple Departures & Vehicle Chaining (§2.1 & §2.5)
-- Route 9: Bidholi Multiple Departures (Vehicle 9 Chaining)
(19, 9, 9, 9, '11:00:00', '11:40:00', 'Late Morning (11:00 - 11:40)', 'inbound', 'scheduled'),
(20, 9, 9, 9, '15:00:00', '15:45:00', 'Afternoon Departure (15:00 - 15:45)', 'outbound', 'scheduled'),
(21, 9, 9, 9, '16:00:00', '16:45:00', 'Evening Batch 1 (16:00 - 16:45)', 'outbound', 'scheduled'),
(22, 9, 9, 9, '17:00:00', '17:45:00', 'Evening Batch 2 (17:00 - 17:45)', 'outbound', 'scheduled'),
(23, 9, 9, 9, '18:00:00', '18:45:00', 'Last Bus Return (18:00 - 18:45)', 'outbound', 'scheduled'),
-- Route 15: Doiwala Multiple Departures (Vehicle 15 Chaining)
(24, 15, 15, 15, '10:45:00', '11:45:00', 'Late Morning (10:45 - 11:45)', 'inbound', 'scheduled'),
(25, 15, 15, 15, '15:00:00', '16:00:00', 'Afternoon Return (15:00 - 16:00)', 'outbound', 'scheduled'),
(26, 15, 15, 15, '17:00:00', '18:00:00', 'Evening Return (17:00 - 18:00)', 'outbound', 'scheduled'),
(27, 15, 15, 15, '18:00:00', '19:00:00', 'Night Express (18:00 - 19:00)', 'outbound', 'scheduled'),
-- Route 6: Saharanpur Multiple Departures (Vehicle 6 Chaining)
(28, 6, 6, 6, '11:15:00', '11:43:00', 'Midday Saharanpur Run (11:15 - 11:43)', 'inbound', 'scheduled'),
(29, 6, 6, 6, '15:30:00', '16:00:00', 'Afternoon Return (15:30 - 16:00)', 'outbound', 'scheduled'),
(30, 6, 6, 6, '17:30:00', '17:58:00', 'Evening Saharanpur Return (17:30 - 17:58)', 'outbound', 'scheduled'),
-- Route 1: Premnagar Multiple Departures (Vehicle 1 Chaining)
(31, 1, 1, 1, '11:30:00', '12:05:00', 'Midday Premnagar Run (11:30 - 12:05)', 'inbound', 'scheduled'),
(32, 1, 1, 1, '14:00:00', '14:35:00', 'Afternoon Premnagar Run (14:00 - 14:35)', 'outbound', 'scheduled'),
(33, 1, 1, 1, '17:15:00', '17:50:00', 'Evening Premnagar Return (17:15 - 17:50)', 'outbound', 'scheduled');

-- Existing MySQL databases keep their schedule labels and directions current too.
UPDATE schedules SET arrival_time = '10:15:00', time_window = 'GEIMS Medical Corridor (10:00 - 10:15)', direction = 'inbound' WHERE schedule_id = 4;
UPDATE schedules SET arrival_time = '17:55:00', time_window = 'Ballupur Evening Return (17:30 - 17:55)' WHERE schedule_id = 5;
UPDATE schedules SET arrival_time = '08:28:00', time_window = 'Saharanpur Morning Run (08:00 - 08:28)', direction = 'inbound' WHERE schedule_id = 6;
UPDATE schedules SET arrival_time = '08:40:00', time_window = 'Patel Nagar Morning Run (08:15 - 08:40)', direction = 'inbound' WHERE schedule_id = 7;
UPDATE schedules SET arrival_time = '08:20:00', time_window = 'Rajpur Road Morning Run (07:45 - 08:20)', direction = 'inbound' WHERE schedule_id = 8;
UPDATE schedules SET arrival_time = '08:20:00', time_window = 'Bidholi Express (07:30 - 08:20)', direction = 'inbound' WHERE schedule_id = 9;
UPDATE schedules SET arrival_time = '08:10:00', time_window = 'IMA Gate Morning Run (07:40 - 08:10)', direction = 'inbound' WHERE schedule_id = 10;
UPDATE schedules SET arrival_time = '11:43:00', time_window = 'Midday Saharanpur Run (11:15 - 11:43)', direction = 'inbound' WHERE schedule_id = 28;
UPDATE schedules SET arrival_time = '17:58:00', time_window = 'Evening Saharanpur Return (17:30 - 17:58)' WHERE schedule_id = 30;
UPDATE schedules SET arrival_time = '12:05:00', time_window = 'Midday Premnagar Run (11:30 - 12:05)' WHERE schedule_id = 31;
UPDATE schedules SET arrival_time = '14:35:00', time_window = 'Afternoon Premnagar Run (14:00 - 14:35)' WHERE schedule_id = 32;
UPDATE schedules SET arrival_time = '17:50:00', time_window = 'Evening Premnagar Return (17:15 - 17:50)' WHERE schedule_id = 33;
UPDATE bookings SET purpose = 'Saharanpur Return Shuttle' WHERE booking_id = 5;

-- 10. SEED TRANSPORT REQUESTS
INSERT IGNORE INTO transport_requests (request_id, student_id, route_id, requested_time, priority, purpose, status) VALUES
(1, 4, 2, '09:00:00', 'P3', 'CSIT Lab Session Commute', 'allocated'),
(2, 5, 2, '09:00:00', 'P3', 'Data Science Lecture Commute', 'allocated'),
(3, 4, 1, '08:30:00', 'P3', 'Regular Morning Commute to Campus', 'allocated'),
(4, 6, 1, '08:30:00', 'P2', 'Faculty Assistant Duty in Block A', 'allocated'),
(5, 4, 4, '14:00:00', 'P1', '[EMERGENCY - AMBULANCE] Severe allergic reaction requiring emergency dispensary transfer', 'pending'),
(6, 5, 3, '13:15:00', 'P3', 'Sports Arena Practice Session', 'pending');

-- 11. SEED BOOKINGS (In Route, Confirmed, Completed, Cancelled)
INSERT IGNORE INTO bookings (booking_id, request_id, student_id, route_id, schedule_id, vehicle_id, seat_no, priority_level, purpose, requested_date, status) VALUES
(1, 1, 4, 2, 2, 2, 11, 'P3', 'CSIT Lab Session Commute', '2026-10-30', 'in_route'),
(2, 2, 5, 2, 2, 2, 12, 'P3', 'Data Science Lecture Commute', '2026-10-30', 'in_route'),
(3, 3, 4, 1, 1, 1, 11, 'P3', 'Regular Morning Commute to Campus', '2026-10-30', 'confirmed'),
(4, 4, 6, 1, 1, 1, 1, 'P2', 'Faculty Assistant Duty in Block A', '2026-10-30', 'confirmed'),
(5, NULL, 4, 6, 6, 6, 14, 'P3', 'Saharanpur Return Shuttle', '2026-10-28', 'completed'),
(6, NULL, 5, 5, 5, 5, 15, 'P3', 'Hostel Zone Return Trip', '2026-10-28', 'cancelled');

-- Update Schedule 2 and Driver 2 to in_progress / on_trip for the active in_route trip
UPDATE schedules SET status = 'in_progress' WHERE schedule_id = 2;
UPDATE drivers SET availability_status = 'on_trip' WHERE driver_id = 2;

-- 12. SEED DRIVER LEAVES
INSERT IGNORE INTO driver_leaves (leave_id, driver_id, start_date, end_date, leave_type, reason, status) VALUES
(1, 3, '2026-11-01', '2026-11-03', 'Medical Leave', 'Family medical appointment in Rishikesh', 'Pending'),
(2, 5, '2026-10-25', '2026-10-27', 'Personal Leave', 'Attending family wedding ceremony', 'Approved');

-- 13. SEED DRIVER EARLY DISPATCH REQUESTS (50% Capacity)
INSERT IGNORE INTO dispatch_requests (dispatch_id, schedule_id, driver_id, vehicle_id, occupancy_percent, passenger_count, capacity, shift_window, message, status) VALUES
(1, 1, 1, 1, 50.0, 20, 40, 'Morning Shift (06:30 - 12:00)', 'Bus has reached 50% capacity (20/40 seats booked). Ready for early departure.', 'pending');

-- 14. SEED TIER 1 FIXED SEAT ALLOCATIONS (Season Pass Commuters)
-- Additional pass holders make the administrator and driver demonstrations
-- representative of a real campus shuttle operation.
INSERT IGNORE INTO users (user_id, student_id, name, email, phone, department, password_hash, role) VALUES
(7, 24022001, 'Ananya Sharma', 'ananya.sharma@student.geu.ac.in', '+91-9876543301', 'Computer Science & Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(8, 24022002, 'Arjun Mehta', 'arjun.mehta@student.geu.ac.in', '+91-9876543302', 'Information Technology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(9, 24022003, 'Kavya Singh', 'kavya.singh@student.geu.ac.in', '+91-9876543303', 'Computer Applications', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(10, 24022004, 'Ritvik Joshi', 'ritvik.joshi@student.geu.ac.in', '+91-9876543304', 'Mechanical Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(11, 24022005, 'Ishita Kapoor', 'ishita.kapoor@student.geu.ac.in', '+91-9876543305', 'Electronics & Communication', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(12, 24022006, 'Yash Bhatia', 'yash.bhatia@student.geu.ac.in', '+91-9876543306', 'Civil Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(13, 24022007, 'Meera Nair', 'meera.nair@student.geu.ac.in', '+91-9876543307', 'Computer Science & Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(14, 24022008, 'Dev Malhotra', 'dev.malhotra@student.geu.ac.in', '+91-9876543308', 'Management Studies', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(15, 24022009, 'Pooja Rawat', 'pooja.rawat@student.geu.ac.in', '+91-9876543309', 'Biotechnology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(16, 24022010, 'Aditya Rana', 'aditya.rana@student.geu.ac.in', '+91-9876543310', 'Computer Applications', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(17, 24022011, 'Simran Kaur', 'simran.kaur@student.geu.ac.in', '+91-9876543311', 'Information Technology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(18, 24022012, 'Nikhil Verma', 'nikhil.verma@student.geu.ac.in', '+91-9876543312', 'Computer Science & Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(19, 24022013, 'Tanya Gupta', 'tanya.gupta@student.geu.ac.in', '+91-9876543313', 'Electronics & Communication', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(20, 24022014, 'Harsh Vardhan', 'harsh.vardhan@student.geu.ac.in', '+91-9876543314', 'Mechanical Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(21, 24022015, 'Aditi Chauhan', 'aditi.chauhan@student.geu.ac.in', '+91-9876543315', 'Civil Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(22, 24022016, 'Rohan Malik', 'rohan.malik@student.geu.ac.in', '+91-9876543316', 'Management Studies', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(23, 24022017, 'Sanya Arora', 'sanya.arora@student.geu.ac.in', '+91-9876543317', 'Computer Applications', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(24, 24022018, 'Kunal Sethi', 'kunal.sethi@student.geu.ac.in', '+91-9876543318', 'Information Technology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(25, 24022019, 'Priya Negi', 'priya.negi@student.geu.ac.in', '+91-9876543319', 'Biotechnology', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(26, 24022020, 'Siddharth Jain', 'siddharth.jain@student.geu.ac.in', '+91-9876543320', 'Computer Science & Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(27, 24022021, 'Neha Bisht', 'neha.bisht@student.geu.ac.in', '+91-9876543321', 'Electronics & Communication', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(28, 24022022, 'Varun Thakur', 'varun.thakur@student.geu.ac.in', '+91-9876543322', 'Mechanical Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(29, 24022023, 'Ira Pant', 'ira.pant@student.geu.ac.in', '+91-9876543323', 'Civil Engineering', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student'),
(30, 24022024, 'Kabir Saxena', 'kabir.saxena@student.geu.ac.in', '+91-9876543324', 'Management Studies', 'scrypt:32768:8:1$3QmUEYF52quvubUk$6e504f2d271ce3bb7015f1bb55804b49635c2ee0b509d37c1fa01e37808701ee728e638011ac3b308b4040ddc57769008dbe6237084ade1b351c0b6411d8fbe6', 'student');

INSERT IGNORE INTO seat_allocations (allocation_id, student_id, route_id, schedule_id, vehicle_id, seat_no, semester, status, valid_from, valid_until) VALUES
(1, 4, 1, 1, 1, 15, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(2, 5, 2, 2, 2, 8, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(3, 6, 1, 1, 1, 16, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(4, 7, 1, 1, 1, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(5, 8, 2, 2, 2, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(6, 9, 3, 3, 3, 1, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(7, 10, 4, 4, 4, 1, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(8, 11, 5, 5, 5, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(9, 12, 6, 6, 6, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(10, 13, 7, 7, 7, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(11, 14, 8, 8, 8, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(12, 15, 9, 9, 9, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(13, 16, 10, 10, 10, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(14, 17, 1, 1, 1, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(15, 18, 2, 2, 2, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(16, 19, 3, 3, 3, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(17, 20, 4, 4, 4, 2, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(18, 21, 5, 5, 5, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(19, 22, 6, 6, 6, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(20, 23, 7, 7, 7, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(21, 24, 8, 8, 8, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(22, 25, 9, 9, 9, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(23, 26, 10, 10, 10, 3, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(24, 27, 1, 1, 1, 4, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(25, 28, 2, 2, 2, 4, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(26, 29, 5, 5, 5, 4, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31'),
(27, 30, 9, 9, 9, 4, '2026-Monsoon', 'active', '2026-08-01', '2026-12-31');

-- 15. SEED DAILY ATTENDANCE & SEAT RECYCLING
-- Amit Saxena (allocation 3, Seat 16) is absent today; seat recycled into Tier 2 Open Pool
INSERT IGNORE INTO daily_attendance (attendance_id, allocation_id, date, status, marked_at, released_to_pool, booked_by_student_id) VALUES
(1, 3, '2026-10-30', 'absent', '2026-10-30 06:15:00', 1, NULL),
(2, 1, '2026-10-30', 'present', '2026-10-30 08:20:00', 0, NULL);
