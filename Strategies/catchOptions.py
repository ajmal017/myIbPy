# from ib_api_demo.py

from time import sleep
import math as mth
import IbHistDataCSV as hD
import readBarchart as rdPv


def IsOptionabuy(opcontract,stkpr,optask,optbid):


#volatility check


    if price<S1[symb]: return True
    return False