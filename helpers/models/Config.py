# models/mi_clase.py
from app.models import get_conf_db, close_conf_db

class Config:
    @staticmethod
    def get_ticket_headers():
        db = get_conf_db()
        try:
            query = "SELECT * FROM ticketText WHERE header = 1 ORDER BY Line;"
            rows = db.execute(query).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise e
        finally:
            close_conf_db()

    @staticmethod
    def get_ticket_footers():
        db = get_conf_db()
        try:
            query = "SELECT * FROM ticketText WHERE header = 0 ORDER BY Line;"
            rows = db.execute(query).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            raise e
        finally:
            close_conf_db()

    @staticmethod
    def set_ticket_headers(obj_list: list):
        Config.set_tickets_text(1, obj_list)

    @staticmethod
    def set_ticket_footers(obj_list: list):
        Config.set_tickets_text(0, obj_list)

    @staticmethod
    def set_tickets_text(level_id: int, obj_list: list) -> list: 
        db = get_conf_db()
        try:
            query = "DELETE FROM ticketText  WHERE header = ?;"
            db.execute(query,[level_id])

            query = "INSERT INTO ticketText (Text, Font, Size, Weight, Line, header) VALUES (?, ?, ?, ?, ?, ?);"
            keys = ["Text", "Font", "Size", "Weight", "Line"]
            for obj in obj_list:
                params = [obj[key] for key in keys]
                params.append(level_id)
                db.execute(query, params)

            return 
        except Exception as e:
            raise e
        finally:
            close_conf_db()
