-- Library DB Schema
-- Will define all the tables, constraints, and triggers for the library system

--to ensure that foreign key constraints are enforced
PRAGMA foreign_keys = ON;

--creating table Members
CREATE TABLE Members (
    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Address TEXT,
    DateOfBirth DATE NOT NULL,
    DateOfRegistration DATE NOT NULL
);

--creating Items 
CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Author TEXT NOT NULL,
    Publisher TEXT NOT NULL,
    DateOfPublication DATE NOT NULL,
    Category TEXT NOT NULL
);

--creating Copies (needs to reference Items)
CREATE TABLE Copies (
    CopyID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemID INTEGER NOT NULL,
    DateOfAcquisition DATE NOT NULL,
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
);

--creating Holds (needs to reference Members and Items)
CREATE TABLE Holds (
    MemberID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    DateOfHold DATE NOT NULL,
    DateOfReady DATE,
    PRIMARY KEY (MemberID, ItemID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID)
);

--creating Borrows (needs to reference Members and Copies)
--modified extension to be either 0, 7, or 14 days
CREATE TABLE Borrows (
    BorrowID INTEGER PRIMARY KEY,
    MemberID INTEGER NOT NULL,
    CopyID INTEGER NOT NULL,
    DateOfCheckout DATE NOT NULL,
    DateOfReturn DATE,
    Extension INTEGER NOT NULL DEFAULT 0 CHECK (Extension IN (0, 7, 14)),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (CopyID) REFERENCES Copies(CopyID)
);

--creating FutureAcquisitions
CREATE TABLE FutureAcquisitions (
    FutureID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Author TEXT NOT NULL,
    Publisher TEXT NOT NULL,
    DateOfPublication DATE NOT NULL,
    Category TEXT NOT NULL,
    Price REAL NOT NULL
);

--creating Donations
CREATE TABLE Donations (
    CopyID INTEGER PRIMARY KEY,
    MemberID INTEGER NOT NULL,
    DateOfDonation DATE NOT NULL,
    FOREIGN KEY (CopyID) REFERENCES Copies(CopyID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

--creating Employees
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Address TEXT,
    Department TEXT NOT NULL,
    JobTitle TEXT NOT NULL,
    Salary REAL NOT NULL,
    DateOfHire DATE NOT NULL
);
--creating Volunteers (needs to reference Members)
CREATE TABLE Volunteers (
    MemberID INTEGER PRIMARY KEY,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

--creating Rooms
CREATE TABLE Rooms (
    RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    Capacity INTEGER NOT NULL,
    EquipmentDescription TEXT
);

--creating Events (needs to reference Rooms)
CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    RoomID INTEGER NOT NULL,
    Date DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Capacity INTEGER NOT NULL,
    Type TEXT NOT NULL,
    RecommendedMinAge INTEGER NOT NULL,
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
    UNIQUE (RoomID, Date, StartTime), --referencing BCNF candidate key
    UNIQUE (RoomID, Date, EndTime) ----referencing BCNF candidate key
);

--creating Sign-Ups (needs to reference Events and Members)
CREATE TABLE SignUps (
    EventID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    DateOfSignup DATE NOT NULL,
    PRIMARY KEY (EventID, MemberID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

--creating EventStaffing (needs to reference Events and Employees)
CREATE TABLE EventStaffing (
    EventID INTEGER NOT NULL,
    EmployeeID INTEGER NOT NULL,
    PRIMARY KEY (EventID, EmployeeID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

--creating EventVolunteering (needs to reference Events and Volunteers)
CREATE TABLE EventVolunteering (
    EventID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    Role TEXT NOT NULL,
    PRIMARY KEY (EventID, MemberID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID),
    FOREIGN KEY (MemberID) REFERENCES Volunteers(MemberID)
);

--creating AssistanceRequests (needs to reference Members and Employees)
CREATE TABLE AssistanceRequests (
    AssistID INTEGER PRIMARY KEY,
    MemberID INTEGER NOT NULL,
    EmployeeID INTEGER NOT NULL,
    RequestText TEXT NOT NULL,
    DateOfSubmission DATE NOT NULL,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

--creating required triggers
--event capcity cannot exceed room capacity
CREATE TRIGGER check_room_capacity
BEFORE INSERT ON Events
BEGIN
    SELECT RAISE (ABORT, 'Event capacity exceeds room capacity')
    WHERE NEW.Capacity > (SELECT Capacity FROM Rooms WHERE RoomID = NEW.RoomID);
END;

--can't borrow a copy that's already checked out
CREATE TRIGGER check_copy_availability
BEFORE INSERT ON Borrows
BEGIN
    SELECT RAISE (ABORT, 'Copy is already checked out')
    WHERE EXISTS (SELECT 1 FROM Borrows WHERE CopyID = NEW.CopyID AND DateOfReturn IS NULL);
END;

--a member cannot have more than 10 active holds at a time
CREATE TRIGGER check_max_holds
BEFORE INSERT ON Holds
BEGIN
    SELECT RAISE (ABORT, 'Member has reached the maximum number of active holds')
    WHERE (SELECT COUNT(*) FROM Holds WHERE MemberID = NEW.MemberID) >= 10;
END;

--two events cannot be scheduled in the same room at the same time
CREATE TRIGGER check_event_overlap
BEFORE INSERT ON Events
BEGIN
    SELECT RAISE (ABORT, 'Event overlaps with another event in the same room')
    WHERE EXISTS (SELECT 1 FROM Events WHERE RoomID = NEW.RoomID AND Date = NEW.Date AND ((StartTime < NEW.EndTime AND EndTime > NEW.StartTime)));
END;

--cannot sign up for an event if the event is at full capacity
CREATE TRIGGER check_signup_capacity
BEFORE INSERT ON SignUps
BEGIN
    SELECT RAISE (ABORT, 'Event is at full capacity')
    WHERE (SELECT COUNT(*) FROM SignUps WHERE EventID = NEW.EventID) >= (SELECT Capacity FROM Events WHERE EventID = NEW.EventID);
END;