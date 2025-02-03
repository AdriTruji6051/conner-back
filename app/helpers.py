import logging
import socket
import json
import math
from .models import get_conf_db, close_conf_db

logging.basicConfig(
    filename='logs.txt',  
    level=logging.ERROR,       
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'  
)

def round_number(number):
    rounded = math.ceil(number * 2) / 2
    return int(rounded) if rounded.is_integer() else rounded

def format_number(number) -> str: 
    return str(int(number)) if number.is_integer() else "{:.2f}".format(number)

def log_error(error_message: str):
    logging.error(error_message)

def get_printers(ipv4):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ipv4, 12345))
    client_socket.sendall(b'GET PRINTERS')

    data = client_socket.recv(1024)
    client_socket.close()
    data = json.loads(data.decode('utf-8'))
    return data

def send_to_printer(print_info,printer):
    print_info = json.dumps(print_info)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((printer, 12345))
    client_socket.sendall(print_info.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"Respuesta del servidor: {data.decode()}")

    client_socket.close()

def send_ticket_to_printer(ticket_struct: list, printer: dict, open_drawer: bool = False):
    ticketsPrint = []
    for i in range(0, len(ticket_struct), 50):
        ticketsPrint.append(ticket_struct[i:i + 50])
    
    for ticket in ticketsPrint:
        print_info = {
            'includeLogo': True,
            'printerName': printer['name'],
            'text': ticket,
            'openDrawer': open_drawer 
        }

        send_to_printer(print_info, printer['ipv4'])

def send_label_to_printer(label: dict, printer: dict):
    text = [['Arial', 60, 1300], str(label['description'])]
    number = str(round_number(label['salePrice']))
    
    #Config for diferent texts len at termal printer
    fontWeight = 1200
    if len(number) >= 6: 
        number = [['Calibri', 245, fontWeight], number]
    elif len(number) == 5: 
        number = [['Calibri', 300, fontWeight], number]
    elif len(number) <= 4:
        if len(number) < 4: number = f'${number}'
        if '.' in number: number = [['Calibri', 385, fontWeight], number]
        else: number = [['Calibri', 330, fontWeight], number]

    print_info = {
        'includeLogo': False,
        'printerName': printer['name'],
        'text': [text, number],
        'openDrawer': False 
    }

    send_to_printer(print_info, printer['ipv4'])

def open_drawer(printer: dict):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((printer['ipv4'], 12345))
    print_info = {
        'printerName': printer['name'],
        'text': 'OPEN DRAWER',
    }

    print_info = json.dumps(print_info)
    client_socket.sendall(print_info.encode('utf-8'))

    data = client_socket.recv(1024)
    print(f"Respuesta del servidor: {data.decode()}")
    client_socket.close()

    return data.decode('utf-8')

from num2words import num2words

def create_ticket_struct(ticketID: int ,products: list, total: float, subtotal: float, notes: str, date: str, productCount: int, wholesale: float):
    ticketLen = 29
    ticketLines = []
    conf_db = get_conf_db()
    try:
        #Ticket header TODO
        query = 'SELECT * FROM ticketText WHERE header = 1 ORDER BY Line;'
        headerText = conf_db.execute(query).fetchall()

        for head in headerText:
            head = dict(head)
            ticketLines.append([[head['Font'], head['Size'], head['Weight']], head['Text'].center(ticketLen, ' ').upper()])
        
        if (notes):
            ticketLines.append([['Lucida Console', 30, 1200 ], 'NOTAS:'])
            for i in range(0, len(notes), ticketLen):
                ticketLines.append([['Lucida Console', 30, 1200 ], f'{notes[i:i + ticketLen]}'.upper()])

        ticketLines.append([['Lucida Console', 30, 1200 ], 'FECHA: {}'.format(date[:16]).center(ticketLen, ' ')])
        ticketLines.append([['Lucida Console', 30, 1200 ], 'TICKET ° {}'.format(ticketID).center(ticketLen, ' ')])
        ticketLines.append([['Lucida Console', 30, 1200 ], ''])
        ticketLines.append([['Lucida Console', 30, 1500 ], 'CANTIDAD    PRECIO    IMPORTE'])
        ticketLines.append([['Lucida Console', 30, 1200 ], '-------------------------------'])

        #Ticket products
        for prod in products:
            description = prod['description']
            cantity = round(prod['cantity'],3)
            rowImport = round(prod['import'],1)

            ticketLines.append([['Lucida Console', 30, 1500], "{:29}".format(description[:29]).upper()]) #Product description
            ticketLines.append([['Lucida Console', 30, 1500], "{:5} pz   $ {:7}  $ {}".format(cantity, format_number(rowImport/cantity), rowImport).upper()])


        
        ticketLines.append([['Lucida Console', 30, 1200 ], '-------------------------------'])
        change = total - subtotal

        #Ticket footer TODO
        footer = [
            f'Total: $ {subtotal}',
        ]

        footer.append(num2words(subtotal, lang='es'))

        if change: footer.append(f'Cambio: $ {change}')
        footer.append(f'Productos: {productCount}')
        if wholesale: footer.append(f'Descuento: $ {wholesale}')

        for line in footer:
            ticketLines.append([['Arial', 45, 1300], line.upper()])
        
        query = 'SELECT * FROM ticketText WHERE header = 0 ORDER BY Line;'
        footerText = conf_db.execute(query).fetchall()

        for foot in footerText:
            foot = dict(foot)
            ticketLines.append([[foot['Font'], foot['Size'], foot['Weight']], foot['Text'].center(ticketLen, ' ').upper()])
        

        return ticketLines
    except Exception as e:
        print(e)
    finally:
        close_conf_db()
