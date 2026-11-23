-- ====================================================================
-- CampusMove — Unified Relational Database Schema (3NF)
-- Aligned with Mentor-Approved ER Diagram
-- Integration Owner: Aayushi Pokhariya (Member 1 — Lead)
-- Course Integration: DBMS (TCS 503) & OS (TCS 502)
-- Relational Model: Third Normal Form (3NF) with Referential Constraints
-- ====================================================================

-- 1. STUDENT / USERS TABLE
-- Maps to ER Entity: Student (student_id, name, email, phone, department)
-- Supports role-based authentication (student / admin)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    student_id INTEGER, -- Alias identifier matching campus roll/student number
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(80),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'faculty', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 2. FLEET (VEHICLES) TABLE
-- Maps to ER Entity: Vehicle (vehicle_id, registration_no, vehicle_type, capacity, owner_type)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    registration_no VARCHAR(50), -- Alias for ER diagram attribute
    model VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(100),   -- Alias for ER diagram attribute
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    owner_type VARCHAR(20) NOT NULL DEFAULT 'college' CHECK (owner_type IN ('college', 'private')),
    availability_status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (availability_status IN ('available', 'in_use', 'maintenance')),
    maintenance_status VARCHAR(20) NOT NULL DEFAULT 'good' CHECK (maintenance_status IN ('good', 'due', 'under_repair')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vehicles_availability ON vehicles(availability_status);
CREATE INDEX IF NOT EXISTS idx_vehicles_maintenance ON vehicles(maintenance_status);
CREATE INDEX IF NOT EXISTS idx_vehicles_owner_type ON vehicles(owner_type);

-- 3. PRIVATE VEHICLE SPECIALIZATION (Schema Completion)
-- Maps to ER Entity: Private_vehicle (private_id, student_id, vehicle_id, available_seats)
CREATE TABLE IF NOT EXISTS private_vehicles (
    private_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    student_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL UNIQUE,
    available_seats INTEGER NOT NULL CHECK (available_seats >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pvt_vehicles_student ON private_vehicles(student_id);

-- 4. MAINTENANCE TABLE
-- Maps to ER Entity: Maintenance (maintenance_id, vehicle_id, issue, start_date, end_date, status)
CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,
    issue VARCHAR(255) NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    status VARCHAR(25) NOT NULL DEFAULT 'in_progress' CHECK (status IN ('scheduled', 'in_progress', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle ON maintenance(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance(status);

-- 5. DRIVERS TABLE
-- Maps to ER Entity: Driver (driver_id, name, phone, license_no, availability)
CREATE TABLE IF NOT EXISTS drivers (
    driver_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    license_no VARCHAR(50),      -- Alias for ER diagram attribute
    availability_status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (availability_status IN ('available', 'on_trip', 'off_duty')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_drivers_availability ON drivers(availability_status);

-- 6. TRANSIT ROUTES TABLE
-- Maps to ER Entity: Route (route_id, source, destination, distance, estimated_time)
CREATE TABLE IF NOT EXISTS routes (
    route_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(120) NOT NULL UNIQUE,
    origin VARCHAR(120) NOT NULL,
    source VARCHAR(120),         -- Alias for ER diagram attribute
    destination VARCHAR(120) NOT NULL,
    distance_km REAL NOT NULL CHECK (distance_km > 0),
    distance REAL,               -- Alias for ER diagram attribute
    estimated_duration_mins INTEGER NOT NULL CHECK (estimated_duration_mins > 0),
    estimated_time INTEGER,      -- Alias for ER diagram attribute
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routes_origin_dest ON routes(origin, destination);

-- 7. STOPS TABLE
-- Maps to ER Entity: Stop (stop_id, route_id, stop_name, sequence_no)
CREATE TABLE IF NOT EXISTS stops (
    stop_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    route_id INTEGER NOT NULL,
    stop_name VARCHAR(120) NOT NULL,
    sequence_no INTEGER NOT NULL CHECK (sequence_no > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stops_route ON stops(route_id);

-- 8. CARPOOL TABLE (Schema Completion)
-- Maps to ER Entity: Carpool (carpool_id, driver_student_id, route_id, capacity, departure_time)
CREATE TABLE IF NOT EXISTS carpools (
    carpool_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    driver_student_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    departure_time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_student_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_carpools_driver ON carpools(driver_student_id);
CREATE INDEX IF NOT EXISTS idx_carpools_route ON carpools(route_id);

-- 9. SCHEDULES TABLE
-- Maps to ER Entity: Schedule (schedule_id, route_id, vehicle_id, driver_id, departure_time, arrival_time)
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    route_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    time_window VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL DEFAULT 'inbound' CHECK (direction IN ('inbound', 'outbound')),
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_schedules_route ON schedules(route_id);
CREATE INDEX IF NOT EXISTS idx_schedules_vehicle ON schedules(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_schedules_driver ON schedules(driver_id);
CREATE INDEX IF NOT EXISTS idx_schedules_status ON schedules(status);

-- 10. TRANSPORT REQUESTS TABLE
-- Maps to ER Entity: Transport_request (request_id, student_id, route_id, requested_time, priority)
CREATE TABLE IF NOT EXISTS transport_requests (
    request_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    student_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    requested_time TEXT NOT NULL,
    priority VARCHAR(5) NOT NULL DEFAULT 'P3' CHECK (priority IN ('P1', 'P2', 'P3')),
    purpose VARCHAR(255),
    status VARCHAR(25) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'allocated', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_requests_student ON transport_requests(student_id);
CREATE INDEX IF NOT EXISTS idx_requests_priority ON transport_requests(priority);
CREATE INDEX IF NOT EXISTS idx_requests_status ON transport_requests(status);

-- 11. BOOKINGS TABLE
-- Maps to ER Entity: Booking (booking_id, request_id, schedule_id, vehicle_id, seat_no, status, booking_time)
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    request_id INTEGER,
    student_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    schedule_id INTEGER,
    vehicle_id INTEGER,
    seat_no INTEGER,
    priority_level VARCHAR(5) NOT NULL DEFAULT 'P3' CHECK (priority_level IN ('P1', 'P2', 'P3')),
    purpose VARCHAR(255) NOT NULL,
    requested_date TEXT NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(25) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'in_route', 'aborted_requeued', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES transport_requests(request_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bookings_request ON bookings(request_id);
CREATE INDEX IF NOT EXISTS idx_bookings_student ON bookings(student_id);
CREATE INDEX IF NOT EXISTS idx_bookings_schedule ON bookings(schedule_id);
CREATE INDEX IF NOT EXISTS idx_bookings_priority ON bookings(priority_level);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);

-- 12. DRIVER LEAVES TABLE
CREATE TABLE IF NOT EXISTS driver_leaves (
    leave_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    leave_type VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_leaves_driver ON driver_leaves(driver_id);
CREATE INDEX IF NOT EXISTS idx_leaves_status ON driver_leaves(status);


-- 13. DRIVER DISPATCH REQUESTS TABLE (50% Capacity Early Dispatch Workflow)
CREATE TABLE IF NOT EXISTS dispatch_requests (
    dispatch_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    schedule_id INTEGER,
    driver_id INTEGER NOT NULL,
    vehicle_id INTEGER,
    occupancy_percent REAL NOT NULL,
    passenger_count INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    shift_window VARCHAR(50),
    message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dispatch_driver ON dispatch_requests(driver_id);
CREATE INDEX IF NOT EXISTS idx_dispatch_status ON dispatch_requests(status);


-- 14. NOTIFICATIONS TABLE (Admin Operational Alerts)
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    vehicle_id INTEGER,
    driver_id INTEGER,
    route_id INTEGER,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

-- 15. SEAT ALLOCATIONS TABLE (Three-Tier Model -- Tier 1 Fixed Seats)
-- Maps to Tier 1: Fixed Season-Pass holders with guaranteed daily seats
CREATE TABLE IF NOT EXISTS seat_allocations (
    allocation_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    student_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    seat_no INTEGER NOT NULL,
    semester VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'expired')),
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE(vehicle_id, seat_no, semester)
);

CREATE INDEX IF NOT EXISTS idx_seat_alloc_student ON seat_allocations(student_id);
CREATE INDEX IF NOT EXISTS idx_seat_alloc_schedule ON seat_allocations(schedule_id);
CREATE INDEX IF NOT EXISTS idx_seat_alloc_vehicle ON seat_allocations(vehicle_id);

-- 16. DAILY ATTENDANCE & SEAT RECYCLING TABLE (Tier 1 Absence Releases & Check-in)
-- Maps to Tier 1 daily absence marking and dynamic seat recycling into Tier 2 Open Pool
CREATE TABLE IF NOT EXISTS daily_attendance (
    attendance_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    allocation_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'present' CHECK (status IN ('present', 'absent', 'auto_released', 'no_show')),
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_to_pool INTEGER NOT NULL DEFAULT 0,
    booked_by_student_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (allocation_id) REFERENCES seat_allocations(allocation_id) ON DELETE CASCADE,
    FOREIGN KEY (booked_by_student_id) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE(allocation_id, date)
);

CREATE INDEX IF NOT EXISTS idx_daily_att_alloc ON daily_attendance(allocation_id);
CREATE INDEX IF NOT EXISTS idx_daily_att_date ON daily_attendance(date);
CREATE INDEX IF NOT EXISTS idx_daily_att_status ON daily_attendance(status);
