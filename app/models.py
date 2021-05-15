from app import db


class Chat(db.Model):
    __tablename__ = 'chat'
    chat_id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50))