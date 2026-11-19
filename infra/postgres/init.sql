-- Demo-only local credentials, three independent owners/databases.
CREATE USER orders WITH PASSWORD 'orders';
CREATE USER inventory WITH PASSWORD 'inventory';
CREATE USER payments WITH PASSWORD 'payments';
CREATE DATABASE orders OWNER orders;
CREATE DATABASE inventory OWNER inventory;
CREATE DATABASE payments OWNER payments;
