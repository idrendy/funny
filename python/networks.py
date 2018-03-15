#networks.py
# -*- coding: utf-8 -*- 
import random
import sys  
#增加递归深度,与netSize一致就可以
sys.setrecursionlimit(50000)  

#cluster accumulation
global clusterAcc
clusterAcc=0
netSize=1000

def initNet(net,prob):
	#初始化dict
	isolatedNodes=[]
	for i in range(netSize):
		#print "init net node: ",i
		for j in range(i+1,netSize):
			#两点连接概率m% ==  1~netSize个数中随机抽取一个数小于 netSize * m%的概率
			if random.randint(1,netSize) < prob:
				#保存连接关系
				va1=net.get(i,set([]))
				va1.add(j)
				net[i]=va1
				va2=net.get(j,set([]))
				va2.add(i)
				net[j]=va2
		#如果i经过遍历之后仍未在网络中，则是孤立节点
		if len(net.get(i,set([])))==0:
			isolatedNodes.append(i)

	print "网络第一次构建完后，孤立节点数：",len(isolatedNodes)
	for i in isolatedNodes:
		#随机连边
		j=random.randint(0,netSize-1)
		while(j==i):
			j=random.randint(0,netSize-1)
		#保存连接关系
		va1=net.get(i,set([]))
		va1.add(j)
		net[i]=va1
		va2=net.get(j,set([]))
		va2.add(i)
		net[j]=va2

def initCluster(net,clusters):
	global clusterAcc
	clusterAcc=0
	for i in range(netSize):
		clusters[i]=0
	for i in range(netSize):
		repartitionCluster(i,net,clusters)


def repartitionCluster(node,net,clusters):
	global clusterAcc
	if node in net:
		#如果此节点未归过cluster,则说明此节点以及它的相邻节点都与之前的节点都无交集，新建cluster
		if clusters[node]==0:
			clusterAcc+=1
			clusters[node]=clusterAcc
			#相邻节点也是同样的cluster
		for n in net.get(node,set([])):
			if clusters[n]==0:
				clusters[n]=clusterAcc
				#深度遍历
				repartitionCluster(n,net,clusters)

def remainGiantCluster(clusters,net):
	#最大cluster标号及规模
	cs={}
	for c in clusters:
		size=cs.get(c,0)
		cs[c]=size+1
	maxc=0
	maxs=0
	for (c,size) in cs.items():
		if size>maxs:
			maxc=c
			maxs=size

	print "max clusters:",maxc,maxs

	#remove网络中不在max cluster的连边
	for n in range(netSize):
		if clusters[n]<>maxc:
			clusters[n]=0
			if n in net:
				net.pop(n)


def attckNet(node,net):
	if node in net:
		#删除别人与node的连边
		for n in net.get(node):
			#print "remove link:",node,n
			net.get(n,set([])).remove(node)
			if len(net.get(n))==0:
				net.pop(n)
		#在网络中删除node
		net.pop(node)

def effectNet(targetNet,targetCluster,effectCluster):
	#遍历目标网络中的所有连边
	for (k,v) in targetNet.items():
		removeLink=set([])
		for n in v:
			#连边在effectCluster中在同一个cluster则跳过，不在则断开，并处理断开的连锁反应
			if effectCluster[n]==0 or effectCluster[k]==0 or effectCluster[n]!=effectCluster[k]:
				#print "break link:",k,n
				targetNet.get(n,set([])).remove(k)
				removeLink.add(n)
		for r in removeLink:
			targetNet.get(k).remove(r)

	print "net pre num:",len(targetNet)
	#去除网络中没有连边的点
	for k in targetNet.keys():
		if len(targetNet.get(k))==0:
			targetNet.pop(k)
	print "net aft num:",len(targetNet),"\n"

	#更新cluster,TODO: 这是偷懒写法，是可优化点，将这个操作放在断边时做
	initCluster(targetNet,targetCluster)

	remainGiantCluster(targetCluster,targetNet)	

def networkAction(prob,attckNum,effectNum):
	#定义网络AB
	#array: index{node}=>value{cluster}; index begin with zero,0是网络中的一号节点
	clusterAs =[]
	clusterBs =[]
	#dict: key{node}=>value{set(links)
	netA ={}
	netB ={}
	"""
	初始网络
	"""
	#初始化array;range begin with zero
	for i in range(netSize):
		clusterAs.append(clusterAcc)
		clusterBs.append(clusterAcc)
	#初始化dict
	initNet(netA,prob)
	initNet(netB,prob)

	#将字典节果打印到txt中,TODO： 此步为debug
	# dicfile=open('./netA.txt','w')
	# dicfile.write(str(netA))
	# dicfile.close()
	# dicfile=open('./netB.txt','w')
	# dicfile.write(str(netB))
	# dicfile.close()

	"""
	攻击开始
	随机破坏A和B网络中的attcknum个节点
	"""
	attcked=set([])
	for i in range(attckNum):
		attckNode = random.randint(0,netSize-1)
		while(attckNode in attcked):	
			attckNode = random.randint(0,netSize-1)
		attcked.add(attckNode)
		print "attck node:",attckNode
		#destroy netA node & link
		attckNet(attckNode,netA)
		#destroy netB node & link
		attckNet(attckNode,netB)

	"""
	遍历网络，统计各节点的cluster归属情况
	最终生成cluster名不是顺序的，但不影响后续计算
	"""
	#A
	initCluster(netA,clusterAs)
	remainGiantCluster(clusterAs,netA)
	#B
	initCluster(netB,clusterBs)
	remainGiantCluster(clusterBs,netB)

	# print "cluster acc:",clusterAcc
	# print "cluster A:",clusterAs
	# print "cluster B:",clusterBs

	"""
	A、B网络互相影响
	"""
	for i in range(effectNum):
		print ">>>>effect count: ",i+1
		#A影响B
		effectNet(netB,clusterBs,clusterAs)
		#B影响A
		effectNet(netA,clusterAs,clusterBs)
	
	# print "cluster A:",clusterAs
	# print "cluster B:",clusterBs
	# print "netA:",netA
	# print "netB:",netB

	#将字典节果打印到txt中,TODO： 此步为debug
	# dicfile=open('./netA2.txt','w')
	# dicfile.write(str(netA))
	# dicfile.close()
	# dicfile=open('./netB2.txt','w')
	# dicfile.write(str(netB))
	# dicfile.close()

	# 如果cluster中不全是孤立节点，则结果为1；反之则为0
	if len(netA) ==0:
		return 0
	else:
		return 1
#程序入口
if __name__ == '__main__':
	print "Catastrophic cascade of failures in interdependent networks\n\n"
	#link probability 0.4%：连接概率
	prob= 4
	#effect num:相互影响次数
	effectNum=10

	results=[]
	for i in range(1,10):
		#attack num：攻击次数
		attckNum=i*100
		count=0
		#跑10次
		for i in range(10):
			print "---------------------------",attckNum,i,"--------------------"
			count+=networkAction(prob,attckNum,effectNum)
		#除以跑的次数，这里
		results.append(count/10.0)


	dicfile=open('./result.txt','w')
	for  i,val in enumerate(results):
		print("攻击次数：%s   结果1平均占比：%s  prob*(netSize-attcknum)/netSie: %s" % ((i+1)*100, val,prob*(netSize-(i+1)*100)*1.0/netSize))
		dicfile.write("%s %s %s" % ((i+1)*100, val,prob*(netSize-(i+1)*100)*1.0/netSize))
	dicfile.close()








