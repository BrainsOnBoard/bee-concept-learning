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
A = 3
B = 4
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
	neg_reward = [-0.025,-0.025,-0.025,-0.025,0.0,0.0,0.0,0.0]
	pos_reward = [0.025,0.025,0.025,0.025,-0.0,-0.0,-0.0,-0.0]

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
		num_trials = -1 # 30
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
					# train C_E on own
					temp1 = copy.deepcopy(feature_vect[Ap])
					temp1[:] = [x*base_strengthB*0.9 for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
					else:
						pydata_rew = pos_reward_train
						training_counter = 0
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 1
				if stage == 1:
					# train C_L on own
					temp1 = copy.deepcopy(feature_vect[Ap])
					temp1[:] = [x*base_strengthB*0.9 for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
					else:
						pydata_rew = pos_reward_train
						training_counter = 0
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 2
				elif stage == 2:
					# train C_R on own
					temp1 = copy.deepcopy(feature_vect[Ap])
					temp1[:] = [x*base_strengthB*0.9 for x in temp1]
					pydata_in = temp1
					if training_counter < train_len:
						training_counter = training_counter + 1
					else:
						pydata_rew = pos_reward_train
						training_counter = 0	
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 3
							delay_between_trials = max_delay_between_trials	* 2			
							if DNMTS == True:
								temp = pos_reward
								pos_reward = neg_reward
								neg_reward = temp	
				elif stage == 3: 
					if visitStart == True:
						# we are now in the apparatus - choose a stage depending on num visits
						f_it = starting_f_it
						# print "arm={0}, stim={1}".format(arm,stim_match)
						if visits % visits_per_arm_change == 0:
							# flip arm
							arm = -arm				
						visits = visits + 1
						visitStart = False
					# are we fully trained? If do reversal
					if visits > 14:
						stage = 6
					pydata_loc = [1]
					# ok, initial training is done... now we need to add the stimuli
					temp1 = copy.deepcopy(feature_vect[C_E])
					temp1[:] = [x*base_strength*c_strength for x in temp1]
					temp2 = copy.deepcopy(feature_vect[Cp])
					temp2[:] = [x*(base_strength) for x in temp2]
					pydata_in = map(add, temp1, temp2)
					if total_go + total_nogo > 0.1:
						if total_go + 1000.0 > total_nogo:
							# choose an arm to try first
							# no tagging this time but needed for analysis
							pydata_rew = [tag_rate,tag_rate,tag_rate,tag_rate,0,0,0,0]
							arm_chosen = random.choice([4,5])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
						else:
							# well, this bee mucked up
							pydata_in = feature_vect[11]
							pydata_loc = [10]
							delay_between_trials = max_delay_between_trials
				elif stage == 4: # chosen the LEFT arm
					pydata_loc = [2]
					# stimulus
					if arm == L:
						temp1 = copy.deepcopy(feature_vect[C_L])
						temp1[:] = [x*base_strengthB*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[A])
						temp2[:] = [x*(base_strengthB+repetition_effect) for x in temp2]
						pydata_in = map(add, temp1, temp2)
					if arm == R:
						temp1 = copy.deepcopy(feature_vect[C_L])
						temp1[:] = [x*base_strength*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[B])
						temp2[:] = [x*base_strength for x in temp2]
						pydata_in = map(add, temp1, temp2)
					# ok - now what is the reaction!
					if total_go + total_nogo > 0.1:
						if total_go + (random.random()-0.5)*f_it > total_nogo:
							# we have chosen this arm - what is the result?
							if arm == L:
								pydata_rew = pos_reward
							else:
								pydata_rew = neg_reward
							stage = 3
							visitStart = True
							delay_between_trials = max_delay_between_trials
						else:
							# choose a new arm
							arm_chosen = random.choice([4,5])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
							f_it = f_it + f_it_increment
				elif stage == 5: # chosen the RIGHT arm
					pydata_loc = [3]
					# stimulus
					if arm == L :
						temp1 = copy.deepcopy(feature_vect[C_R])
						temp1[:] = [x*base_strength*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[B])
						temp2[:] = [x*base_strength for x in temp2]
						pydata_in = map(add, temp1, temp2)
					if arm == R:
						temp1 = copy.deepcopy(feature_vect[C_R])
						temp1[:] = [x*base_strengthB*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[A])
						temp2[:] = [x*(base_strengthB+repetition_effect) for x in temp2]
						pydata_in = map(add, temp1, temp2)
					# ok - now what is the reaction!
					if total_go + total_nogo > 0.1:
						if total_go + (random.random()-0.5)*f_it > total_nogo: #random.normalvariate(0,f_it)
							# we have chosen this arm - what is the result?
							if arm == R:
								pydata_rew = pos_reward
							else:
								pydata_rew = neg_reward
							stage = 3
							visitStart = True
							delay_between_trials = max_delay_between_trials
						else:
							# choose a new arm
							arm_chosen = random.choice([4,5])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
							f_it = f_it + f_it_increment
				if stage == 9:
					# train C_E with Cp, Dp - 'familiarisation'
					if training_trial_counter % 2:
						pydata_in = map(add, feature_vect[C_E], feature_vect[C])
					else:
						pydata_in = map(add, feature_vect[C_E], feature_vect[D])
					pydata_in[:] = [x*base_strength for x in pydata_in]
					if training_counter < train_len:
						training_counter = training_counter + 1
					else:
						pydata_rew = pos_reward
						training_counter = 0
						delay_between_trials = max_delay_between_trials
						if training_trial_counter < num_trials:
							training_trial_counter = training_trial_counter + 1
						else:
							training_trial_counter = 0
							stage = 6
				elif stage == 6:
					if visitStart == True:
						f_it = starting_f_it
						# we are now in the apparatus - choose a stage depending on num visits
						if True:
							# flip arm
							arm = -arm
						visits = visits + 1
						visitStart = False
					pydata_loc = [5]
					# ok, initial training is done... now we need to add the stimuli
					temp1 = copy.deepcopy(feature_vect[C_E])
					temp1[:] = [x*base_strength*c_strength for x in temp1]
					temp2 = copy.deepcopy(feature_vect[Cp])
					temp2[:] = [x*(base_strength) for x in temp2]
					pydata_in = map(add, temp1, temp2)
					#pydata_in[:] = [x*base_strength for x in pydata_in]
					if total_go + total_nogo > 0.1:
						if total_go + 1000.0 > total_nogo:
							# choose an arm to try first
							# no tagging this time but needed for analysis
							pydata_rew = [tag_rate+0.1,tag_rate,tag_rate,tag_rate,0,0,0,0]
							arm_chosen = random.choice([7,8])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
						else:
							# well, this bee mucked up
							pydata_in = feature_vect[11]
							pydata_loc = [10]
				elif stage == 7: # chosen the LEFT arm
					pydata_loc = [6]
					# stimulus
					if arm == L :
						temp1 = copy.deepcopy(feature_vect[C_L])
						temp1[:] = [x*base_strengthB*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[B])
						temp2[:] = [x*(base_strengthB+repetition_effect) for x in temp2]
						pydata_in = map(add, temp1, temp2)
					if arm == R:
						temp1 = copy.deepcopy(feature_vect[C_L])
						temp1[:] = [x*base_strength*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[A])
						temp2[:] = [x*base_strength for x in temp2]
						pydata_in = map(add, temp1, temp2)
					# ok - now what is the reaction!
					if total_go + total_nogo > 0.1:
						if total_go + (random.random()-0.5)*f_it > total_nogo:
							# we have chosen this arm - what is the result?
							if arm == L:
								pydata_rew = pos_reward
							else:
								pydata_rew = neg_reward
							stage = 6
							visitStart = True
							delay_between_trials = max_delay_between_trials
						else:
							# choose a new arm
							arm_chosen = random.choice([7,8])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
							f_it = f_it + f_it_increment
				elif stage == 8: # chosen the RIGHT arm
					pydata_loc = [7]
					# stimulus
					if arm == L:
						temp1 = copy.deepcopy(feature_vect[C_R])
						temp1[:] = [x*base_strength*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[A])
						temp2[:] = [x*base_strength for x in temp2]
						pydata_in = map(add, temp1, temp2)
					if arm == R:
						temp1 = copy.deepcopy(feature_vect[C_R])
						temp1[:] = [x*base_strengthB*c_strength for x in temp1]
						temp2 = copy.deepcopy(feature_vect[B])
						temp2[:] = [x*(base_strengthB+repetition_effect) for x in temp2]
						pydata_in = map(add, temp1, temp2)
					# ok - now what is the reaction!
					if total_go + total_nogo > 0.1:
						if total_go + (random.random()-0.5)*f_it > total_nogo:
							# we have chosen this arm - what is the result?
							if arm == R:
								pydata_rew = pos_reward
							else:
								pydata_rew = neg_reward
							stage = 6
							visitStart = True
							delay_between_trials = max_delay_between_trials
						else:
							# choose a new arm
							arm_chosen = random.choice([7,8])
							stage = arm_chosen
							delay_between_trials = max_delay_between_trials
							f_it = f_it + f_it_increment
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



