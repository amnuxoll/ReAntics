import re
from string import printable
from Ant import *

def getAntStats():
    rs_assign = r"\s*(?P<lhs>[^ ]*)\s*=\s*(?P<rhs>.*)\s*"
    # grab the ant indices
    ants = {}
    with open ( "Constants.py", 'r' ) as f :
        on = False
        for l in f :
            l_l = l.lower()
            if "#" in l_l and "type" in l_l and "ant" in l_l :
                on = True
                continue
            elif "#" in l :
                on = False
            if not on : 
                continue
            m = re.match(rs_assign, l)
            if m :
                ants[m.group("lhs")] = int(m.group("rhs"))

    # grab the indices of the unitstats
    locs = {}
    with open ( "Constants.py", 'r' ) as f :
        on = False
        for l in f :
            if re.match ( r".*unit\s*stats.*", l.lower() ) :
                on = True
                continue
            elif "#" in l :
                on = False
            if not on : 
                continue
            m = re.match(rs_assign, l)
            if m :
                locs[m.group("lhs")+" "] = int(m.group("rhs"))

    # grab unit stats data -- actually not really necessary
    #stats = []
    #with open ( "Ant.py", 'r' ) as f :
    #    for l in f :
    #        match = re.match ( r"^\s*UNIT_STATS\.append\((?P<stats>.*)\).*\s*$", l )
    #        if match :
    #            s = match.group("stats").strip()
    #            s = s.replace("[","").replace("]","").replace(" ","")
    #            s = s.split(",")
    #            tmp = []
    #            for x in s :
    #                if re.match(r"\d+",x):
    #                    tmp.append(int(x))
    #                elif x == "True" :
    #                    tmp.append(True)
    #                elif x == "False" :
    #                    tmp.append(False)
    #                else: #unrecognizeable
    #                    tmp.append(None)
    #            stats.append(tmp)

    #print(ants, locs, stats)
    data = [["ANT_TYPES"] + list(locs.keys())]
    for k in ants.keys() :
        data.append([k] + [ str(x) for x in UNIT_STATS[ants[k]] ] )
    #print(data)

    # fix later
    #https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
    s = [[str(e) + "  " for e in row] for row in data]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = ''.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    return '\n'.join(table)

def getHotKeyInfo():
    # GUIHandler.py -- self.root.bind("",stuff)
    rgx_hotkey = re.compile ( r"^\s*self\.root\.bind\s*\(\s*\"(?P<key>.+)\"\s*,\s*.+\s*\)\s*(#\s*(?P<descrip>.*)\s*)?$" )
    k = []
    with open ( "GUIHandler.py", 'r' ) as f :
        for l in f :
            match = rgx_hotkey.match ( l )
            if not match :
                continue
            key = match.group ( "key" )
            descrip = match.group ( "descrip" )
            if descrip is not None:
                k.append ( "%-13s: %s" % ( key, descrip ) )
                
    return re.sub("[^{}]+".format(printable), "", '\n'.join(k))

