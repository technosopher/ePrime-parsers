# This script assumes that ePrime files have been exported as CSV files with commas as field deliminators.  
import codecs
import numpy
import argparse

filelist = []
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datafiles", type=str, nargs='+', help="List of one or more datafiles")
parser.add_argument("-f", "--filelist", type=str, help="Single file containing a list of datafiles")
args = parser.parse_args()
if args.filelist:
        f = open(args.filelist)
        for filename in f:
                filelist.append(filename.strip())
elif args.datafiles:
        filelist = args.datafiles
else:
        print "You must specify where the datafile(s) are located using either the --datafiles or --filelist parameter.  Run the script with --help for more information.  Exiting..."
        exit()

summary = [['Filename','Subject', '%ACC-total', 'Mean RT-ACC_total', 'Mean RT-INACC_total', '%ACC-all_nonswitch', 'Mean RT-ACC-all_nonswitch', 'Mean RT-INACC_all_nonswitch', '%ACC-all_switch', 'Mean RT-ACC_all_switch', 'Mean RT-INACC_all_switch', '%ACC-nonswitch1', 'Mean RT-ACC-nonswitch1', 'Mean RT-INACC_nonswitch1', '%ACC-nonswitch2', 'Mean RT-ACC-nonswitch2', 'Mean RT-INACC_nonswitch2', '%ACC-nonswitch3', 'Mean RT-ACC-nonswitch3', 'Mean RT-INACC_nonswitch3', '%ACC-switch1', 'Mean RT-ACC_switch1', 'Mean RT-INACC_switch1', '%ACC-switch2', 'Mean RT-ACC_switch2', 'Mean RT-INACC_switch2', '%ACC-switch3', 'Mean RT-ACC_switch3', 'Mean RT-INACC_switch3', '%ACC-switch4', 'Mean RT-ACC_switch4', 'Mean RT-INACC_switch4']]

def id_outliers(list_of_RTs, check_depth, max_step): #Takes a list of response times, an integer indicating how many RTs on either end of the sorted list should be evaluated, and an integer indicating how large of a jump between two sequential RTs in these end regions designates the start of the outliers.  
	if check_depth < 2:  
		check_depth = 2 #Check at least the two most extreme values at either end of the list
		if check_depth > len(list_of_RTs)/2: #If there are fewer than four values in the entire list, it makes no sense to declare any of them to be outliers,
			return [] #so we return an empty list
	list_of_RTs.sort() 
	replace_RTs = []
	trigger = 0
	#print list_of_RTs[:check_depth]
	#print list_of_RTs[-check_depth:]
	for i in range(len(list_of_RTs[:check_depth])-1,-1,-1): #Loop through the first (n=check_depth) values of list_of_RTs, backwards, such that values are processed from least extreme to most extreme
		if trigger > 0: #If a gap of max_step has already been identified in a prior comparison
			replace_RTs.append([list_of_RTs[:check_depth][i],trigger]) #Add current RT to list of RTs to be changed
		elif i < 0:
			break #No list items left to process
		elif list_of_RTs[:check_depth][i]-list_of_RTs[:check_depth][i-1] > max_step: #If gap between current RT and prior RT is greater than max_step, activate the trigger
			trigger = list_of_RTs[:check_depth][i]
	trigger = 0
	for i in range(len(list_of_RTs[-check_depth:])): #Loop through the last (n=check_depth) values of list_of_RTs, forwards, such that values are checked from least extreme to most extreme
		if trigger > 0:
			replace_RTs.append([list_of_RTs[-check_depth:][i],trigger])
		elif i == len(list_of_RTs[-check_depth:])-1:
			break
		elif list_of_RTs[-check_depth:][i+1]-list_of_RTs[-check_depth:][i] > max_step:
			trigger = list_of_RTs[-check_depth:][i]
	#print replace_RTs
	return replace_RTs #Returns a list of pairs of [Original RTs, Replacement RTs]

for filename in filelist:
        print "Now processing " + filename.strip()
        datafile = codecs.open(filename.strip(),encoding='utf16') #ePrime outputs files encoded in the utf16 character encoding.  who knows why.  
	datarows = []
	rts_acc = []
	rts_inacc = []
	datarowsbytrialtype = {'all_switch':[], 'switch1':[], 'switch2':[], 'switch3':[], 'switch4':[] , 'all_nonswitch':[], 'nonswitch1':[], 'nonswitch2':[], 'nonswitch3':[], 'all':[]} 
        for row in datafile:
                if row.count(',') < 80: #Skip any rows in the file that don't contain approximately the right number of data fields
                        continue
		activerow = row.strip().split(',')
		if activerow[82] == '1' or activerow[82] == '0': #If the active row contains a "real" trial (as opposed to a test/demo trial, for which this value is NULL)
			if activerow[82] == '1':
				rts_acc.append(int(activerow[89]))
			else:
				rts_inacc.append(int(activerow[89]))
			activerow = activerow[1]+','+activerow[72]+','+activerow[82]+','+activerow[89] #Subject, Cue Type (L/N), Correct, Response Time
			datarows.append(activerow)
	#print len(datarows)
	#print len(rts_acc)
	#print len(rts_inacc)
	replacerts_acc = id_outliers(rts_acc, len(rts_acc)/20, 200) #Check for/replace all outliers in the list of correct response times
	replacerts_inacc = id_outliers(rts_inacc, len(rts_inacc)/20, 200) #Check for/replace all outliers in the list of incorrect response times
	#print "Replacing"
	#print replacerts_acc
	#print replacerts_inacc

	priorstim = [datarows[0].strip().split(',')[1], 1] #Switch status marker: [0]: case of last stim; [1]: historical depth of prior case
	for i in range(0, len(datarows)):
		activerow = datarows[i].strip().split(',')
		if activerow[2] == '1': #Replace the outliers identified previously with the normalized values
			for rt in replacerts_acc:
				if int(activerow[3]) == rt[0]:
					activerow[3] = unicode(str(rt[1]))
		else:
			for rt in replacerts_inacc:
				if int(activerow[3]) == rt[0]:
					activerow[3] = unicode(str(rt[1]))
		datarowsbytrialtype['all'].append(activerow)

		if i == 0:
			#print str(priorstim[0]) + ": This is the first trial."
			datarowsbytrialtype['all_nonswitch'].append(activerow)
			continue
		if activerow[1] == priorstim[0]: #For non-switch trials:
			#print str(activerow[1]) + ": This is a nonswitch-" + str(priorstim[1]) + " trial"
			datarowsbytrialtype['all_nonswitch'].append(activerow) #Add this trial's data to the all_nonswitch pool
			datarowsbytrialtype['nonswitch'+str(priorstim[1])].append(activerow) #Add this trial's data to the appropriate nonswitch-n pool
			priorstim[1] += 1 #Increment historical depth counter
		else: #For switch trials:
			#print str(activerow[1]) + ": This is a switch-" + str(priorstim[1]) + " trial"
			datarowsbytrialtype['all_switch'].append(activerow) #Add this trial's data to the all_switch pool
			datarowsbytrialtype['switch'+str(priorstim[1])].append(activerow) #Add this trial's data to the appropriate switch-n pool
			priorstim[0] = activerow[1] #Set the "prior stimulus" variable to the type of this trial.  
			priorstim[1] = 1 #Reset historical depth counter
			
	filereport = [filename[filename.rfind('/')+1:].strip(), datarows[0].strip().split(',')[0]] #
	for case, dataarray in iter(sorted(datarowsbytrialtype.iteritems())): #Sort the dictionary to ensure that the outputs of the iterator align with the static column headers defined above
		correctrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '1'] #Assemble a list of all correct response times
		wrongrts = [int(datapoint[3]) for datapoint in dataarray if datapoint[2] == '0'] #Assemble a list of all incorrect response times
		#print correctrts
		#print case
		numtrials = len(dataarray)
		#print "Total number of " + case + " responses: " + str(numtrials)
		#print "Number of correct " + case + " responses: " + str(len(correctrts))
		#print "Number of incorrect " + case + " responses: " + str(len(wrongrts))
		if numtrials == 0:
			numtrials = 1 #To deal with errors thrown by dividing zero by zero
		filereport.append(str(float(len(correctrts))/float(numtrials))) #Calculate accuracy rate for this type of trial
		filereport.append(str(numpy.mean(correctrts))) #Calculate mean response time for all accurate trials of this type
		filereport.append(str(numpy.mean(wrongrts))) #Calculate mean response time for all inaccurate trials of this type
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

