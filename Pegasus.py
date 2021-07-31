

#---------------------------------------------------------------------------------------------------------------------------
# Function to generate Unique 10 digit ID for every agent 
def genuid (N):
    import random
    agentid = []
    for i in range (N) :
        uid = []
        for j in range(3) :
            uid.append(chr(random.randint(65,90)))
        uid.append(str(i))
        for j in range(10-len(uid)) :
            uid.append(str(random.randint(0,9)))
        agentid.append("".join(uid))
    return agentid
#---------------------------------------------------------------------------------------------------------------------------

#Function to simulate a realistic population 

def gen_popn(filename = "Database.csv", pop_size=10000, c_min=10, u_min=5):
    import csv
    import numpy as np
    global N,a
    N = pop_size
    a = u_min
    f = open(filename,'w')
    csvout = csv.writer(f)
    csvout.writerow(["Agent ID", "Net monthly income", "Initial Reserve",'Shock Rate', "Mean Shock Size distribution", "Ruin Probability"])
    c = np.random.poisson(2*np.log(10), size=(N, 1)) * c_min + c_min
    u = np.random.exponential(0.4, size=(N, 1)) * \
        c_min**2  # np.zeros(shape=(N, 1))
    mu = a*u * np.exp(np.divide(-u, a))
    mu[u < a] = a**2/np.e
    beta = np.random.uniform(np.zeros((N, 1)), c*u/mu)
    beta[u < a] = np.random.uniform(np.zeros((N, 1)), c/mu)[u < a]
    psi = beta*mu/c
    psi[u > a] = (beta*mu/(u*c))[u > a]
    popn = np.column_stack((genuid(N), c, u, beta, mu, psi))
    csvout.writerows(popn)
    f.close()
    return popn

#---------------------------------------------------------------------------------------------------------------------------


#Function to generate random data for N members of a population

def gen_random_popn(N,filename) :
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
    
#---------------------------------------------------------------------------------------------------------------------------

#Function to sort data on a header basis   

def sort_data(filename = "Database.csv",basis = "Ruin Probability") :
    import pandas as pd
    global sorteddata,sortbyrp
    f = open(filename,'r')
    data = pd.read_csv(f)
    sortbyrp = (basis=='Ruin Probability')
    sorteddata = data.sort_values(by=[basis],ascending=False)
    f.close()
    sorteddata.index = data.index
    sorteddata = sorteddata.values.tolist()
    return sorteddata

#------------------------------------------------------------------------------------------------------------------------------------

#Function to compute subsidy to reach the rp of agent number goal

def subsidy (goal) :
    import math
    global sortbyrp,sorteddata,xi,N,a
    try : sortbyrp
    except NameError : sort_data()
    if not sortbyrp :
        sort_data()
    try : a
    except NameError : a = math.sqrt(math.e*sorted(sorteddata, key=lambda x: x[4])[-1][4])
    sdg = sorteddata[goal]
    xi = []
    current = 0
    sdc = sorteddata[current]
    while current < goal and (sdg[-1]-sdc[-1]) < 0:
        sdc = sorteddata[current]
        if sorteddata[current][2] < a :
            xi.append((sdc[3]*sdc[4]/sdg[-1]) - sdc[1])
        else :
            xi.append(((sdc[3]*sdc[4])/(sdg[-1]*sdc[2])) - sdc[1])
        current+=1
    return sum(xi)

#------------------------------------------------------------------------------------------------------------------------------------

#How many agents benefit in population size of n and budget of target

def HowManyBenefit(target):
    global xi,N,sorteddata
    try: sorteddata
    except NameError: sort_data()
    try: N
    except NameError: N = len(sorteddata) 

    # Corner cases
    if (target <= subsidy(1)):
        return 0
    if target >= subsidy(N - 1):
        return (N - 1)

    # Doing binary search
    i = 0; j = N; mid = 0
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
            
            if (mid < N - 1 and target < subsidy(mid + 1)):
                xi = tempsub
                return mid
                
            # update i
            i = mid + 1

    return mid

#------------------------------------------------------------------------------------------------------------------------------------

# View results

def viewresults() :
    global N,a,xi,sorteddata
    import matplotlib.pyplot as plt
    try: N
    except NameError: N = len(sorteddata) 
    plt.style.use("dark_background")
    plt.scatter(range(N),[sorteddata[i][-1] for i in range(N)],color='r')
    plt.ylabel("Ruin probability")
    plt.xlabel("Agent number")
    plt.title("RP before allocation")
    xmin, xmax, ymin, ymax = plt.axis()
    plt.show()
    rp = []
    for i in range(len(xi)) :
        sd = sorteddata[i]
        if sd[2] < a:
            rp.append((sd[3]*sd[4])/(sd[1]+xi[i]))
        else :
            rp.append((sd[3]*sd[4])/(sd[2]*(sd[1]+xi[i])))
    for i in range(len(xi),len(sorteddata),1) :
        rp.append(sorteddata[i][-1])
    plt.scatter(range(len(xi)),rp[:len(xi)],color='g')
    plt.scatter(range(len(xi),N),rp[len(xi):N],color='r')
    plt.ylim(ymin,ymax)
    plt.ylabel("Ruin probability")
    plt.xlabel("Agent number")
    plt.title("RP After Allocation")
    plt.show()

#------------------------------------------------------------------------------------------------------------------------------------

#Function to only subsidize to given rp

def setrplimit (goal) :
    import math
    global sortbyrp,sorteddata,xi,a
    try: sortbyrp
    except NameError : sort_data()
    if not sortbyrp :
        sort_data()
    try: a
    except NameError : a = math.sqrt(math.e*sorted(sorteddata, key=lambda x: x[4])[-1][4])
    if goal > 1 or goal < 0 :
        raise Exception('Range Error : RP must be between 0 and 1')
    xi = []
    current = 0
    sdc = sorteddata[current]
    while sdc[-1] > goal :
        sdc = sorteddata[current]
        if sorteddata[current][2] < a :
            xi.append((sdc[3]*sdc[4]/goal) - sdc[1])
        else :
            xi.append(((sdc[3]*sdc[4])/(goal*sdc[2])) - sdc[1])
        current+=1
    return sum(xi)

#------------------------------------------------------------------------------------------------------------------------------------

def statistics(scheme,show_subsidy=False) :
    import matplotlib.pyplot as plt
    global xi,N
    try: N
    except NameError: N = len(sorteddata) 
    print(f"Scheme : {scheme}")
    print(f"Percentage population helped : {len(xi)*100/N}%")
    print(f"Budget required : {round(sum(xi),3)} units")
    print(f"RP Limit : {sorteddata[len(xi)][-1]}")
    if show_subsidy :
        plt.style.use("dark_background")
        plt.scatter(range(len(xi)),xi,color='r')
        plt.xlabel("Agent Number")
        plt.ylabel("Income subsidy")
        plt.title(scheme)
    return
        
#------------------------------------------------------------------------------------------------------------------------------------