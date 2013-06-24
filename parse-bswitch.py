import codecs
import numpy
filelist = open('./bswitch-filelist')
summary = [['Filename','Subject', '%ACC-total', 'Mean RT-ACC_total', 'Mean RT-INACC_total', '%ACC-all_nonswitch', 'Mean RT-ACC-all_nonswitch', 'Mean RT-INACC_all_nonswitch', '%ACC-all_switch', 'Mean RT-ACC_all_switch', 'Mean RT-INACC_all_switch', '%ACC-nonswitch1', 'Mean RT-ACC-nonswitch1', 'Mean RT-INACC_nonswitch1', '%ACC-nonswitch2', 'Mean RT-ACC-nonswitch2', 'Mean RT-INACC_nonswitch2', '%ACC-nonswitch3', 'Mean RT-ACC-nonswitch3', 'Mean RT-INACC_nonswitch3', '%ACC-nonswitch4', 'Mean RT-ACC-nonswitch4', 'Mean RT-INACC_nonswitch4', '%ACC-switch1', 'Mean RT-ACC_switch1', 'Mean RT-INACC_switch1', '%ACC-switch2', 'Mean RT-ACC_switch2', 'Mean RT-INACC_switch2', '%ACC-switch3', 'Mean RT-ACC_switch3', 'Mean RT-INACC_switch3', '%ACC-switch4', 'Mean RT-ACC_switch4', 'Mean RT-INACC_switch4']]

def id_outliers(list_of_RTs, check_depth, max_step): #Takes a list of response times, an int indicating how many RTs on either end of the sorted list should be evaluated, and an int indicating how large of a jump between two sequential RTs in these end regions designates the start of the outliers.  
	if check_depth < 2:
		check_depth = 2
		if check_depth > len(list_of_RTs)/2:
			return []
	list_of_RTs.sort()
	replace_RTs = []
	trigger = 0
	print list_of_RTs[:check_depth]
	print list_of_RTs[-check_depth:]
	for i in range(len(list_of_RTs[:check_depth])-1,-1,-1):
		if trigger > 0:
			replace_RTs.append([list_of_RTs[:check_depth][i],trigger])
		elif i < 0:
			break	
		elif list_of_RTs[:check_depth][i]-list_of_RTs[:check_depth][i-1] > max_step:
			trigger = list_of_RTs[:check_depth][i]
	trigger = 0
	for i in range(len(list_of_RTs[-check_depth:])):
		if trigger > 0:
			replace_RTs.append([list_of_RTs[-check_depth:][i],trigger])
		elif i == len(list_of_RTs[-check_depth:])-1:
			break
		elif list_of_RTs[-check_depth:][i+1]-list_of_RTs[-check_depth:][i] > max_step:
			trigger = list_of_RTs[-check_depth:][i]
	print replace_RTs
	return replace_RTs #Returns a list of pairs of [Original RTs, Replacement RTs]

for filename in filelist:
        print "Now processing " + filename.strip()
        datafile = codecs.open(filename.strip(),encoding='utf16')
	datarows = []
	rts_acc = []
	rts_inacc = []
	datarowsbycase = {'all_switch':[], 'switch1':[], 'switch2':[], 'switch3':[], 'switch4':[] , 'all_nonswitch':[], 'nonswitch1':[], 'nonswitch2':[], 'nonswitch3':[], 'all':[]}
        for row in datafile:
                if row.count(',') < 80:
                        continue
		activerow = row.strip().split(',')
		if activerow[82] == '1' or activerow[82] == '0':
			if activerow[82] == '1':
				rts_acc.append(int(activerow[89]))
			else:
				rts_inacc.append(int(activerow[89]))
			activerow = activerow[1]+','+activerow[72]+','+activerow[82]+','+activerow[89] #Subject, Cue Type (L/N), If Correct, Response Time
			datarows.append(activerow)
	print len(datarows)
	print len(rts_acc)
	print len(rts_inacc)
	replacerts_acc = id_outliers(rts_acc, len(rts_acc)/20, 200) 
	replacerts_inacc = id_outliers(rts_inacc, len(rts_inacc)/20, 200) 
	print "Replacing"
	print replacerts_acc
	print replacerts_inacc

	#print datarows
	priorstim = [datarows[0].strip().split(',')[1], 1] #Switch status marker: [0]: case of last stim; [1]: historical depth of prior case
	#print priorstim
	for i in range(0, len(datarows)):
		activerow = datarows[i].strip().split(',')
		if activerow[2] == '1':
			for rt in replacerts_acc:
				if int(activerow[3]) == rt[0]:
					activerow[3] = unicode(str(rt[1]))
		else:
			for rt in replacerts_inacc:
				if int(activerow[3]) == rt[0]:
					activerow[3] = unicode(str(rt[1]))
			
		datarowsbycase['all'].append(activerow)
		if i == 0:
			print str(priorstim[0]) + ": This is the first trial."
			continue
		if activerow[1] == priorstim[0]:
			datarowsbycase['all_nonswitch'].append(activerow)
			datarowsbycase['nonswitch'+str(priorstim[1])].append(activerow)
			print str(activerow[1]) + ": This is a nonswitch-" + str(priorstim[1]) + " trial"
			priorstim[1] += 1
			
		else:
			datarowsbycase['all_switch'].append(activerow)
			datarowsbycase['switch'+str(priorstim[1])].append(activerow)
			print str(activerow[1]) + ": This is a switch-" + str(priorstim[1]) + " trial"
			priorstim[0] = activerow[1]
			priorstim[1] = 1
			
	#print datarowsbycase
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0]]
	for case, dataarray in iter(sorted(datarowsbycase.iteritems())):
		correctrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '1']
		wrongrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '0']
		#print correctrts
		numtrials = len(dataarray)
		print "Total number of " + case + " responses: " + str(numtrials)
		print "Number of correct " + case + " responses: " + str(len(correctrts))
		#print "Number of incorrect " + case + " responses: " + str(len(wrongrts))
		if numtrials == 0:
			numtrials = 1 #To deal with errors thrown by dividing zero by zero
		filereport.append(str(float(len(correctrts))/float(numtrials)))
		filereport.append(str(numpy.mean(correctrts)))
		filereport.append(str(numpy.mean(wrongrts)))
#	print filereport
        datafile.close()
        summary.append(filereport)
report = codecs.open('./bswitch-report.csv','w',encoding='utf16')
for row in summary:
#	for entry in row:
#		if entry.find('nan') > 0:
#			entry = 'NULL'
        report.write(','.join(row) + "\n")
report.write("\n")
report.close();

