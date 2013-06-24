import codecs
import numpy
filelist = open('./bswitch-filelist')
summary = [['Filename','Subject', '%ACC-total', 'Mean RT-ACC_total', 'Mean RT-INACC_total', '%ACC-all_nonswitch', 'Mean RT-ACC-all_nonswitch', 'Mean RT-INACC_all_nonswitch', '%ACC-all_switch', 'Mean RT-ACC_all_switch', 'Mean RT-INACC_all_switch', '%ACC-nonswitch0', 'Mean RT-ACC-nonswitch0', 'Mean RT-INACC_nonswitch0', '%ACC-nonswitch1', 'Mean RT-ACC-nonswitch1', 'Mean RT-INACC_nonswitch1', '%ACC-nonswitch2', 'Mean RT-ACC-nonswitch2', 'Mean RT-INACC_nonswitch2', '%ACC-nonswitch3', 'Mean RT-ACC-nonswitch3', 'Mean RT-INACC_nonswitch3', '%ACC-switch0', 'Mean RT-ACC_switch0', 'Mean RT-INACC_switch0' '%ACC-switch1', 'Mean RT-ACC_switch1', 'Mean RT-INACC_switch1', '%ACC-switch2', 'Mean RT-ACC_switch2', 'Mean RT-INACC_switch2', '%ACC-switch3', 'Mean RT-ACC_switch3', 'Mean RT-INACC_switch3', '%ACC-switch4', 'Mean RT-ACC_switch4', 'Mean RT-INACC_switch4']]

for filename in filelist:
        print "Now processing " + filename.strip()
        datafile = codecs.open(filename.strip(),encoding='utf16')
	datarows = []
	rts = []
	datarowsbycase = {'all_switch':[], 'switch0':[], 'switch1':[], 'switch2':[], 'switch3':[], 'switch4':[] , 'all_nonswitch':[], 'nonswitch0':[], 'nonswitch1':[], 'nonswitch2':[], 'nonswitch3':[], 'all':[]}
        for row in datafile:
                if row.count(',') < 80:
                        continue
		activerow = row.strip().split(',')
		if activerow[82] == '1' or activerow[82] == '0':
			rts.append(int(activerow[89]))
			activerow = activerow[1]+','+activerow[72]+','+activerow[82]+','+activerow[89] #Subject, Cue Type (L/N), If Correct, Response Time
			datarows.append(activerow)

	rts.sort()
	replacerts = []
	trigger = 0
	for i in range(len(rts[:10])-1,-1,-1):
		if trigger > 0:
			replacerts.append((rts[:10][i],trigger))
		elif i == 0:
			break	
		elif rts[:10][i]-rts[:10][i-1] > 100:
			trigger = rts[:10][i]
	trigger = 0
	for i in range(len(rts[-10:])):
		if trigger > 0:
			replacerts.append((rts[-10:][i],trigger))
		elif i == len(rts[-10:])-1:
			break
		elif rts[-10:][i+1]-rts[-10:][i] > 100:
			trigger = rts[-10:][i]

	print rts[:10]
	print rts[-10:]
	print "Replacing"
	print replacerts

	#print datarows
	priorstim = [datarows[0].strip().split(',')[1], 0, 0] #Switch status marker: [0]: case of last stim; [1]: switch depth; [2]: non-switch depth
	#print priorstim
	for i in range(0, len(datarows)):
		activerow = datarows[i].strip().split(',')
		for rt in replacerts:
			if int(activerow[3]) == rt[0]:
				activerow[3] = unicode(str(rt[1]))
		datarowsbycase['all'].append(activerow)
		if activerow[1] == priorstim[0]:
			datarowsbycase['all_nonswitch'].append(activerow)
			datarowsbycase['nonswitch'+str(priorstim[2])].append(activerow)
			priorstim[1] = 0
			priorstim[2] += 1
			
		else:
			datarowsbycase['all_switch'].append(activerow)
			datarowsbycase['switch'+str(priorstim[1])].append(activerow)
			priorstim[0] = activerow[1]
			priorstim[1] += 1
			priorstim[2] = 0
			
	#print datarowsbycase
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0]]
	for case, dataarray in iter(sorted(datarowsbycase.iteritems())):
		correctrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '1']
		wrongrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '0']
		#print correctrts
		numtrials = len(dataarray)
		print "Number of " + case + " trials: " + str(numtrials)
		if numtrials == 0:
			numtrials = 1
		print "% accuracy for " + case + " trials: " + str(float(len(correctrts))/float(numtrials))
		#print "% inaccuracy for " + case + " trials: " + str(float(len(wrongrts))/float(len(dataarray)))
		print "Average response time for correct answers for " + case + " trials: " + str(numpy.mean(correctrts))
		print "Average response time for wrong answers for " + case + " trials: " + str(numpy.mean(wrongrts))
		filereport.append(str(float(len(correctrts))/float(numtrials)))
		filereport.append(str(numpy.mean(correctrts)))
		filereport.append(str(numpy.mean(wrongrts)))
#	activerow = ','.join(activerow)
#	print activerow
# for case, rts in rtsbycase.iteritems():
#	print "Mean for "+case+" is: "+ str(numpy.mean(rts))
#	print rts
#	print "Size: "+str(len(rts))
	print filereport
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

