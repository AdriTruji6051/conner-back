from app.helpers import open_drawer, send_label_to_printer
from app.models import close_hist_db, close_pdv_db, get_hist_db, get_drawer_db, close_drawer_db, get_pdv_db
from app.routes import PRINTERS_ON_WEB
from datetime import datetime
import calendar

def date_info(date: str) -> dict:
    # Input format YYYY-MM-DD
    try:
        dateFormat = datetime.strptime(date, '%Y-%m-%d')
        
        day = dateFormat.strftime('%A') 
        month = dateFormat.strftime('%B')

        month_days = calendar.monthrange(dateFormat.year, dateFormat.month)[1] 
        
        return {
            'month': month,
            'day': day,
            'month_days': month_days
        }
    except ValueError:
        print("Invalid input format, please send an input with the next format str('YYYY-MM-DD').")

def workload_day(date: str) -> list:
    db = get_pdv_db()
    workload = list()
    try:
        date = date.split('-')
        year = date[0] 
        month = date[1]
        day = date[2]

        query = 'SELECT COUNT() as count FROM tickets WHERE createdAt LIKE ?;'
        if int(day) < 10: day = '0' + str(int(day))
        if not dict(db.execute(query, [f'{year}-{month}-{day}%']).fetchone())['count']:
            print(f'PREV RETURN AT: {year}-{month}-{day}', date)
            return workload #Return if not data at this day

        for i in range(24):
            hour =  '0' + str(i) if i < 10 else str(i)
            try:
                count = dict(db.execute(query, [f'{year}-{month}-{day} {hour}:%']).fetchone())['count']

                articleQuery = 'SELECT sum(articleCount) as articleCount FROM tickets WHERE createdAt LIKE ?;'
                articlesCount = dict(db.execute(articleQuery, [f'{year}-{month}-{day} {hour}:%']).fetchone())['articleCount']

                if articlesCount < 1: continue

                dateInfo = date_info(date=f'{year}-{month}-{day}')

                workload.append({
                    'hour': hour,
                    'workload': count,
                    'articles': articlesCount if articlesCount else 0,
                    'day': dateInfo['day'],
                    'month': dateInfo['month']
                })
            except Exception as e:
                continue

    except Exception as e:
        print('Error (getWorkload) -> ', e)
    finally:
        close_pdv_db()
        return workload

def get_products_changes(day):
    db = get_hist_db()
    try:
        rows = db.execute("SELECT * FROM history_changes_products WHERE modifiedAt = ? AND operationType != 'DELETE';",[day]).fetchall()
        products = []
        for row in rows:
            products.append(dict(row))

        return products
    except Exception as e:
        raise e
    finally:
        close_hist_db()

def labels_print(data):
    try:        
        labels = data['labels']
        printer = PRINTERS_ON_WEB[data['printerName']]

        for label in labels:
            send_label_to_printer(label, printer)
        
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        drawer_log(time=date, action='LABELS')
        
        return {'message' : 'Succesfull labels print'}
    except Exception as e:
        raise e
    
def drawer_open(data):
    try:        
        printer = PRINTERS_ON_WEB[data['printerName']]

        open_drawer(printer)

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        drawer_log(time=date, action='OPEN')
        
        return {'message' : 'Succesfull drawer open'}
    
    except Exception as e:
        raise e
    
def drawer_log(time: str, action: str):
    db = get_drawer_db() 
    try:
        query = 'INSERT INTO drawerLogs (logTime, action) VALUES (?, ?);'
        db.execute(query, (time, action))
        db.commit()
    except Exception as e:
        raise e
    finally:
        close_drawer_db()


   