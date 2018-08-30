#!/usr/bin/python

from subprocess import call
import os.path
import os
import time, stat, random, math
import ctypes
import struct
import re

# standard paths
from setup import *

print 'Script to run many bees using the model'

# the different configs 
seeds = range(123,525,2)
print "Running ",
print len(seeds),
print " bees..."

print 'Beginning bees'
prevseed = 123
for seed in seeds:
	print 'Running bee ',
	print seed
	
	# create new bee!
	p_ext = 0.5
	p_ret = 0.5
	random.seed(seed)
	n_ext = 8
	n_kc = 5000
	n_pn = 144
	
	# and the PN->KC connectivity seed
	with open( model_path + "/model.xml", "r+" ) as model:
		data = model.read()
		data = re.sub(r'seed="\d+"', 'seed="{0}"'.format(seed), data)
		model.seek(0)
		model.write( data )
		model.truncate()
	
	script_name = "batch_bee.sh"
	fl = open(script_name, "w")
	fl.write("#!/bin/bash\n");
	fl.write("cd " + script_path + "\n");
	fl.write("python world_KC_repeat.py &\n")
	fl.write("cd " + s2b_path + "\n");
	run_line = "BRAHMS_NS=" + s2b_path + "/Namespace/ SYSTEMML_INSTALL_PATH=" + systemml_path + " PATH=" + os.environ['PATH'] + ":" + systemml_path + "/brahms/bin:. ./convert_script_s2b -w " + s2b_path + " -m " + model_path + " -e 0 -o " + out_path + "/bee{0}/".format(seed)
	run_line = run_line + "\n"
	fl.write(run_line);
	fl.close()
	# Now make the script executable...
	st = os.stat(script_name)
	os.chmod(script_name, st.st_mode | stat.S_IEXEC)
				
	# launch the batch
	call(['bash', script_name])
