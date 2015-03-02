from services.database import db


class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(3), nullable=True)
    state_custom = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(3), nullable=True)
    
    def as_string(self):
        state = (self.state_custom and [self.state_custom] or [self.state])[0]
        return ", ".join([self.address, self.city, state, self.country, self.postal_code])
