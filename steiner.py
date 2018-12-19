import sys,copy

import networkx as nx
from networkx.algorithms.connectivity import local_edge_connectivity

import random
random.seed(0)

#Read an instance from file
def read_instance():
	folder=sys.argv[1]
	graph_file=open(folder+"graph.txt","r")
	st_file=open(folder+"st.txt","r")
	G = nx.Graph()
	adj_lst={}
	st_lst=[]
	weights={}
	for line in graph_file:
		line=line.strip()
		line=line.split()
		u=int(line[0])
		v=int(line[1])
		G.add_edge(u,v)
		weights[(u,v)] = float(line[2])
	for line in st_file:
		line=line.strip()
		line=line.split()
		st_lst.append((int(line[0]),int(line[1])))
	return (G,st_lst,weights)

#generate a random graph and st pairs
def generate_instance(n,m,stnum):
	G = nx.Graph()
	i=0
	while i<n:
		G.add_node(i)
		i+=1
	i=0
	edges={}
	weights={}
	while i<m:
		u=random.randint(0,n-1)
		v=random.randint(0,n-1)
		if (u,v) in edges or (v,u) in edges:
			continue
		if not u==v:
			weights[(u,v)] = random.randint(1,100)
			G.add_edge(u,v,weight=weights[(u,v)])
			edges[(u,v)]=1
		else:
			continue
			
		i+=1
	i=0
	st_lst=[]
	st_pairs={}
	while i<stnum:
		u=random.randint(0,n-1)
		v=random.randint(0,n-1)
		if (u,v) in st_pairs or (v,u) in st_pairs:
			continue
		if not u==v:
			st_lst.append((u,v))
			st_pairs[(u,v)]=1
		else:
			continue
		i+=1
	return (G,st_lst,weights)


#Check if the st pairs are connected in H
def connected_all(st_lst,H):
	#print H.edges()
	for (u,v) in st_lst:
		if local_edge_connectivity(H, u, v)>0:
			continue
		else:
			return False
	return True

#Identify the subset of components that have one of s or t
def get_subset(C_lst, st_lst):
	C_subset=[]
	comp=[]
	for C in C_lst:
		comp.append(C)
	for (s,t) in st_lst:
		for C in comp:
			#print C,"geetiing",s,t
			if s in C and not t in C:
				C_subset.append(C)
			elif t in C and not s in C:
				C_subset.append(C)
	return C_subset

import itertools

#Calculate the cost of the subgraph
def get_cost(ed_lst,weights):
	cost=0
	for (u,v) in ed_lst:
		if (u,v) in weights:
			cost+=weights[(u,v)]
		else:
			cost+=weights[(v,u)]

	return cost

#Brute force algorithm
def steiner_brute_force(G,st_lst,weights):
	
	ed_lst=G.edges()
	i=0
	mincost=10000000
	while i<len(G.edges()):
		lst=list(itertools.combinations(ed_lst,i))
		
		for sub_edges in lst:
			H=nx.Graph()
			for u in G.nodes():
				H.add_node(u)
			
			for ed in sub_edges:
				H.add_edge(ed[0],ed[1])
			if connected_all(st_lst,H):
				if get_cost(H.edges(),weights)<mincost:
					mincost=get_cost(H.edges(),weights)
					print "Brute force minimum till now",mincost
				#print "connected",H.edges(),get_cost(H.edges(),weights)
			#edges = H.edges()
  			#H.remove_edges_from(edges)
		i+=1
	return mincost#list(itertools.combinations(ed_lst,1))[0]


def steiner_primal_dual(G,st_lst,weights):
	y=0
	F=[]
	l=0
	H=nx.Graph()
	for u in G.nodes():
		H.add_node(u)

	#dictionary of values of y for each component
	# each component is converted to a string
	yC={}
	edgeconstraints=copy.deepcopy(weights)
	edge_order=[]
	while not connected_all(st_lst,H):
		l=l+1

		#Identify the connected components
		C_complete=nx.connected_components(H)
		#Get the components that have one of s and t
		C_subset=get_subset(C_complete,st_lst)

		#Identify the outgoing edges 
		edge_lst=[]	
		for C in C_subset:
			deltaC=nx.edge_boundary(G,C)
			edge_lst.extend(deltaC)

		#Identify the minimum threshold which changes any of these components
		minval=10000000
		for (u,v) in edge_lst:
			if (u,v) in edgeconstraints:
				if edgeconstraints[(u,v)]<minval:
					minval=edgeconstraints[(u,v)]
			elif (v,u) in edgeconstraints:
				if edgeconstraints[(v,u)]<minval:
					minval=edgeconstraints[(v,u)]

		#dictionary to keep track of edges for which the minval has been reduced
		modified={}

		for C in C_subset:
			Clst=list(C)
			Clst.sort()
			Ckey=""
			for elem in Clst:
				Ckey+=str(elem)+";"
			yval=0
			if Ckey in yC.keys():
				yval=yC[Ckey]
			#increased yval of the component
			yC[Ckey] = yval+minval

			#look at boundary edges of each component and look for all tight constraints
			for ed in nx.edge_boundary(G,C):
				if ed in modified:
					if modified[ed]==1:
						H.add_edge(ed[0],ed[1])
						if (ed[0],ed[1]) not in edge_order and (ed[1],ed[0]) not in edge_order:
							edge_order.append((ed[0],ed[1]))
					continue
				else:
					if ed in edgeconstraints:
						edgeconstraints[ed]=edgeconstraints[ed]-minval
						if edgeconstraints[ed]==0:
							modified[ed]=1
							modified[(ed[1],ed[0])]=1
							H.add_edge(ed[0],ed[1])
							edge_order.append((ed[0],ed[1]))
						else:
							modified[ed]=0
							modified[(ed[1],ed[0])]=0
					else:
						edgeconstraints[(ed[1],ed[0])]=edgeconstraints[(ed[1],ed[0])]-minval
						if edgeconstraints[(ed[1],ed[0])]==0:
							modified[ed]=1
							modified[(ed[1],ed[0])]=1
							H.add_edge(ed[0],ed[1])
							edge_order.append((ed[0],ed[1]))
						else:
							modified[ed]=0
							modified[(ed[1],ed[0])]=0
	iter=len(edge_order)-1
	while iter>=0:
		ed=edge_order[iter]

		H.remove_edge(ed[0],ed[1])
		if connected_all(st_lst,H):
			iter-=1
			continue
		H.add_edge(ed[0],ed[1])
		iter-=1

	return H

if sys.argv[1]=='1':
	(G,st_lst,weights)=	generate_instance(5,7,3)

	#(G,st_lst,weights)=	generate_instance(10,25,45)
	#(G,st_lst,weights)=	generate_instance(20,100,190)
	#(G,st_lst,weights)=	generate_instance(10,25,5)

else:
	(G,st_lst,weights)=	read_instance()
if not connected_all(st_lst,G):
	print "incorrect input"
	exit(-1)

H =steiner_primal_dual(G,st_lst,weights)

print "Primal-Dual solution"
print "Connected all st pairs?",connected_all(st_lst,H)
print "Primal-Dual cost:",get_cost(H.edges(),weights)


if len(st_lst)== (len(G.nodes())*(len(G.nodes())-1))/2:
	#find the Minimum spanning tree
	T=nx.minimum_spanning_tree(G)
	print "Minimum spanning tree is",get_cost(T.edges(),weights)


print "Trying to run the brute force algorithm"
brute_force=steiner_brute_force(G,st_lst,weights)
print "Brute force cost",brute_force
print "Approximation ratio", get_cost(H.edges(),weights)*1.0/brute_force