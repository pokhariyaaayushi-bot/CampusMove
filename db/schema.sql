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
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER, -- Alias identifier matching campus roll/student number
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(80),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 2. FLEET (VEHICLES) TABLE
-- Maps to ER Entity: Vehicle (vehicle_id, registration_no, vehicle_type, capacity, owner_type)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    private_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    carpool_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    time_window VARCHAR(50) NOT NULL,
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
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    status VARCHAR(25) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'aborted_requeued', 'cancelled', 'completed')),
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

