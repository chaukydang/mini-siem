# mini-SIEM — Step 1 (PostgreSQL)


## 0) Prepare Postgres
Create DB & user (example):


```sql
CREATE USER mini_siem WITH PASSWORD 'mini_siem';
CREATE DATABASE mini_siem OWNER mini_siem;
GRANT ALL PRIVILEGES ON DATABASE mini_siem TO mini_siem;
