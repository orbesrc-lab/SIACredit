import re

model_code = '''
class BotUnanswered(db.Model):
    __tablename__ = 'bot_unanswered'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, resolved
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
'''

with open('models.py', 'a', encoding='utf-8') as f:
    f.write(model_code)

print('Model appended')
