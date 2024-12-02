from datetime import datetime
from app.helpers import create_ticket_struct, open_drawer, send_ticket_to_printer
from app.models import close_pdv_db, get_pdv_db
from app.routes import PRINTERS_ON_WEB
from helpers.utils import drawer_log


def get_tickets_by_date(date):
    db = get_pdv_db()
    try:        
        sql = 'SELECT * FROM tickets WHERE createdAt LIKE ?;'
        sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

        rows = db.execute(sql, [f'{date}%']).fetchall()
        tickets = []

        for row in rows:
            row = dict(row)
            for key in row:
                if type(row[key]) == bytes:
                    row[key] = str(row[key])

            prodRows = db.execute(sqlPr, [row['ID']]).fetchall()
            products = []
            for prod in prodRows:
                products.append(dict(prod))
            
            row['products'] = products
            tickets.append(row)

        return tickets[::-1]
    
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def ticket_print(data):
    db = get_pdv_db()
    try:        
        id = data['ID']
        printerName = data['printerName']
        if(printerName):
            printer = PRINTERS_ON_WEB[printerName]
            
            sql = 'SELECT * FROM tickets WHERE ID = ?;'
            sqlPr = 'SELECT * FROM ticketsProducts WHERE ticketId = ?;'

            row = dict(db.execute(sql, [id]).fetchone())
            prodRows = db.execute(sqlPr, [id]).fetchall()

            products = []
            for prod in prodRows:
                prod = dict(prod)
                prod['import'] = prod['cantity'] * prod['usedPrice']
                products.append(prod)
            
            ticketStruct = create_ticket_struct(ticketID=id ,products=products, total=row['total'], subtotal=row['subTotal'], notes=row['notes'], date=row['createdAt'], productCount=row['articleCount'], wholesale=row['discount'])
            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=False)
        
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        drawer_log(time=date, action='REPRINT')

        return {'message' : 'Succesfull ticket reprint!'}
    
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def ticket_create(data):
    db = get_pdv_db()
    try:        
        date = datetime.now()

        createAt = date.strftime('%Y-%m-%d %H:%M:%S')
        printerName = data['printerName']
        willPrint = data['willPrint']
        wholesale = data['wholesale']
        subtotal = data['total']
        total = data['paidWith']
        notes = data['notes']
        productsCount = data['productsCount']

        profitTicket = 0

        ticketId = dict(db.execute('SELECT MAX (ID) FROM tickets;').fetchone())['MAX (ID)']
        queryTicktProd = 'INSERT INTO ticketsProducts (ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) values (?,?,?,?,?,?,?,?);'
        queryTickt = 'INSERT INTO tickets (ID, createdAt, subTotal, total, profit, articleCount, notes, discount) values (?,?,?,?,?,?,?,?);'

        if(ticketId):
            ticketId += 1
        else:
            ticketId = 1

        for prod in data['products']:
            profit = 0
            if 'wholesalePrice' in prod: prod['wholesalePrice'] = prod['wholesalePrice'] if prod['wholesalePrice'] else prod['salePrice']
            else: prod['wholesalePrice'] = prod['salePrice']

            if(prod['cost']): profit = ( (prod['wholesalePrice'] * 100) / prod['cost'] ) - 100 if wholesale else ( prod['salePrice'] * 100) /  (prod['cost']) - 100
            else: profit = 10

            params = [
                ticketId,
                prod['code'],
                prod['description'],
                prod['cantity'],
                round(profit),
                createAt,
                wholesale,
                prod['wholesalePrice'] if wholesale else prod['salePrice']
            ]
            
            profitTicket += round(( prod['wholesalePrice'] * (profit /100)) * prod['cantity'] ) if wholesale else round(( prod['salePrice'] * (profit / 100)) * prod['cantity'] )
            db.execute(queryTicktProd, params)
        
        
        params = [
            ticketId,
            createAt,
            subtotal,
            total,
            profitTicket,
            productsCount,
            notes,
            wholesale
        ]

        db.execute(queryTickt, params)
        db.commit()

        if(willPrint and printerName):
            createAt = date.strftime('%d-%m-%Y %H:%M')
            ticketStruct = create_ticket_struct(ticketID=ticketId, products=data['products'], total=total, subtotal=subtotal,notes=notes, date=createAt, productCount=productsCount, wholesale=wholesale )
            printer = PRINTERS_ON_WEB[printerName]

            send_ticket_to_printer(ticket_struct=ticketStruct, printer=printer, open_drawer=False)

        if(not willPrint and printerName):
            printer = PRINTERS_ON_WEB[printerName]
            open_drawer(printer=printer)

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        drawer_log(time=date, action='SALE')
        
        return {'folio' : ticketId}
    except Exception as e:
        raise e
    finally:
        close_pdv_db()


def ticket_update(data):
    db = get_pdv_db()
    try:        
        ticketID = data['ID']
        products = data['products']

        db.execute('UPDATE tickets SET profit = ?, discount = ?, subTotal = ?, total = ?, articleCount = ? WHERE ID = ?;',[
            data['profit'],
            data['discount'],
            data['subTotal'],
            data['total'],
            data['articleCount'],
            ticketID
        ])
        
        rows = db.execute('SELECT ID FROM ticketsProducts WHERE ticketId = ?;', [ticketID])
        prodIDs = set()

        for row in rows:
            prodIDs.add(dict(row)['ID'])

        for prod in products:
            db.execute('UPDATE ticketsProducts SET cantity = ? WHERE ID = ?;', [
                prod['cantity'],
                prod['ID']
            ])
            prodIDs.discard(prod['ID'])
        
        for id in prodIDs:
            db.execute('UPDATE ticketsProducts SET ticketId = ? WHERE ID = ?;', [ticketID * -1, id])

        
        date = datetime.now()
        createAt = date.strftime('%Y-%m-%d %H:%M:%S')
        queryTicktProd = 'INSERT INTO ticketsProducts (ticketId, code, description, cantity, profit, paidAt, isWholesale, usedPrice) values (?,?,?,?,?,?,?,?);'

        for prod in data['newProducts']:
            if(prod['cost']): profit = prod['salePrice'] * 100 /  prod['cost'] - 100
            else: profit = 10

            params = [
                ticketID,
                prod['code'],
                prod['description'],
                prod['cantity'],
                round(profit),
                createAt,
                0,
                prod['salePrice']
            ]
            
            db.execute(queryTicktProd, params)
        
        db.commit()

        return {'message' : 'Ticket updated!'}
    except Exception as e:
        raise e
    finally:
        close_pdv_db()
