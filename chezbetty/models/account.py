from .model import *

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(Enum("user", "placeholder"), nullable=False)
    balance = Column(Float, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    __mapper_args__ = {'polymorphic_on':type}


class PlaceholderAccount(Account):
    __mapper_args__ = {'polymorphic_identity': 'placeholder'}


def __make_account(name):
    t = DBSession.query(PlaceholderAccount).filter(PlaceholderAccount.name == name).first()
    if t:
        return t
    t = PlaceholderAccount(name)
    DBSession.add(t)
    return t

# special accounts
chezbetty = __make_account("chezbetty")
lost      = __make_account("lost")