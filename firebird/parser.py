#Este metodo de acceso por abrir coneccion, query, cambios, commit y cerrar lo hace bastante mas lento, 
#pero al ser un proceso de un solo uso me facilita el mudar la base de datos de FDB a sqlite mediante un 
#codigo mas limpio 

import fdb
import ctypes
import sqlite3

def fdbQuery(query)-> list:
    ctypes.cdll.LoadLibrary('./fbclient.dll')
    con =  fdb.connect(
        dsn='PDVDATA.fdb', 
        user='SYSDBA', 
        password='masterkey',
        charset='NONE'
    )

    cur = con.cursor()
    cur.execute(query)

    queryResult = cur.fetchall()

    cur.close()
    con.close()

    return queryResult

def sqlite3Query(query) -> list:
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = cursorSQL.execute(query)
    conSQL.commit()
    conSQL.close()

    return queryResult

def sqlite3QueryParams(query, params) -> list:
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = cursorSQL.execute(query, params)
    conSQL.commit()
    conSQL.close()

    return queryResult

def sqlite3_Several_Querys(query, paramsArray):
    conSQL = sqlite3.connect("./data_base.db")
    cursorSQL = conSQL.cursor()
    queryResult = []

    for params in paramsArray:
        try:
            queryResult.append(cursorSQL.execute(query, params))
        except Exception as e:
            print('-------------------------------------------->')
            print(f'Error al insertar el registro: "{params}"')
            print(e)

    conSQL.commit()
    conSQL.close()

    return queryResult

def productosParser() -> None:
    print('Exportando productos...')
    sqlite3Query('DROP TABLE IF EXISTS products;')
    sqlite3Query('''
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
        FOREIGN KEY("familyCode") REFERENCES "productsFamily"("code") ON UPDATE CASCADE ON DELETE SET NULL,
        FOREIGN KEY("parentCode") REFERENCES "products"("code") ON UPDATE CASCADE ON DELETE SET NULL
    );
    ''')

    sqlQuery = 'INSERT INTO products (code,description,saleType,cost, salePrice,department,wholesalePrice,priority,inventory,modifiedAt,profitMargin) VALUES (?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?);'
    cur = fdbQuery('SELECT CODIGO, DESCRIPCION, TVENTA, PCOSTO, PVENTA, DEPT, MAYOREO, IPRIORIDAD, DINVENTARIO, CHECADO_EN, PORCENTAJE_GANANCIA FROM PRODUCTOS;')
    
    sqlite3_Several_Querys(sqlQuery, cur)

def ventaTicketsParser() -> None:
    print('Exportando tickets...')
    sqlite3Query('DROP TABLE IF EXISTS tickets;')
    sqlite3Query('CREATE TABLE "tickets" ("ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "createdAt" TEXT NOT NULL, "subTotal" REAL NOT NULL, "total" REAL NOT NULL, "profit" REAL NOT NULL, "articleCount" INTEGER NOT NULL, "notes" TEXT, "discount" REAL);')

    sqlQuery = 'INSERT INTO tickets (ID,createdAt,subTotal,total,profit,articleCount,notes) VALUES (?, ?, ?, ?, ?, ?, ?);'

    cur = fdbQuery('SELECT ID, CREADO_EN, SUBTOTAL, TOTAL, GANANCIA, NUMERO_ARTICULOS, NOTAS FROM VENTATICKETS;')

    sqlite3_Several_Querys(sqlQuery, cur)

def ventaTicketsArticulosParser():
    print('Exportando productos vendidos...')
    sqlite3Query('DROP TABLE IF EXISTS ticketsProducts;')
    sqlite3Query('CREATE TABLE "ticketsProducts" ("ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "ticketId" INTEGER NOT NULL, "code" VARCHAR(50) NOT NULL, "description" TEXT NOT NULL, "cantity" REAL NOT NULL, "profit" REAL, "paidAt" TEXT NOT NULL, "isWholesale" REAL, "usedPrice" REAL NOT NULL);')
    sqlQuery = 'INSERT INTO ticketsProducts (ID, ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'

    cur = fdbQuery('SELECT ID, TICKET_ID, PRODUCTO_CODIGO, PRODUCTO_NOMBRE, CANTIDAD, GANANCIA, PAGADO_EN, USA_MAYOREO, PRECIO_USADO FROM VENTATICKETS_ARTICULOS;')

    sqlite3_Several_Querys(sqlQuery, cur)
        
try:
    print('CHAMBEANDO ANDAMOS V5.1.1')
    print('Creating basic data base!')
    print('Creating departments....')

    sqlite3Query('''
    CREATE TABLE "departments" (
        "code"	INTEGER NOT NULL,
        "description"	TEXT NOT NULL,
        PRIMARY KEY("code" AUTOINCREMENT)
    );
    ''')
    depts = [
        "INSERT INTO departments (code, description) VALUES (0, 'Sin departamento');",
        "INSERT INTO departments (code, description) VALUES (18, '18%');",
        "INSERT INTO departments (code, description) VALUES (17, '17%');",
        "INSERT INTO departments (code, description) VALUES (19, '19%');",
        "INSERT INTO departments (code, description) VALUES (13, '13%');",
        "INSERT INTO departments (code, description) VALUES (20, '20%');",
        "INSERT INTO departments (code, description) VALUES (6, '6%');",
        "INSERT INTO departments (code, description) VALUES (3, '3%');",
        "INSERT INTO departments (code, description) VALUES (4, '4%');",
        "INSERT INTO departments (code, description) VALUES (15, '15%');",
        "INSERT INTO departments (code, description) VALUES (5, '5%');",
        "INSERT INTO departments (code, description) VALUES (8, '8%');",
        "INSERT INTO departments (code, description) VALUES (9, '9%');",
        "INSERT INTO departments (code, description) VALUES (7, '7%');",
        "INSERT INTO departments (code, description) VALUES (10, '10%');",
        "INSERT INTO departments (code, description) VALUES (11, '11%');",
        "INSERT INTO departments (code, description) VALUES (12, '12%');",
        "INSERT INTO departments (code, description) VALUES (2, '2%');",
        "INSERT INTO departments (code, description) VALUES (22, '22%');",
        "INSERT INTO departments (code, description) VALUES (21, '21%');"
    ]

    for d in depts:
        sqlite3Query(d)
    
    sqlite3Query('''
    CREATE TABLE "productsFamily" (
        "code"	INTEGER NOT NULL,
        "description"	TEXT NOT NULL,
        PRIMARY KEY("code" AUTOINCREMENT),
        FOREIGN KEY("code") REFERENCES ""
    );
    ''')

    sqlite3Query('''
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
    ''')

    sqlite3Query('''
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
    ''')
    productosParser()    
except Exception as e:
    print(e)
finally:
    print('Finalizado...')