DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS questions;

CREATE TABLE interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interviewLength INTEGER,
    interviewCategory TEXT,
    timestamp DATETIME
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interviewId INTEGER,
    questionText TEXT,
    answer TEXT,
    analysis TEXT,
    FOREIGN KEY (interviewId) REFERENCES interviews (id)
);