DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS question_list;
DROP TABLE IF EXISTS users;
--Table schema used in the project
--consists of three tables users, question_list, interviews
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE,
    password TEXT
);

CREATE TABLE question_list (
    question_id INTEGER PRIMARY KEY,
    question_text TEXT,
    sub_category TEXT
);

CREATE TABLE interviews (
    session_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    interview_answers TEXT,
    interview_analysis TEXT,
    eye_contact REAL,
    timestamp DATETIME,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);