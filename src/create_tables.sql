USE WT2;

CREATE TABLE Admin(
    admin_id varchar(20),
    pwd varchar(100),
    name varchar(100)
)

INSERT INTO Admin values('admin','pbkdf2:sha256:50000$OUbRQks7$3f3b83a4201e7f980c3446054b5fdec63c048fb375325fa0d90234715a555d35','ADMIN');
