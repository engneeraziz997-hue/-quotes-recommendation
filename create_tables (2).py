import sqlite3
conn = sqlite3.connect("quotes.db", timeout=30)
cur = conn.cursor()


def init_db(cur):
    cur.executescript("""
CREATE TABLE errors (
	stage	TEXT,
	indexed_t	TEXT,
	topic	TEXT,
	url	TEXT,
	handled	BOOLEAN DEFAULT 0,
	error_msg	TEXT,
	timestamp	DATETIME DEFAULT CURRENT_TIMESTAMP,
	last_retry	datetime,
	letter	TEXT
);
                      
CREATE TABLE indexed_topics (
	indexed_t	TEXT,
	topic	TEXT,
	PRIMARY KEY(topic)
);

CREATE TABLE indexed_topics_info (
	name	TEXT,
	num_of_topics	INTEGER,
	PRIMARY KEY(name)
);

CREATE TABLE lett_of_ind_tops (
	letter	TEXT,
	indexed_t	TEXT,
	PRIMARY KEY(indexed_t)
);

CREATE TABLE letter_info (
	letter	TEXT,
	num_of_ind_tops	INTEGER,
	PRIMARY KEY(letter)
);    

CREATE TABLE quotes (
	topic	TEXT,
	author	TEXT,
	quote	TEXT,
	UNIQUE(topic,author,quote)
);

CREATE TABLE topics (
	topic	TEXT,
	pages	INTEGER,
	PRIMARY KEY(topic)
);                                                                                                                                                            
    """)


init_db(cur)
conn.commit()
