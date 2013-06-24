import codecs
import numpy
filelist = open('./filtering-filelist')
summary = [['Filename','Subject', 'Acc_total', 'RT_2_0',  'Acc_2_0', 'RT_2_2', 'Acc_2_2', 'RT_2_4', 'Acc_2_4', 'RT_2_6', 'Acc_2_6']]

def id_outliers(list_of_RTs, check_depth, max_step): #Takes a list of response times, an int indicating how many RTs on either end of the sorted list should be evaluated, and an int indicating how large of a jump between two sequential RTs in these end regions designates the start of the outliers.  
        if check_depth < 2:
                check_depth = 2
                if check_depth > len(list_of_RTs)/2:
                        return []
        list_of_RTs.sort()
        replace_RTs = []
        trigger = 0
        #print list_of_RTs[:check_depth]
        #print list_of_RTs[-check_depth:]
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
	rtsbycase = {'2_0':[], '2_2':[], '2_4':[], '2_6':[]}
	for row in datafile:
		if row.count(',') < 50:
			continue
		activerow = row.strip().split(',')
		if activerow[41].find("2_") > -1:
			if activerow[52] == '1' or activerow[52] == '0':
				if activerow[52] == '1':
					rts_acc.append(int(activerow[59]))
				else:
					rts_inacc.append(int(activerow[59]))
				activerow = activerow[1]+','+activerow[41]+','+activerow[52]+','+activerow[53]+','+activerow[59]
				datarows.append(activerow)
	
	replacerts = id_outliers(rts_acc, 6, 100)

	for row in datarows:
		activerow = row.strip().split(',')
		for rt in replacerts:
			if int(activerow[4]) == rt[0]:
				activerow[4] = unicode(str(rt[1]))
		rtsbycase[activerow[1][:3]].append(activerow)
		activerow = ','.join(activerow)
	print "Number of trials was: " +  str(len(datarows))
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0], str(float(len(rts_acc))/float(len(datarows)))]	
	for case, dataarray in rtsbycase.iteritems():
		allrts = [int(datapoint[4]) for datapoint in dataarray]
		correctrts = [int(datapoint[4]) for datapoint in dataarray if datapoint[2] == '1']
		wrongrts = [int(datapoint[4]) for datapoint in dataarray if datapoint[2] == '0']
#		hits = [int(datapoint[4]) for datapoint in dataarray if datapoint[2] == '1' and datapoint[3] == '4']
#		falsealerts = [int(datapoint[4]) for datapoint in dataarray if datapoint[2] == '0' and datapoint == '4']
		
		print "Mean for "+case+" is: "+ str(numpy.mean(correctrts))
		filereport.append(str(numpy.mean(correctrts)))
		filereport.append(str(float(len(correctrts))/float(len(allrts))))
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
