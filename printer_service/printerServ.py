import socket
import json
import threading
import win32print
import win32ui
from PIL import Image, ImageWin
import sqlite3
import webbrowser
import time

def sqlite3_query(query, params = [], commit = False) -> list:
    res = []
    conSQL = sqlite3.connect("./db/config.db")
    cursorSQL = conSQL.cursor()
    rows = cursorSQL.execute(query, params)
    for row in rows:
        res.append(row)

    if(commit): conSQL.commit() 
    conSQL.close()

    return res

def getServerIp():
    return sqlite3_query('SELECT ipv4 FROM serverIp;',[])[0][0]

def openPDV():
    time.sleep(2)
    webbrowser.open(f'http://{getServerIp()}:5000/')

def get_default_printer():
    return sqlite3_query('SELECT printerName FROM defaultPrinter;',[])[0][0]

def list_printers(ipv4) -> dict:
    default_printer = get_default_printer()

    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    avaliable_printers = {}
    for printer in printers:
        avaliable_printers[f'{printer[2]}.{ipv4.split('.')[3]}'] = {
            'ipv4': ipv4,
            'name': printer[2],
            'isdefault': True if printer[2] == default_printer else False
        }
    
    return avaliable_printers

def termal_printer(lines: list, printer_name: str, include_logo: bool = True) -> bool:
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc("Ticket")
        hDC.StartPage()
        y = 10  # Initial Y position

        if(include_logo):
            bmp = Image.open('./db/logo.jpg')
            bmp = bmp.resize((1200, 590))
            dib = ImageWin.Dib(bmp)
            dib.draw(hDC.GetHandleOutput(), (10, y, 590, y + 250))

            y += 250

        for line in lines:
            fontConfig = line[0]
            text = line[1]

            fontFamily = fontConfig[0]
            fontSize = fontConfig[1]
            fontWeight = fontConfig[2]

            font = win32ui.CreateFont({
                "name": fontFamily,
                "height": fontSize, 
                "weight": fontWeight,
            })

            hDC.SelectObject(font)
            hDC.TextOut(10, y, text)
            y += fontSize + 5

        hDC.EndPage()
        hDC.EndDoc()
        return True
    except Exception as e:
        print('Error printing ->', e)
        return False
    finally:
        win32print.ClosePrinter(hPrinter)
    

def open_drawer(printer_name):
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(hPrinter, 1, ("Open Drawer", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, b'\x1B\x70\x00\x19\xFA')
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    except Exception as e:
        print('Error ->', e)
    finally:
        win32print.ClosePrinter(hPrinter)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def run_printer_service():
    print(f'Servicion de impresión en {get_local_ip()}')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345)) 
    server_socket.listen(10) 

    print("Servidor de impresion esperando conexiones...")

    while True:
        conn, addr = server_socket.accept()
        try:
            print(f"Conección de servidor {addr}")
            
            data = conn.recv(4096)
            
            data = data.decode('utf-8')
            
            if(data == 'GET PRINTERS'):
                print('Printers GET')
                ipv4 = get_local_ip()
                printers = list_printers(ipv4=ipv4)
                conn.sendall(json.dumps(printers).encode('utf-8'))
            else:
                ticket = json.loads(data)

                if(ticket['text'] == 'OPEN DRAWER'):
                    open_drawer(ticket['printerName'])
                else:
                    if ticket['openDrawer']: open_drawer(ticket['printerName'])

                    if ticket['includeLogo']: termal_printer(lines=ticket['text'], printer_name=ticket['printerName'])
                    else: termal_printer(lines=ticket['text'], printer_name=ticket['printerName'], include_logo=False)

                    conn.sendall(b'Succesfull print!')
  
        except Exception as e:
            print(e)
            conn.sendall(b'Something was wrong, try it out!')
        finally:
            conn.close()

def isPrinterRunning(host='127.0.0.1', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout):
            return False

if __name__ == "__main__":
    pdv =  threading.Thread(target=openPDV)
    printer_serv =  threading.Thread(target=run_printer_service)
    if(not isPrinterRunning()): printer_serv.start()
    pdv.start()