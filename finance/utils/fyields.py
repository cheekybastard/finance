from calendar import timegm
from time import time
from decimal import Decimal

def mtwo(fnumber):
    return Decimal("%.3f" % fnumber)

def bondyield(coupon_value, current_price, maturity, coupons=None):    
    term = (timegm(maturity + (0, 0, 0)) - time()) / (86400 * 365.256)
    coupons = coupons or term
    absyield = coupons * coupon_value - current_price + 100
    pyield = absyield / current_price
    return mtwo(100 * pyield / term), mtwo(term)

def bondcurrentyield(coupon_value, current_price):
    return 100 * coupon_value / current_price

