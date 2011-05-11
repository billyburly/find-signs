#!/usr/bin/python

'''
This script will scan through every chunk looking for signs and write out an
updated overviewer.dat file.  This can be useful if your overviewer.dat file
is either out-of-date or non-existant.  

To run, simply give a path to your world directory, for example:

    python contrib/findSigns.py ../world.test/

Once that is done, simply re-run the overviewer to generate markers.js:

    python overviewer.py ../world.test/ output_dir/

Note: if your cachedir is not the same as your world-dir, you'll need to manually
move overviewer.dat into the correct location.

'''
import sys
import re
import os
import json

sys.path.append(".")
import nbt

from pprint import pprint

worlddir = sys.argv[1]
if os.path.exists(worlddir):
    print "Scanning chunks in ", worlddir
else:
    sys.exit("Bad WorldDir")

if len(sys.argv) == 3:
    outdir = sys.argv[2]
else:
    outdir = worlddir

matcher = re.compile(r"^r\..*\.mcr$")

POI = []
numsigns = 0

for dirpath, dirnames, filenames in os.walk(worlddir):
    for f in filenames:
        if matcher.match(f):
            #print f
            full = os.path.join(dirpath, f)
            r = nbt.load_region(full)
            chunks = r.get_chunks()
            for x,y in chunks:
                chunk = r.load_chunk(x,y).read_all()                
                data = chunk[1]['Level']['TileEntities']
                for entity in data:
                    if entity['id'] == 'Sign':
                        msg=' \n'.join([entity['Text1'], entity['Text2'], entity['Text3'], entity['Text4']])
                        #print "checking -->%s<--" % msg.strip()
                        if msg.strip():
                            newPOI = dict(type="sign",
                                            x= entity['x'],
                                            y= entity['y'],
                                            z= entity['z'],
                                            msg=msg,
                                            chunk= (entity['x']/16, entity['z']/16),
                                           )
                            POI.append(newPOI)
                            #print "Found sign at (%d, %d, %d): %r" % (newPOI['x'], newPOI['y'], newPOI['z'], newPOI['msg'])
                            numsigns += 1

print str(numsigns) + " signs found"

jsonFile = os.path.join(outdir,"signs.json")
f = open(jsonFile,"wb")
f.write("signData = " + json.dumps(POI) + ";")

