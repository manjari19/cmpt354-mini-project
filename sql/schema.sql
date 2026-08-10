-- Library DB Schema

PRAGMA foreign_keys = ON;

CREATE TABLE Members (
    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Address TEXT NOT NULL,
    DateBirth DATE NOT NULL,
    DateRegistration DATE NOT NULL
        CHECK (DateBirth < DateRegistration)
);

CREATE TABLE Items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Author TEXT NOT NULL,
    Publisher TEXT NOT NULL,
    DatePublication DATE NOT NULL,
    Category TEXT NOT NULL
        CHECK (Category IN (
            'Print Book',
            'Online Book',
            'Magazine',
            'Scientific Journal',
            'Record',
            'Audiobook',
            'DVD',
            'Other'
        ))
);

CREATE TABLE Copies (
    CopyID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemID INTEGER NOT NULL,
    DateAcquisition DATE NOT NULL,
    FOREIGN KEY (ItemID)
        REFERENCES Items(ItemID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE Holds (
    MemberID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    DateHold DATE NOT NULL,
    DateReady DATE,

    CHECK (DateReady IS NULL OR DateReady >= DateHold),

    PRIMARY KEY (MemberID, ItemID),
    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (ItemID)
        REFERENCES Items(ItemID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE Borrows (
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER NOT NULL,
    CopyID INTEGER NOT NULL,
    DateCheckout DATE NOT NULL,
    DateReturn DATE,
    Extension INTEGER NOT NULL
        DEFAULT 0
        CHECK (Extension IN (0, 7, 14)),

    CHECK (DateReturn IS NULL OR DateReturn >= DateCheckout),

    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (CopyID)
        REFERENCES Copies(CopyID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE FutureAcquisitions (
    FutureID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Author TEXT NOT NULL,
    Publisher TEXT NOT NULL,
    DatePublication DATE NOT NULL,
    Category TEXT NOT NULL
        CHECK (Category IN (
            'Print Book',
            'Online Book',
            'Magazine',
            'Scientific Journal',
            'Record',
            'Audiobook',
            'DVD',
            'Other'
        )),
    Price REAL NOT NULL
        CHECK (Price >= 0)
);

CREATE TABLE Donations (
    CopyID INTEGER PRIMARY KEY,
    MemberID INTEGER NOT NULL,
    DateDonation DATE NOT NULL,
    FOREIGN KEY (CopyID)
        REFERENCES Copies(CopyID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Address TEXT NOT NULL,
    Department TEXT NOT NULL,
    JobTitle TEXT NOT NULL,
    Salary REAL NOT NULL
        CHECK (Salary > 0),
    DateHire DATE NOT NULL
);

CREATE TABLE Volunteers (
    MemberID INTEGER PRIMARY KEY,
    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE Rooms (
    RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    Capacity INTEGER NOT NULL
        CHECK (Capacity > 0),
    EquipmentDescription TEXT NOT NULL
);

CREATE TABLE Events (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    RoomID INTEGER NOT NULL,
    Date DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Capacity INTEGER NOT NULL
        CHECK (Capacity > 0),
    Type TEXT NOT NULL
        CHECK (Type IN (
            'Book Club',
            'Book-Related Event',
            'Art Show',
            'Film Screening',
            'Workshop',
            'Author Talk',
            'Storytime',
            'Other'
        )),
    RecommendedMinAge INTEGER NOT NULL
        DEFAULT 0
        CHECK (RecommendedMinAge >= 0),

    CHECK (EndTime > StartTime),

    FOREIGN KEY (RoomID)
        REFERENCES Rooms(RoomID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    UNIQUE (RoomID, Date, StartTime),
    UNIQUE (RoomID, Date, EndTime)
);

CREATE TABLE SignUps (
    EventID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    DateSignup DATE NOT NULL,
    PRIMARY KEY (EventID, MemberID),
    FOREIGN KEY (EventID)
        REFERENCES Events(EventID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE EventStaffing (
    EventID INTEGER NOT NULL,
    EmployeeID INTEGER NOT NULL,
    PRIMARY KEY (EventID, EmployeeID),
    FOREIGN KEY (EventID)
        REFERENCES Events(EventID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID)
        REFERENCES Employees(EmployeeID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE EventVolunteering (
    EventID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    Role TEXT NOT NULL,
    PRIMARY KEY (EventID, MemberID),
    FOREIGN KEY (EventID)
        REFERENCES Events(EventID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (MemberID)
        REFERENCES Volunteers(MemberID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE AssistanceRequests (
    AssistID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER NOT NULL,
    EmployeeID INTEGER NOT NULL,
    RequestText TEXT NOT NULL,
    DateSubmission DATE NOT NULL,
    FOREIGN KEY (MemberID)
        REFERENCES Members(MemberID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (EmployeeID)
        REFERENCES Employees(EmployeeID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TRIGGER check_room_capacity
BEFORE INSERT ON Events
BEGIN
    SELECT RAISE(ABORT, 'Room Capacity')
    WHERE NEW.Capacity > (SELECT Capacity FROM Rooms WHERE RoomID = NEW.RoomID);
END;

CREATE TRIGGER check_copy_availability
BEFORE INSERT ON Borrows
BEGIN
    SELECT RAISE(ABORT, 'Copy Availability.')
    WHERE EXISTS (SELECT 1 FROM Borrows WHERE CopyID = NEW.CopyID AND DateReturn IS NULL);
END;

CREATE TRIGGER check_max_holds
BEFORE INSERT ON Holds
BEGIN
    SELECT RAISE(ABORT, 'Max Holds')
    WHERE (SELECT COUNT(*) FROM Holds WHERE MemberID = NEW.MemberID) >= 10;
END;

CREATE TRIGGER check_event_overlap
BEFORE INSERT ON Events
BEGIN
    SELECT RAISE(ABORT, 'Event Overlap')
    WHERE EXISTS (SELECT 1 FROM Events WHERE RoomID = NEW.RoomID
        AND Date = NEW.Date
        AND StartTime < NEW.EndTime
        AND EndTime > NEW.StartTime);
END;

CREATE TRIGGER check_signup_capacity
BEFORE INSERT ON SignUps
BEGIN
    SELECT RAISE(ABORT, 'Event is at full capacity.')
    WHERE (SELECT COUNT(*) FROM SignUps WHERE EventID = NEW.EventID)
        >= (SELECT Capacity FROM Events WHERE EventID = NEW.EventID);
END;

CREATE TRIGGER check_event_update
BEFORE UPDATE ON Events
BEGIN
    SELECT RAISE(ABORT, 'Room Capacity')
    WHERE NEW.Capacity > (SELECT Capacity FROM Rooms WHERE RoomID = NEW.RoomID);

    SELECT RAISE(ABORT, 'Event is at full capacity.')
    WHERE NEW.Capacity < (SELECT COUNT(*) FROM SignUps WHERE EventID = NEW.EventID);

    SELECT RAISE(ABORT, 'Event Overlap')
    WHERE EXISTS (SELECT 1 FROM Events WHERE RoomID = NEW.RoomID
        AND Date = NEW.Date
        AND EventID != NEW.EventID
        AND StartTime < NEW.EndTime
        AND EndTime > NEW.StartTime);
END;

CREATE TRIGGER check_room_update
BEFORE UPDATE ON Rooms
BEGIN
    SELECT RAISE(ABORT, 'Room Capacity')
    WHERE NEW.Capacity < (SELECT MAX(Capacity) FROM Events WHERE RoomID = NEW.RoomID);
END;

CREATE TRIGGER check_borrow_update
BEFORE UPDATE ON Borrows
BEGIN
    SELECT RAISE(ABORT, 'Copy Availability.')
    WHERE NEW.DateReturn IS NULL
      AND EXISTS (SELECT 1 FROM Borrows WHERE CopyID = NEW.CopyID
            AND DateReturn IS NULL AND BorrowID != NEW.BorrowID);
END;

CREATE TRIGGER check_hold_update
BEFORE UPDATE ON Holds
BEGIN
    SELECT RAISE(ABORT, 'Max Holds')
    WHERE NEW.MemberID != OLD.MemberID
      AND (SELECT COUNT(*) FROM Holds WHERE MemberID = NEW.MemberID) >= 10;
END;

CREATE TRIGGER check_signup_update
BEFORE UPDATE ON SignUps
BEGIN
    SELECT RAISE(ABORT, 'Event is at full capacity.')
    WHERE NEW.EventID != OLD.EventID
      AND (SELECT COUNT(*) FROM SignUps WHERE EventID = NEW.EventID)
            >= (SELECT Capacity FROM Events WHERE EventID = NEW.EventID);
END;

CREATE TRIGGER check_item_has_copy
BEFORE DELETE ON Copies
BEGIN
    SELECT RAISE(ABORT, 'Item Needs A Copy')
    WHERE (SELECT COUNT(*) FROM Copies WHERE ItemID = OLD.ItemID) <= 1;
END;

CREATE VIEW BorrowStatus AS
SELECT BorrowID, MemberID, CopyID, DateCheckout, DateReturn,
       date(DateCheckout, '+' || (21 + Extension) || ' days') AS DueDate,
       ROUND(MAX(0, julianday(COALESCE(DateReturn, date('now')))
                    - julianday(date(DateCheckout, '+' || (21 + Extension) || ' days'))) * 0.25, 2) AS Fine
FROM Borrows;
