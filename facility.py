import sys,random
import math
import copy
import numpy as np
from scipy.optimize import linprog
from pulp import *

random.seed(0)

def read_instance():
	folder=sys.argv[1]
	wij_file=open(folder+"weight.txt","r")
	facility_file=open(folder+"facility.txt","r")
	D=[]
	F=[]
	wij={}
	for line in wij_file:
		line=line.strip()
		line=line.split()
		wij[(int(line[0]),int(line[1]))]=float(line[-1])
		if int(line[1])not in D:
			D.append(int(line[1]))
	fi={}
	for line in facility_file:
		line=line.strip()
		line=line.split()
		fi[int(line[0])] = float(line[-1])
		F.append(int(line[0]))
	return (wij,F,fi,D)

#Generate a random instance with f facilities and n clients
def generate_instance(f,n):
	w={}
	F=[]
	fi=[]
	D=[]
	i=0
	while i<f:
		fi.append(random.randint(1,100))
		F.append(i)
		i+=1
	i=0
	while i<f:
		j=0
		while j<n:
			w[(i,j)]=random.randint(1,100)
			if j not in D:
				D.append(j)
			j+=1
		i+=1
	return (w,F,fi,D)

assignment={}

#Find the minimum increase required to have a tight constraint
def checktightnessval (v,w,cij,fi,D,F,T,AlreadyTight):
	min=10000
	newTight=[]
	for i in F:
		if i in T:
			continue
		sum=0
		num_w=0
		for j in D:
			if (i,j) in w:
				sum+=w[(i,j)]
				num_w+=1

		if sum<fi[i]:
			if i in AlreadyTight:
				continue
			else:
				if num_w==0 and min>(fi[i]-sum):
					min=(fi[i]-sum)
				elif num_w>0 and min>(fi[i]-sum)*1.0/num_w:
					min=(fi[i]-sum)*1.0/num_w
	return min

#Check the tightness of the constraints
def checktightness (v,w,cij,fi,D,F,T,AlreadyTight):
	newTight=[]
	#print "checking tight"
	for i in F:
		if i in T:
			continue
		sumval=0
		for j in D:
			if (i,j) in w:
				sumval+=w[(i,j)]
		if round(sumval,2)==round(fi[i],2):
			if i in AlreadyTight:
				continue
			else:
				newTight.append(i)
	#print newTight
	return newTight

#Check if j neighbors some i already in T
def checkNeighbor(v,cij,S,T):
	neigh_lst=[]
	for j in S:
		if not j in v:
			continue
		for i in T: 
			if v[j] >= cij[(i,j)]:
				if j not in neigh_lst:
					neigh_lst.append(j)
				assignment[(i,j)]=1
				#print "neigh",i,j,cij[(i,j)]
	return neigh_lst

#Get the neighbors of a particular value of j
def get_neighborsj(s,v,cij,F):
	neigh_lst=[]
	if not s in v:
		return []
	for i in F:
		if v[s]>=cij[(i,s)]:
			neigh_lst.append(i)
	return neigh_lst

#Get the neighbors for a particular value of i
def get_neighborsi(i,v,cij,S):
	neigh_lst=[]
	for j in S:
		if v[j]>=cij[(i,j)]:
			neigh_lst.append(j)
	return neigh_lst

#Get the minimum value that changes the neighbors for any j
def get_neigh_val(S,v,cij,F):
	minval=10000
	for j in S:
		vval=0
		if j in v:
			vval=v[j]
		#print vval
		for i in F:
			#print cij[i,j],i,j,vval
			if vval<cij[(i,j)]:
				if cij[(i,j)]-vval<minval:
					minval=cij[(i,j)]-vval
	#print minval
	return minval

def facility_problem(cij,fi,D,F):
	#print cij,fi
	v={}
	w={}
	T=[]
	S=copy.deepcopy(D)
	alreadyTight=[]
	#Iterate till all elements in S are not assigned
	while len(S)>0:
		#Increment v and wij untill some inequality becomes tight or a client neighbors a facility already in T
		while True:#s(v,w,cij,fi,D,F):
			new_tight=checktightness(v,w,cij,fi,D,F,T,alreadyTight)
			new_neighborLst=checkNeighbor(v,cij,S,T)
			#print new_tight,"new",new_neighborLst
			if len(new_tight)>0 or len(new_neighborLst)>0:
				#print "breaking"
				break
			v1=get_neigh_val(S,v,cij,F)
			v2=checktightnessval(v,w,cij,fi,D,F,T,alreadyTight)
			v1=min(v1,v2)
			
			for s in S:
				Nj=get_neighborsj(s,v,cij,F)
				for i in Nj:
					if (i,s) in w:
						w[(i,s)]+=v1
					else:
						w[(i,s)]=v1
				if s in v:
					v[s]+=v1
				else:
					v[s]=v1

		#Remove the clients that neighbor any element in T
		for elem in new_neighborLst:
			S.remove(elem)

		#Add the facilities corresponsing new tight inequalities to T
		# and remove the corresponding clients
		for i in new_tight:
			T.append(i)
			neigh=get_neighborsi(i,v,cij,S)
			for j in neigh:
				S.remove(j) 
				#print "neigh",i,j,cij[(i,j)]
				assignment[(i,j)]=1	
		
		alreadyTight.extend(new_tight)

	#Remove all facilities h if a particular client contributes to two facilities i and h
	T1=[]
	while len(T)>0:
		curr=T[0]
		T1.append(T[0])
		del T[0]
		for j in D:
			if (curr,j) in w and w[(curr,j)]>0:
				for h in F:
					if h==curr:
						continue
					if (h,j) in w and h in T:
						del w[(h,j)]
						if (h,j) in assignment:
							assignmen[(h,j)]=0


	print "Set of facilities",T1

	#Calculate Cost
	cost=0
	for (i,j) in assignment:
		cost+=cij[(i,j)]
	for i in T1:
		cost+=fi[i]

	print "cost",cost
	return cost


#ILP solution Courtesy: Sudeep Putta
def ILP(w,fi,D,F):
	primal = LpProblem("Facility Location Primal",LpMinimize)

	y = [LpVariable("y"+str(i),cat='Binary') for i in range(len(F))]
	x = [[LpVariable("x"+str(i)+str(j),cat='Binary') for i in range(len(F))] for j in range(len(D))]

	c_1 = sum(y[i]*fi[i] for i in range(len(F)))
	c_2 = sum(x[j][i]*w[(i,j)] for i in range(len(F)) for j in range(len(D)))

	primal += c_1+c_2

	for j in range(len(D)):
		primal += sum(x[j][i] for i in range(len(F))) == 1

	for i in range(len(F)):
		for j in range(len(D)):
			primal += x[j][i] - y[i] <= 0

	primal.solve()
	primals = {a.name:a.varValue for a in primal.variables()}
	y = [primals["y"+str(i)] for i in range(len(F))]
	x = [[primals["x"+str(i)+str(j)] for i in range(len(F))] for j in range(len(D))]

	Facilities_chosen = {i:{j for j in range(len(D)) if x[j][i]==1.0} for i in range(len(F)) if y[i]==1.0}
	cost = 0
	for i in Facilities_chosen:
		cost+= fi[i]
		for j in Facilities_chosen[i]:
			cost+= w[(i,j)]
	return (cost,Facilities_chosen)


if sys.argv[1]=='1':
	(w,F,fi,D)=generate_instance(3,5)
else:
	(w,F,fi,D)=read_instance()
	

primal_dual_cost=facility_problem(w,fi,D,F)
print "primal-dual cost: ",primal_dual_cost

(ilp_cost,ilp_sol)= ILP(w,fi,D,F)
print "ILP cost:",ilp_cost

print "Approximation",primal_dual_cost*1.0/ilp_cost