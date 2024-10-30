--data_base structure: TO MAIN data base
CREATE TABLE "departments" (
	"code"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	PRIMARY KEY("code" AUTOINCREMENT)
);

CREATE TABLE "productsFamily" (
	"code"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	PRIMARY KEY("code" AUTOINCREMENT),
	FOREIGN KEY("code") REFERENCES ""
);

CREATE TABLE "products" (
	"code"	TEXT NOT NULL UNIQUE,
	"description"	TEXT NOT NULL,
	"saleType"	TEXT NOT NULL,
	"cost"	REAL,
	"salePrice"	REAL NOT NULL,
	"department"	INTEGER,
	"wholesalePrice"	REAL,
	"priority"	INTEGER,
	"inventory"	REAL,
	"modifiedAt"	TEXT,
	"profitMargin"	INTEGER,
	"parentCode"	TEXT,
	"familyCode"	INTEGER,
	PRIMARY KEY("code"),
	FOREIGN KEY("department") REFERENCES "departments"("code"),
	FOREIGN KEY("familyCode") REFERENCES "productsFamily"("code")
);

CREATE TABLE "tickets" (
	"ID"	INTEGER NOT NULL,
	"createdAt"	TEXT NOT NULL,
	"subTotal"	REAL NOT NULL,
	"total"	REAL NOT NULL,
	"profit"	REAL NOT NULL,
	"articleCount"	INTEGER NOT NULL,
	"notes"	TEXT,
	"discount"	REAL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

CREATE TABLE "ticketsProducts" (
	"ID"	INTEGER NOT NULL,
	"ticketId"	INTEGER NOT NULL,
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"cantity"	REAL NOT NULL,
	"profit"	REAL,
	"paidAt"	TEXT NOT NULL,
	"isWholesale"	REAL,
	"usedPrice"	REAL NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

--Config structure: TO CONFIG data base
CREATE TABLE "defaultPrinter" (
	"printerName"	TEXT NOT NULL,
	PRIMARY KEY("printerName")
);

CREATE TABLE "serverIp" (
	"ipv4"	TEXT NOT NULL,
	PRIMARY KEY("ipv4")
);

--history structure: TO HISTORY changes data base
CREATE TABLE "history_changes_products" (
	"code"	VARCHAR(50) NOT NULL,
	"description"	TEXT NOT NULL,
	"saleType"	BLOB,
	"cost"	REAL,
	"salePrice"	REAL NOT NULL,
	"wholesalePrice"	REAL,
	"modifiedAt"	INTEGER NOT NULL,
	"profitMargin"	INTEGER,
	"operationType"	TEXT NOT NULL
);

--Inserts for department, delete it at new db create
INSERT INTO departments (code, description) VALUES (0, 'Sin departamento');
INSERT INTO departments (code, description) VALUES (18, '18%');
INSERT INTO departments (code, description) VALUES (17, '17%');
INSERT INTO departments (code, description) VALUES (19, '19%');
INSERT INTO departments (code, description) VALUES (13, '13%');
INSERT INTO departments (code, description) VALUES (20, '20%');
INSERT INTO departments (code, description) VALUES (6, '6%');
INSERT INTO departments (code, description) VALUES (3, '3%');
INSERT INTO departments (code, description) VALUES (4, '4%');
INSERT INTO departments (code, description) VALUES (15, '15%');
INSERT INTO departments (code, description) VALUES (5, '5%');
INSERT INTO departments (code, description) VALUES (8, '8%');
INSERT INTO departments (code, description) VALUES (9, '9%');
INSERT INTO departments (code, description) VALUES (7, '7%');
INSERT INTO departments (code, description) VALUES (10, '10%');
INSERT INTO departments (code, description) VALUES (11, '11%');
INSERT INTO departments (code, description) VALUES (12, '12%');
INSERT INTO departments (code, description) VALUES (2, '2%');
INSERT INTO departments (code, description) VALUES (22, '22%');
INSERT INTO departments (code, description) VALUES (21, '21%');


--Querys to get data