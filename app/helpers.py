import logging
import socket
import json
import math

logging.basicConfig(
    filename='logs.txt',  
    level=logging.ERROR,       
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'  
)

def round_number(number):
    rounded = math.ceil(number * 2) / 2
    return int(rounded) if rounded.is_integer() else rounded

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

def create_ticket_struct(ticketID: int ,products: list, total: float, subtotal: float, notes: str, date: str, productCount: int, wholesale: float):
    ticketLen = 29
    ticketLines = []
    try:
        #Ticket header
        header = [
            'Tel: 373 734 9861'.center(ticketLen, ' '), 
            'Cel: 33 1076 7498'.center(ticketLen, ' '), 
            'Independencia #106 Col Centro'.center(ticketLen, ' '),
            'Servicio a domicilio!...'.center(ticketLen, ' '),
            f'{date}'.center(ticketLen, ' '),
            f'Ticket °{ticketID}'.center(ticketLen, ' ')
            ]
        
        if (notes):
            header.append('Notas:')
            for i in range(0, len(notes), ticketLen):
                header.append(f'{notes[i:i + ticketLen]}')
        
        header.append('-------------------------------')

        for line in header:
            ticketLines.append([['Lucida Console', 30, 1200 ], line.upper()])

        #Ticket products
        for prod in products:
            description = prod['description']
            cantity = round(prod['cantity'],3)
            rowImport = round(prod['import'],1)

            productRow = str(cantity) + ' ' + str(description)
            if(len(productRow) > 24): productRow = productRow[:23]

            ticketLines.append([['Lucida Console', 30, 1500], "{:24}{:>5}".format(productRow, rowImport).upper()])
        
        ticketLines.append([['Lucida Console', 30, 1200 ], '-------------------------------'])
        change = total - subtotal

        #Ticket footer
        footer = [
            f'Total: $ {subtotal}',
        ]

        if change: footer.append(f'Cambio: $ {change}')
        footer.append(f'Productos: {productCount}')
        if wholesale: footer.append(f'Descuento: $ {wholesale}')
        footer.append('Gracias por su compra!...')

        for line in footer:
            ticketLines.append([['Arial', 45, 1300], line.upper()])

        return ticketLines
    except Exception as e:
        print(e)