network = { 'A' : [],
			'B' : [],
			'C' : [],
			'D' : ['A','B','C'],
			'E' : ['D'],
			'F' : ['D']}
		 
valTable = {'A':0.1,
			'B':0.2,
			'C':0.3,
			'D | A B C':0.4,
			'D | A B -C':0.5,
			'D | A -B C':0.6,
			'D | A -B -C':0.7,
			'D | -A B C':0.8,
			'D | -A B -C':0.9,
			'D | -A -B C':0.1,
			'D | -A -B -C':0.2,
			'E | D':0.3,
			'E | -D':0.4,
			'F | D':0.5,
			'F | -D':0.6}	
		 
precedence = ['A','B','C','D','E','F']
L=[]
strng = '\n\n The probability is: '
#Tree Class Definition
class Tree:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left  = left
        self.right = right

    def __str__(self):
        return str(self.data)

#Pushes any negation (compliment) down in the tree until they reside above atoms
def pushNegs(mytree):
	if mytree == None:
		return
	elif mytree.data.isalpha():
		return mytree
	elif mytree.data == '+':
		return(Tree('+', pushNegs(mytree.left), pushNegs(mytree.right)))
	elif mytree.data == '*':
		return(Tree('*', pushNegs(mytree.left), pushNegs(mytree.right)))
	elif mytree.data == '-':
		if mytree.left.data == '*':
			return(Tree('+',pushNegs(Tree('-',mytree.left.left,None)),pushNegs(Tree('-',mytree.left.right,None))))
		elif mytree.left.data == '+':
			return(Tree('*',pushNegs(Tree('-',mytree.left.left,None)),pushNegs(Tree('-',mytree.left.right,None))))
		elif mytree.left.data == '-':
			return(pushNegs(mytree.left.left))			
		elif mytree.left.data.isalpha():
			return(Tree(mytree.data,mytree.left))
		else:
			print 'We could not handle an occurrence of \'-\'! '
	else:
		print 'We could not determine what tree.data was!'
		
#Re-orders our operations of union and intersection to provide us a union of intersections with no inversions
def pushOps(myTree):
	if myTree == None:
		return
	elif myTree.data.isalpha():
		return(myTree)
	elif myTree.data == '-':
		return(myTree)
	elif myTree.data == '+':
		return(Tree('+',pushOps(myTree.left),pushOps(myTree.right)))
	elif myTree.data == '*':
		if myTree.left.data == '+':
			return(Tree('+',pushOps(Tree('*',myTree.left.left,myTree.right)),pushOps(Tree('*',myTree.left.right,myTree.right))))
		elif myTree.right.data == '+':
			return(Tree('+',pushOps(Tree('*',myTree.left,myTree.right.left)),pushOps(Tree('*',myTree.left,myTree.right.right))))
		elif myTree.left.data != '+' and myTree.right.data != '+':
			return(Tree('*',pushOps(myTree.left),pushOps(myTree.right)))
		else:
			print 'We could not handle an occurrence of \'*\' followed by \'+\'!'
	else:
		print 'We could not determine what tree.data was!'

#Divides the tree into disjuncts, (lists of intersections)		
def getDisjuncts(tree):
	if tree.data != '+':
			L.append(tree)
	else:
		getDisjuncts(tree.left)
		getDisjuncts(tree.right)
	return(L)

#Accepts a list of disjuncts, removes all duplicate atoms
def getLits(list):
	j = []
	for i in list:
		k = []
		j.append(grabLits(i,k))
	j=removeDupes(j)	
	return(j)

#Helps getLits by operating specifically on literals
def grabLits(tree,list):
	if tree.data == '*':
		grabLits(tree.left,list)
		grabLits(tree.right,list)
	elif tree.data == '-':
		list.append(tree.data+tree.left.data)
	elif tree.data.isalpha():
		list.append(tree.data)
	return(list)	

#Non-order preserving duplicate removal
def removeDupes(myList):
	j = []
	for i in myList:
		i = list(set(i))
		j.append(i)
	return(j)
	
#Traverses a tree in order and prints it for a visual represenatioin
def traverse(rootTree):
  thislevel = [rootTree]
  while thislevel:
    nextlevel = list()
    for n in thislevel:
      print n.data,
      if n.left: nextlevel.append(n.left)
      if n.right: nextlevel.append(n.right)
    print
    thislevel = nextlevel
	
#Similarly to traverse, walks two trees in order to determine their equality
def treeEquality(myTree,myTree2):
	thislevel = [myTree]
	thatlevel = [myTree2]
	if len(thislevel) != len(thatlevel):
		return False
	while thislevel:
		nextlevel = list()
		nextlevel2 = list()
		for n,l in zip(thislevel,thatlevel):
			if n.data!=l.data:
				return False
			if n.left: nextlevel.append(n.left)
			if l.left: nextlevel2.append(l.left)
			if n.right: nextlevel.append(n.right)
			if l.right: nextlevel2.append(l.right)
		thislevel = nextlevel
		thatlevel = nextlevel2
	return True
		
#Continuously run pushOps on the provided tree until the input to pushOps matches the output,
#this will signify no inversions remain in the tree.
def fixPoint(myTree):
	myTree2 = pushOps(myTree)
	while True:
		if treeEquality(myTree,myTree2) == True: break
		myTree = myTree2
		myTree2 = pushOps(myTree)
	
	return(myTree)

#Removes any inconsistent disjuncts from our list of disjuncts such as ['A,-A,B']
def removeInconsistancy(myList):
	removalList = []
	for sublist in myList:
		for element in sublist:
			ind = sublist.index(element) 
			if len(element) > 1 and element[0] == '-':			
				temp = element
				sublist.pop(ind)
				sublist.insert(ind,element[1:])
				if len(sublist) != len(set(sublist)):
					sublist.pop(ind)
					sublist.insert(ind,temp)
					#print sublist
					removalList.append(sublist)
				else:
					sublist.pop(ind)
					sublist.insert(ind,temp)

	for i in removalList:
		if i in myList:
			myList.pop(myList.index(i))
	return(myList)
		
#Closes our lists of intersections under Ancestry				
def closure(myList):
	temp =[]
	missed = []
	closed = []
	for i in myList:
		i_abs = absolute(i)
		missing = list(set(precedence)-set(i_abs))
		missing.sort(key=lambda x: precedence.index(x))
		missed.append( expand(missing))
	for i,j in zip(myList,missed):
		for k in j:
			update = i+k
			closed.append(getPrecedence(update))

	return closed

#Compliment helper for closing under ancestry
def absolute(myList):
	temp = []
	for i in myList:
		if i[0] == '-':
			temp.append(i[1])
		else:
			temp.append(i)	
	return(temp)

#Takes missing ancestors as an argument and uses it's length to get the appropriate binary string size.	
def expand(m):
	size = binaryString(len(m))
	return (replace(size,m))
 
#Builds binary string for handling compliment
def binaryString(n):
	if n < 1:
		return [[]]
	subtable = binaryString(n-1)
	return [row + [v] for row in subtable for v in [1,0]]

#Takes binary string, and missing ancestors as args to build the list
def replace(n,missing):
	for i in n:
		for j in range(0,len(i)):
			if i[j] == 1:
				i[j] = missing[j]
			else:
				x = '-'+missing[j] 
				i[j] = x
	return n	
	
#Ordering helper for ordering with compliments
def getPrecedence(myList):
	temp = []
	for i in range(len(precedence)):
		compliment = '-'+precedence[i]
		temp.append(precedence[i])
		temp.append(compliment)	
	myList.sort(key=lambda x: temp.index(x))
	return(myList)
	
#Removes and duplicate disjuncts, order preserving
def removeDuplicates(myList):

	myList_set = set(tuple(x) for x in myList)
	newList = [ list(x) for x in myList_set ]
	newList.sort(key = lambda x: myList.index(x) )
	return(newList)
	
#Applies the chain rule to our disjuncts
def chainRule(dj_list):
	temp = []
	temp2 = []
	for sublist in dj_list:
		for literal in sublist:
			parents = parent_lookup(literal)
			if len(parents) == 0:
				temp.append(literal)
			else:
				index = sublist.index(literal)
				count = 0
				expr = str(literal) + ' |'
				while count < index:
					if len(sublist[count]) > 1:
						if sublist[count][1] in parents:
							expr += ' '+str(sublist[count])
						else:
							pass
					else:
						if sublist[count] in parents:
							expr += ' '+str(sublist[count])
						else:
							pass
					count += 1
				temp.append(expr)
				
		temp2.append(temp)
		temp = []
	return temp2

#Looks up and returns the parents of a literal from a Bayesian Network	
def parent_lookup(literal):
	if len(literal) > 1:
		temp = literal[1]
	else:
		temp = literal[0]
	return network.get(temp)
		
#Looks up and returns the values from a table in a Bayesian Network
def tabLookup(myList):
	valList = []
	retList = []
	for sublist in myList:
		for element in sublist:
			if len(element) > 1 and element[0] == '-':	
				valList.append(1-valTable.get(element[1:]))
			else:
				valList.append(valTable.get(element))
		retList.append(valList)
		valList = []
	return retList

#Calculates the probabilty of our query
def calcProb(myList):
	prodList = []
	for sublist in myList:
		prodList.append(reduce(lambda x, y: x*y, sublist))
	probability = reduce(lambda x, y: x+y, prodList)
	return probability
	
#Calculates the probabilyt of our query if it contains conditional probability	
def condProb(top,bot):
	probability = top / bot
	return(probability)

#Execution of all of our functions	
def execute(arg):
	# traverse(arg)
	test1 = pushNegs(arg)	
	test3 = fixPoint(test1)
	test4 = getDisjuncts(test3)
	test5 = getLits(test4)	
	# print '\n\n'+str(test5)
	test6 = removeInconsistancy(test5)
	# print str(test6)
	test7 = closure(test6)
	# print str(test7)
	test8 = removeDuplicates(test7)
	# print str(test8)
	test9 = chainRule(test8)
	# print str(test9)
	test10 = tabLookup(test9)
	# print str(test10)
	test11 = calcProb(test10)
	# print str(test11)
	
	return test11
		
#TREE DEFINITION

#P(D)
#Root = Tree('D', None, None)
#top = execute(Root)
#bot = 1

#P(A+C)
#A = Tree('A',None,None)
#C = Tree('C',None,None)
#Root = Tree('+', A,C)
#top = execute(Root)
#bot = 1

#P(A*-C|B+A)
# A = Tree('A',None,None)
# B = Tree('B',None,None)
# C = Tree('C',None,None)
# Comp_C = Tree('-',C,None)
# L_sub = Tree('*',A,Comp_C)
# R_sub = Tree('+',B,A)
# Root = Tree('*',L_sub, R_sub)
# top = execute(Root)
# bot = execute(R_sub)
# print strng+str(condProb(top,bot))

#P(A*D|E*F)
# A = Tree('A',None,None)
# D = Tree('D',None,None)
# E = Tree('E',None,None)
# F = Tree('F',None,None)
# L_sub = Tree('*',A,D)
# R_sub = Tree('*',E,F)
# Root = Tree('*',L_sub, R_sub)
# top = execute(Root)
# bot = execute(R_sub)
# print strng+str(condProb(top,bot))

#P(A+B*C+~(D*E)|(C+D)*E+~B)
A = Tree('A',None,None)
B = Tree('B',None,None)
C = Tree('C',None,None)
D = Tree('D',None,None)
E = Tree('E',None,None)
H = Tree('*',B,C)
I = Tree('*',D,E)
J = Tree('+',A,H)
K = Tree('-',I,None)
L_sub = Tree('+',J,K)
M = Tree('+',C,D)
N = Tree('-',B,None)
O = Tree('*',M,E)
R_sub = Tree('+',O,N)
Root = Tree('*',L_sub,R_sub)
top = execute(Root)
bot = execute(R_sub)
print strng+str(condProb(top,bot))+'\n\n'