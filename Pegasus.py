

#------------------------------------------------------------------------------------------------------------------------------------
# Function to generate Unique 10 digit ID for every agent 
def genuid (i):
	uid = []
	for j in range(3) :
		uid.append(chr(random.randint(65,90)))
	uid.append(str(i))
	for j in range(10-len(uid)) :
		uid.append(str(random.randint(0,9)))
	return "".join(uid)
#------------------------------------------------------------------------------------------------------------------------------------

#Function to generate realistic data for N members of a population

def generate_data(N,filename) :
	import csv
	import random
	f = open(filename,'w')
	csvout = csv.writer(f)
	data = []
	fields = ["Agent ID", "Net monthly income", "Initial Reserve",'Shock Rate', "Mean Shock Size distribution", "Ruin Probability"]
	csvout.writerow(fields)
	for i in range(N) :
		c = random.randint(1,1000)
		u = random.randint(0,1000)
		if u == 0 :
			μ = random.random()*c
			β = (random.random()*c/μ)
			Ψ = β*μ/c
		else :
			μ = random.random()*u
			β = random.random()*(u*c)/μ
			Ψ = (β*μ)/(u*c)
		data.append([genuid(i),c,u,β,μ,Ψ])
	csvout.writerows(data)
	f.close()
	
#------------------------------------------------------------------------------------------------------------------------------------

#Function to sort data on a header basis   

def sort_data(filename,basis) :
	import pandas as pd
	global sorteddata,sortbyrp
	f = open(filename,'r')
	data = pd.read_csv(f)
	sortbyrp = (basis=='Ruin Probability')
	sorteddata = data.sort_values(by=[basis],ascending=False)
	f.close()
	sorteddata.index = data.index
	sorteddata = sorteddata.values.tolist()
	return 

#------------------------------------------------------------------------------------------------------------------------------------

#Function to compute subsidy to reach the rp of agent number goal

def subsidy (goal,current=0) :
	global sortbyrp,sorteddata
	if not sortbyrp :
		raise Exception('Sort Error : Data not sorted by Ruin Probability')
	xi = []
	sdc = sorteddata[current]
	sdg = sorteddata[goal]
	while current < goal and (sdg[-1]-sdc[-1]) < 0:
		sdc = sorteddata[current]
		if sorteddata[current][2] == 0 :
			xi.append((sdc[3]*sdc[4]/sdg[-1]) - sdc[1])
		else :
			xi.append(((sdc[3]*sdc[4])/(sdg[-1]*sdc[2])) - sdc[1])
		current+=1
	return sum(xi)

#------------------------------------------------------------------------------------------------------------------------------------

#How many agents benefit in population size of n and budget of target

def HowManyBenefit(n, target):
	global xi
	# Corner cases
	if (target <= subsidy(1)):
		return 0
	if target >= subsidy(n - 1):
		return (n - 1)

	# Doing binary search
	i = 0; j = n; mid = 0
	while (i < j):
		mid = (i + j) // 2
		sm = subsidy(mid)
		tempsub = xi

		if (sm == target):
			return mid

		# If target is less than total subsidy
		# then search in left
		if (target < sm) :

			# If target is greater than previous
			# to mid, return lesser of two
			if (mid > 0 and target > subsidy(mid - 1)):
				return mid-1

			# Repeat for left half
			j = mid
		
		# If target is greater than mid
		else :
			
			if (mid < n - 1 and target < subsidy(mid + 1)):
				xi = tempsub
				return mid
				
			# update i
			i = mid + 1

	return mid

#------------------------------------------------------------------------------------------------------------------------------------

# View results

def viewresults() :
	import matplotlib.pyplot as plt
	global xi,sorteddata
	plt.style.use("dark_background")
	plt.scatter(range(N),[sorteddata[i][-1] for i in range(N)],color='r')
	plt.ylabel("Ruin probability")
	plt.xlabel("Agent number")
	plt.title("RP before allocation")
	plt.show()
	rp = []
	for i in range(len(xi)) :
		sd = sorteddata[i]
		if sd[2] == 0 :
			rp.append((sd[3]*sd[4])/(sd[1]+xi[i]))
		else :
			rp.append((sd[3]*sd[4])/(sd[2]*(sd[1]+xi[i])))
	for i in range(len(xi),len(sorteddata),1) :
		rp.append(sorteddata[i][-1])
	plt.scatter(range(N),rp,color='r')
	plt.ylim(0,1)
	plt.ylabel("Ruin probability")
	plt.xlabel("Agent number")
	plt.title("RP after allocation")
	plt.show()

#------------------------------------------------------------------------------------------------------------------------------------