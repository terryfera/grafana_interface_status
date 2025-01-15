CREATE DATABASE interface_status; 

CREATE TABLE interface_status.status (
	`timestamp` DATETIME NULL,
	device varchar(100) NULL,
	interface varchar(100) NULL,
	status varchar(100) NULL
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4;

ALTER TABLE interface_status.status ADD CONSTRAINT results_pk PRIMARY KEY (device,interface);


CREATE USER interface_status_user IDENTIFIED BY 'P@ssw0rd';

GRANT ALL ON interface_status.status to interface_status_user;
