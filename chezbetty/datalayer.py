from .models import *
from .models.transaction import *
from .models.cashtransaction import *

def undo_transaction(t):
    t.to_account -= t.amount
    t.from_account += t.amount
    DBSession.delete(t)

def deposit(user, amount):
    assert(amount > 0.0)
    assert(hasattr(user, "id"))
    prev = user.balance
    t = Deposit(user, amount)
    DBSession.add(t)
    c = CashDeposit(amount, t)
    DBSession.add(c)
    return dict(prev=prev, new=user.balance, amount=amount,
            transaction=t, cash_transaction=c)

def adjust_user_balance(user, adjustment, notes, admin=None):
    assert(hasattr(user, "id"))
    t = Adjustment(user, adjustment, notes, admin)
    DBSession.add(t)

def purchase(user, items):
    assert(hasattr(user, "id"))
    assert(len(items) > 0)
    t = Purchase(user)
    DBSession.add(t)
    DBSession.flush()
    amount = 0.0
    for item, quantity in items.items():
        item.in_stock -= quantity
        st = SubTransaction(t, item, quantity)
        DBSession.add(st)
        amount += st.amount
    t.update_amount(amount)
    return t

def reconcile_items(items, admin):
    t = Reconciliation(admin)
    total_amount_missing = 0.0
    for item, quantity in items.items():
        if item.in_stock == quantity:
            continue
        item.in_stock = quantity
        quantity_missing = item.in_stock - quantity
        st = SubTransaction(t, item, quantity_missing)
        total_amount_missing += st.amount
    t.update_amount(total_amount_missing)
    return t

def reconcile_cash(amount, admin):
    cash = make_cash_account("cashbox")
    expected_amount = cash.balance
    amount_missing = expected_amount - amount

    t = CashTransaction(
        from_account = make_cash_account("cashbox"),
        to_account = make_cash_account("chezbetty"),
        amount = amount,
        transaction = None,
        user = admin
    )
    DBSession.add(t)
    if amount_missing != 0.0:
        t2 = CashTransaction(
            from_account = make_cash_account("cashbox"),
            to_account = make_cash_account("lost"),
            amount = amount_missing,
            transaction = None,
            user = admin
        )
        DBSession.add(t2)
    return expected_amount

