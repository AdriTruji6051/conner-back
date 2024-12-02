from app.models import get_pdv_db, close_pdv_db
from helpers.utils import workload_day

def statitistic_ticket_day(date):
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