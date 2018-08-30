import xml.etree.ElementTree as ET
import sml_log_parser
import matplotlib.pyplot as plt
from numpy import  *
import csv

# standard paths
from setup import *

learn_indices_all = []
seeds = range(123,825,2)
diffs_big = empty(0)
diffs_big_fail = empty(0)
diffs_big_trial_num = empty(0)
diffs_big_fail_trial_num = empty(0)
for seed in seeds:
	# output file dir
	log_dir = out_path + '/bee{0}/log'.format(seed)
	print "Loading logs from {0}".format(log_dir) 
	# load the HR and HP
	logRew = sml_log_parser.sml_log(log_dir, 'Reward_out_logrep.xml')
	# extract data
	data = logRew.getdataforindex(0)
	#print len(data)
	a = array(data)
	# get the indices of the trials
	trial_indices = nonzero(a>0.4)
	# get rid of markers
	a[trial_indices] = 0
	# analyse in blocks
	block_num = 0
	#print trial_indices
	#print len(trial_indices[0].T)
	learn_indices = []
	# we don't want more than 6 blocks + 4 trials
	print len(trial_indices[0].T)
	if len(trial_indices[0].T) > 69:
		trial_indices = trial_indices[0][0:69]
	else:
		trial_indices = trial_indices[0]
	if len(trial_indices) < 69:
		continue	
	print trial_indices
	print len(trial_indices)
	# extract trial lengths
	diffs = trial_indices[1:-1]-trial_indices[0:-2]
	i=0
	while i < len(trial_indices)-2:
		i = i +1
		curr_trial = a[trial_indices[i]:trial_indices[i+1]]
		pos = sum(curr_trial>0)
		if pos > 0.1:
			diffs_big = append(diffs_big, (trial_indices[i+1]-trial_indices[i])/2.0)
			diffs_big_trial_num = append(diffs_big_trial_num, i)
		if pos < 0.1:
			diffs_big_fail = append(diffs_big_fail, (trial_indices[i+1]-trial_indices[i])/2.0)
			diffs_big_fail_trial_num = append(diffs_big_fail_trial_num, i)
	while (block_num+1)*10 < len(trial_indices):
		curr_block = a[trial_indices[block_num*10]:trial_indices[(block_num+1)*10]]
		print "Block ",
		print block_num
		pos = sum(curr_block>0)
		neg = sum(curr_block<0)
		#if block_num == 5:
			# remove re-training
			#pos = pos - 21
		print pos,
		print " vs ",
		print neg
		learn_indices.append(float(pos)/float(pos+neg)*100.0)
		block_num = block_num + 1
	# append last 4 trials
	print len(trial_indices)
	if len(trial_indices) == 69:
		test_block = a[trial_indices[60]:trial_indices[64]]
		#print test_block
		pos = sum(test_block>0)
		neg = sum(test_block<0)
		# remove re-training
		#pos = pos - 21
		print pos,
		print " vs(t) ",
		print neg
		learn_indices.append(float(pos)/float(pos+neg)*100.0)
		test_block = a[trial_indices[64]:trial_indices[68]]
		#print test_block
		pos = sum(test_block>0)
		neg = sum(test_block<0)
		# remove re-training
		#pos = pos - 21
		print pos,
		print " vs(t2) ",
		print neg
		learn_indices.append(float(pos)/float(pos+neg)*100.0)
	learn_indices_all.append(learn_indices)


# sort data by trial
index = 0
trial_sums = zeros(7)
for i in diffs_big_trial_num:
	trial_sums[math.floor(i/10.0)] += diffs_big[index]/100.0
	index += 1
index = 0
trial_sums_fail = zeros(7)
for i in diffs_big_fail_trial_num:
	trial_sums_fail[math.floor(i/10.0)] += diffs_big_fail[index]/100.0
	index += 1

trial_sums[-1] = trial_sums[-1]*2.5
trial_sums_fail[-1] = trial_sums_fail[-1]*2.5

fig3 = plt.figure()	
plt.plot(diffs_big_trial_num, diffs_big,'g.')
plt.hold
plt.plot([5,15,25,35,45,55,62],trial_sums, 'g-')
plt.xlabel('Block / trial')
plt.ylabel('Decision time / average block decision time')
plt.suptitle('Decision time of virtual bees on successful runs (green) (114 bees - all completed full experiment)')

plt.show()
fig3.savefig('descision_time_by_block_success.jpg')
fig4 = plt.figure()	
plt.plot(diffs_big_fail_trial_num, diffs_big_fail,'r.')
plt.hold
plt.plot([5,15,25,35,45,55,62],trial_sums_fail, 'r-')
plt.plot([5,15,25,35,45,55,62],trial_sums, 'g-')
plt.xlabel('Block / trial')
plt.ylabel('Decision time / average block decision time')
plt.suptitle('Decision time of virtual bees on failed runs (red) (also successful in green) (114 bees - all completed full experiment)')

plt.show()
fig4.savefig('decision_time_by_block_fail.jpg')

f = open('data_rt.csv','w')
centres=[5,15,25,35,45,55,62]
for i in xrange(len(centres)):
	f.write("{0},{1},{2}\n".format(centres[i],trial_sums[i],trial_sums_fail[i]))
f.close

sum_li = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
num_sum_li = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
temp_li = [[],[],[],[],[],[],[],[]]
for learn_ind in learn_indices_all:
	for i in xrange(0,len(learn_ind)):
		sum_li[i] = sum_li[i] + learn_ind[i]
		num_sum_li[i] = num_sum_li[i] + 1
		temp_li[i] = append(temp_li[i], learn_ind[i])


sum_li_final = []
std_li_final = []
for i in xrange(0,len(sum_li)):
	if num_sum_li[i] > 0:
		sum_li_final.append(average(temp_li[i]))
		std_li_final.append(std(temp_li[i])/sqrt(num_sum_li[i]))
		#sum_li_final.append(sum_li[i]/float(num_sum_li[i]))
	
fig2 = plt.figure()	
print num_sum_li
plt.errorbar(range(len(sum_li_final)),sum_li_final,yerr=std_li_final,fmt='g')
plt.hold

f = open('data_li.csv','w')
for i in xrange(len(sum_li_final)):
	f.write("{0},{1},{2}\n".format(i,sum_li_final[i],std_li_final[i]))
f.close

def frange(x,y,jump):
	while x < y+0.001:
		yield x
		x+=jump

for li in learn_indices_all:
	small_rand = (random.random()-0.5)*0.2
	i = small_rand
	y = []
	while i < small_rand+len(li)-0.001:
		y.append(i)
		i+=1.0
	plt.plot(y, li,'r.')
plt.title("Reward", fontsize=6)
plt.xlabel('Block (final block is transfer test)')
plt.ylabel('Learning index (success/(success+failure))')
plt.suptitle('Performance of virtual bees (101 bees - all completed full experiment)')

fig2.savefig('performance.jpg')
plt.show()
