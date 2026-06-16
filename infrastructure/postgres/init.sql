-- AgroVision — PostgreSQL Initialization
-- Each microservice owns an isolated database. This script creates them all.
-- Run once on first startup via docker-entrypoint-initdb.d.

CREATE DATABASE identity_db;
CREATE DATABASE farm_db;
CREATE DATABASE livestock_db;
CREATE DATABASE inventory_db;
CREATE DATABASE finance_db;
CREATE DATABASE notification_db;
CREATE DATABASE reporting_db;

-- Grant all databases to the application user
GRANT ALL PRIVILEGES ON DATABASE identity_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE farm_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE livestock_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE finance_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO agrovision;
GRANT ALL PRIVILEGES ON DATABASE reporting_db TO agrovision;
