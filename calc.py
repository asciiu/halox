def oddsToPercent(odds):
    return 1/odds

def profit(investment, percent):
    return investment / percent - investment

def wager(investment, ipercent, tpercent):
    return (investment * ipercent) / tpercent

i = 1000
o1 = 1.77
o2 = 2.13

p1 = oddsToPercent(o1)
p2 = oddsToPercent(o2)
t = p1 + p2

print t
if t < 1:
    profit = profit(i, t)
    w1 = wager(i, p1, t)
    w2 = wager(i, p2, t)
    print "Investment: ", i
    print "Profit: ", profit, " (", (profit/i)*100, "%)"
    print "Wager1: ", w1
    print "Wager2: ", w2
