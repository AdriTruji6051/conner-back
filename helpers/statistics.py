from app.models import get_pdv_db, close_pdv_db
from helpers.utils import workload_day

from datetime import datetime, timedelta

def get_date_range(begin_date: str, end_date: str) -> list:
    # If str parse to date
    if isinstance(begin_date, str):
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    date_range = []
    while begin_date <= end_date:
        date_range.append(begin_date.strftime("%Y-%m-%d"))
        begin_date += timedelta(days=1)

    return date_range

def statitistic_ticket_day(date: str) -> dict:
    db = get_pdv_db()
    try:
        query = 'SELECT COUNT() as count, SUM(subTotal) as SUMSubTotal, SUM(articleCount) as SUMArticleCount, SUM(profit) as SUMProfit, SUM(discount) as SUMDiscount, SUM(subTotal) / COUNT() as averageTicket, (SUM(subTotal) + SUM(discount)) / SUM(articleCount) as averageProductPrice FROM tickets WHERE createdAt LIKE ?;'
        ticketsStat = dict(db.execute(query, [f'{date}%']).fetchone())

        if(ticketsStat['count'] < 1): raise Exception('NO DATA')

        ticketsStat['workload'] = workload_day(date)
        return ticketsStat
    except Exception as e:
        raise e
    finally:
        close_pdv_db()

def statitistic_ticket_range(begining_date: str, finish_date: str) -> dict:
    db = get_pdv_db()
    try:
        dates = get_date_range(begining_date, finish_date)

        query = 'SELECT COUNT() as count, SUM(subTotal) as SUMSubTotal, SUM(articleCount) as SUMArticleCount, SUM(profit) as SUMProfit, SUM(discount) as SUMDiscount, SUM(subTotal) / COUNT() as averageTicket, (SUM(subTotal) + SUM(discount)) / SUM(articleCount) as averageProductPrice FROM tickets WHERE createdAt LIKE ?;'
        
        range_stats = {
            "SUMArticleCount": 0,
            "SUMDiscount": 0,
            "SUMProfit": 0,
            "SUMSubTotal": 0,
            "averageProductPrice": 0,
            "averageTicket": 0,
            "count": 0,
            "workload": []
        }

        keys = ['SUMArticleCount', 'SUMDiscount', 'SUMProfit', 'SUMSubTotal', 'averageProductPrice', 'averageTicket', 'count']

        for date in dates:
            ticketsStat = dict(db.execute(query, [f'{date}%']).fetchone())

            if(ticketsStat['count'] < 1): continue

            for key in keys:
                range_stats[key] += ticketsStat[key]

            range_stats['workload'].append(
                {
                    "articles": ticketsStat['SUMArticleCount'],
                    "day": date[:],
                    "hour": date[5:-3],
                    "month": date[-2:],
                    "workload": ticketsStat['count']
                }
            )
        
        range_stats['averageProductPrice'] /= len(range_stats['workload'])
        range_stats['averageTicket'] /= len(range_stats['workload'])

        return range_stats
    except Exception as e:
        raise e
    finally:
        close_pdv_db()