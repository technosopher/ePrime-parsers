import codecs
import numpy
filelist = open('./filtering-filelist')
summary = [['Filename','Subject', '2_0 RT', '2_2 RT', '2_4 RT', '2_6 RT']]
for filename in filelist:
	print "Now processing " + filename.strip()
	datafile = codecs.open(filename.strip(),encoding='utf16')
	datarows = []
	rts = []
	rtsbycase = {'2_0':[], '2_2':[], '2_4':[], '2_6':[]}
	for row in datafile:
		if row.count(',') < 50:
			continue
		activerow = row.strip().split(',')
		if activerow[52] == '1':
			if activerow[41].find("2_") > -1:
				rts.append(int(activerow[59]))
				activerow = activerow[1]+','+activerow[41]+','+activerow[52]+','+activerow[59]
				datarows.append(activerow)

	rts.sort()
	replacerts = []
	trigger = 0
	for i in range(len(rts[:6])-1,-1,-1):
		if trigger > 0:
			replacerts.append((rts[:6][i],trigger))
		elif i < 0:
			break	
		elif rts[:6][i]-rts[:6][i-1] > 100:
			trigger = rts[:6][i]
	trigger = 0
	for i in range(len(rts[-6:])):
		if trigger > 0:
			replacerts.append((rts[-6:][i],trigger))
		elif i == len(rts[-6:])-1:
			break
		elif rts[-6:][i+1]-rts[-6:][i] > 100:
			trigger = rts[-6:][i]

	#print rts[:6]
	#print rts[-6:]
	#print "Replacing"
	#print replacerts

	for row in datarows:
		activerow = row.strip().split(',')
		for rt in replacerts:
			if int(activerow[3]) == rt[0]:
				activerow[3] = unicode(str(rt[1]))
		rtsbycase[activerow[1][:3]].append(int(activerow[3]))
		activerow = ','.join(activerow)
	
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0]]	
	for case, rts in rtsbycase.iteritems():
		print "Mean for "+case+" is: "+ str(numpy.mean(rts))
		filereport.append(str(numpy.mean(rts)))
	#	print rts
	#	print "Size: "+str(len(rts))
	datafile.close()
	#print filereport
	summary.append(filereport)
report = codecs.open('./filtering-report.csv','w',encoding='utf16')
for row in summary:
	report.write(','.join(row) + "\n")
report.write("\n")
report.close();
