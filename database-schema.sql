CREATE TABLE IF NOT EXISTS page (
    id_page integer primary key,
    url varchar not null unique,
    created_at text default CURRENT_TIMESTAMP,
    is_checked text integer default 0,
    num_errors integer default 0
    );


CREATE TABLE IF NOT EXISTS error (
    id_error INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL,
    message TEXT,
    FOREIGN KEY(page_id) REFERENCES page(id_page)
    );

