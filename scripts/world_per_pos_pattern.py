#!/usr/bin/python

import socket               # Import socket module
import ctypes
import struct
import select, random
import time
import numpy
import math
from operator import add
import copy

# some setup...
random.random()

C_E = 0
C_L = 1
C_R = 2
A = 7
B = 8
Ap = 5
Bp = 6
C = 7
D = 8 
Cp = 9
Dp = 10

L = -1
R = 1
A_match = -1
B_match = 1

feature_vect = numpy.empty([12,144]).tolist()
for i in xrange(12):
	for j in xrange(144):
		if i == C_E:
			if j >= 0 and j < 16:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == C_L:
			if j >= 16 and j < 32:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == C_R:
			if j >= 32 and j < 48:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == A:
			if j >= 48 and j < 64:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == B:
			if j >= 72 and j < 88:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == Ap:
			if j >= 56 and j < 72:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == Bp:
			if j >= 80 and j < 96:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == C:
			if j >= 96 and j < 112:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == D:
			if j >= 120 and j < 136:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == Cp:
			if j >= 104 and j < 120:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == Dp:
			if j >= 128 and j < 144:
				feature_vect[i][j] = random.random()*0.2+0.9
			else:
				feature_vect[i][j] = 0
		if i == 11:
			feature_vect[i][j] = 0
			


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object
s.bind(('127.0.0.1', 50091))        # Bind to the port

s.listen(2)                 # Now wait for client connection.
while True:
	s.setblocking(1)
	print "Listening..."
	#c_in, c_out
	c_in = False
	c_out = False
	c_rew = False
	c_loc = False
	in_sz = 0
	out_sz = 0
	# loop to find one input and one output
	for conn in range(4):
		c, addr = s.accept()     # Establish connection with client.
		print 'Got connection from', addr
		val = c.recv(1)
		print "Handshake val = ", ord(val)
		if ord(val) == 45 or ord(val) == 46:
			print "Handshake recv"
			c.send(chr(41))
			print "Handshake sent"
			dtype = c.recv(1)
			print "Data type recv"
			c.send(chr(42))
			tsize = c.recv(4)
			print "Data size recv"
			size = struct.unpack('i',tsize)[0]
			print "Size = ", size
			c.send(chr(42))
			namesize = c.recv(4)
			name = c.recv(struct.unpack('i',namesize)[0])
			print "Name = ", name
			if name == "input":
				c_in = c
				in_sz = size
			if name == "output":
				c_out = c
				out_sz = size
			if name == "reward":
				c_rew = c
			if name == "location":
				c_loc = c
			c.send(chr(42))
			

	# If only GO is trained
	neg_reward = [-0.4,-0.4,-0.4,-0.4,0.0,0.0,0.0,0.0]
	pos_reward = [0.4,0.4,0.4,0.4,-0.0,-0.0,-0.0,-0.0]

	pos_reward_train = pos_reward

	# testing values (do not learn)
	pos_ind = [0.001,0,0,0,0,0,0,0]
	neg_ind = [-0.001,0,0,0,0,0,0,0]
			
	if c_in and c_rew and c_out and c_loc:
		print "Sent data "
		s.settimeout(0.1)
		#s.setblocking(0)
		#now we should be connected... send the data
		keepgoing = True
		pydata_in = [0] *in_sz
		pydata_rew = [0,0,0,0,0,0,0,0]
		pydata_out = numpy.empty([out_sz]).tolist()
		pydata_loc = [0]
		# some pars for the algorithm
		# need to delay as we are not in a continuous space situation and one decision should take some time to complete
		delay_between_trials = 0
		max_delay_between_trials = 10
		training_counter = 0
		training_trial_counter = 0
		train_len = 10
		num_trials = 24 # 30
		stage = 0
		visits_per_arm_change = 2
		visits = 0
		arm = random.choice([L,R])
		# changed from 0.55 (so half the learning rate)
		tag_rate = 0.525
		visitStart = True
		isTest = False
		# the f it factor
		f_it_increment = 10.0 # 10
		starting_f_it = 0.0 # deadlock breaking (was 10)
		repetition_effect = -0.0
		base_strength = 1.0
		base_strengthB = 1.0
		c_strength = 0.02 #strength of context relative to base
		f_it = starting_f_it
		while keepgoing:
			# PROCESS DATA
			pydata_rew = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
			total_go = pydata_out[0] + pydata_out[1] + pydata_out[2] + pydata_out[3]
			total_nogo = pydata_out[4] + pydata_out[5] + pydata_out[6] + pydata_out[7]
			if delay_between_trials < 1:
				if stage == 0:
					# untrain to no response
					if training_trial_counter % 3 == 0:
						temp1 = copy.deepcopy(feature_vect[A])
					if training_trial_counter % 3 == 1:
						temp1 = copy.deepcopy(feature_vect[B])
					if training_trial_counter % 3 == 2:
						patterned = True
						tempA = copy.deepcopy(feature_vect[A])
						tempA[:] = [x*0.5 for x in tempA]
						tempB = copy.deepcopy(feature_vect[B])
						tempB[:] = [x*0.5 for x in tempB]
						temp1 = map(add, tempA, tempB)
					temp1[:] = [x*base_strengthB*base_strength for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
					else:
						pydata_rew = neg_reward
						training_counter = 0
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < 3:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 1
				if stage == 1:
					# training
					patterned = False
					if training_trial_counter % 4 == 0:
						temp1 = copy.deepcopy(feature_vect[A])
					if training_trial_counter % 4 == 2:
						temp1 = copy.deepcopy(feature_vect[B])
					if training_trial_counter % 4 == 1 or training_trial_counter % 4 == 3:
						patterned = True
						tempA = copy.deepcopy(feature_vect[A])
						tempA[:] = [x*0.5 for x in tempA]
						tempB = copy.deepcopy(feature_vect[B])
						tempB[:] = [x*0.5 for x in tempB]
						temp1 = map(add, tempA, tempB)
					temp1[:] = [x*base_strengthB*base_strength for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
						if training_counter == 1:
							pydata_rew = [tag_rate,tag_rate,tag_rate,tag_rate,0,0,0,0]
						if training_counter == train_len:
							if total_go + total_nogo > 0.1:
								if total_go  + (random.random()-0.5)*f_it_increment > total_nogo:
									pydata_rew = pos_ind
								else:
									pydata_rew = neg_ind
					else:
						if patterned:
							pydata_rew = pos_reward
						else:
							pydata_rew = neg_reward
						training_counter = 0
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 2
				elif stage == 2:
					# testing
					temp1 = copy.deepcopy(feature_vect[A])
					temp1[:] = [x*base_strengthB*0.9 for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
						if training_counter == 1:
							pydata_rew = [tag_rate,tag_rate,tag_rate,tag_rate,0,0,0,0]
					else:
						pydata_rew = pos_ind
						training_counter = 0	
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 2
							delay_between_trials = max_delay_between_trials	* 2			
			else:
				delay_between_trials = delay_between_trials - 1
				pydata_in = feature_vect[11]
			# DO DATA COMMUNICATION
			data = struct.pack('d'*len(pydata_in),*pydata_in)
			c_in.sendall(buffer(data))
			dataRew = struct.pack('d'*len(pydata_rew),*pydata_rew)
			c_rew.sendall(buffer(dataRew))
			dataLoc = struct.pack('d'*len(pydata_loc),*pydata_loc)
			c_loc.sendall(buffer(dataLoc))
			loop_for_in = True
			loop_for_rew = True
			loop_for_loc = True
			loop_for_out = True
			num_loops = 0
			#print ".",
			while loop_for_in or loop_for_out or loop_for_rew or loop_for_loc:
				#time.sleep(.01)
				num_loops = num_loops + 1
				if num_loops > 100:
					c_in.close()                # Close the connection
					c_out.close()                # Close the connection
					c_rew.close()
					c_loc.close()
					exit(0)
				if loop_for_in:
					try:
						c_in.recv(1)
						#print "send confirmed"
					except:
						# nowt here
						print "@",
					else:
						loop_for_in = False
				if loop_for_loc:
					try:
						c_loc.recv(1)
						#print "send confirmed"
					except:
						# nowt here
						print "@",
					else:
						loop_for_loc = False
				if loop_for_rew:
					try:
						c_rew.recv(1)
						#print "send confirmed rew"
					except:
						# nowt here
						print "@",
					else:
						loop_for_rew = False
				if loop_for_out:
					try:
						inDat = c_out.recv(8*out_sz)
						#print "data recv stage 1"
						pydata_out = struct.unpack('d'*len(pydata_out),inDat)
						#print "data recv complete"
						#print pydata
						# confirm
						c_out.send(chr(42))
					except:
						#nowt here
						print "!",
						i = 1
					else:
						loop_for_out = False
		c_in.close()                # Close the connection
		c_out.close()                # Close the connection
		c_rew.close()
		c_loc.close()



