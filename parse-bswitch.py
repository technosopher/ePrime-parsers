import codecs
import numpy
filelist = open('./bswitch-filelist')
summary = [['Filename','Subject', '%ACC-switch', 'Mean RT-ACC_switch', 'Mean RT-INACC_switch', '%ACC-nonswitch', 'Mean RT-ACC-nonswitch', 'Mean RT-INACC_nonswitch', '%ACC-total', 'Mean RT-ACC_total', 'Mean RT-INACC_total']]

for filename in filelist:
        print "Now processing " + filename.strip()
        datafile = codecs.open(filename.strip(),encoding='utf16')
	datarows = []
	rts = []
	datarowsbycase = {'switch':[], 'nonswitch':[], 'all':[]}
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
	priorstim = datarows[0].strip().split(',')[1]
	#print priorstim
	for i in range(0, len(datarows)):
		activerow = datarows[i].strip().split(',')
		for rt in replacerts:
			if int(activerow[3]) == rt[0]:
				activerow[3] = unicode(str(rt[1]))
		datarowsbycase['all'].append(activerow)
		if activerow[1]  == priorstim:
			datarowsbycase['nonswitch'].append(activerow)
		else:
			datarowsbycase['switch'].append(activerow)
			priorstim = activerow[1]

	#print datarowsbycase
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0]]
	for case, dataarray in datarowsbycase.iteritems():
		correctrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '1']
		wrongrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '0']
		#print correctrts
		print "% accuracy for " + case + " trials: " + str(float(len(correctrts))/float(len(dataarray)))
		print "% inaccuracy for " + case + " trials: " + str(float(len(wrongrts))/float(len(dataarray)))
		#print "Average response time for correct answers for " + case + " trials: " + str(numpy.mean(correctrts))
		print "Average response time for wrong answers for " + case + " trials: " + str(numpy.mean(wrongrts))
		filereport.append(str(float(len(correctrts))/float(len(dataarray))))
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
        report.write(','.join(row) + "\n")
report.write("\n")
report.close();

