**Primal-Dual Algorithm for generalized Steiner Tree problem:**

How to run: 

Option1: To randomly generate input use "python steiner.py 1"
	To change the values of m,n and the number of st pairs, please change line 229 where we call generate_instance(n,m,st_number). I have given 4-5 different options that I tested it on.

Option2: To read from input folder use "python steiner.py steiner_data/"


Input format (Only applicable for Option 2):
There should be two files in the data folder, (i) graph.txt which contains the different edges and their weights
					      (ii) st.txt which has st pairs with one pair in each line

If the number of st pairs is equal to {n\choose 2}, the result is same as the minimum spanning tree. We calculate that value for reference of approximation.

I have also implemented a brute force algorithm that is exponential. It runs for small graphs and for larger graphs it takes a lot of time. 

**Uncapacitated Facility Location Problem:**

How to run:

Option1: To randomly generate input use "python facility.py 1"
	The generate_instance function takes the number of facilities and clients as input

Option2: To read from input folder use "python facility.py facility_data/"

Input format (Only applicable for Option 2):
There should be two files in the data folder, (i) facility.txt which contains the cost of each facility
					      (ii) weight.txt which has the cost of assigning a client to a particular facility


To test the approximation ratio, we use the ILP that fives the exact solution. This code has been borrowed from Sudeep.
