CREATE TABLE monobudget.transactions (
    time BIGINT PRIMARY KEY,
    mcc INT,
    description TEXT,
    amount INT,
    category TEXT,
    category_last_asked_seconds BIGINT,
    comment TEXT
);