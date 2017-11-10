import time

for elap in range (9999999999999):
    hours = int(elap/3600)
    minutes = int(elap/60 - hours*60)#int(elap/60)
    seconds = int(elap - hours*3600 - minutes*60.0)#int(elap - minutes*60.0)
    hseconds = int((elap - hours*3600 - minutes*60.0 - seconds)*100) #int((elap - minutes*60.0 - seconds)*100)
    print('%02d:%02d:%02d:%02d' % (hours,minutes, seconds, hseconds))
    time.sleep(0.01)
