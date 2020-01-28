import datetime as dt

for i in range(30):
            
    date = dt.datetime.now().date() - dt.timedelta(days = 30 - i)
    print(date)
        