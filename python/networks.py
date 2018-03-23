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
	return maxs


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

	return remainGiantCluster(targetCluster,targetNet)	


def effectNetByTwoNet(targetNet,targetCluster,effectCluster1,effectCluster2):
	#遍历目标网络中的所有连边
	for (k,v) in targetNet.items():
		removeLink=set([])
		for n in v:
			#连边在net1或net2中同一个cluster则跳过，不在则断开，并处理断开的连锁反应
			if (effectCluster1[n]==effectCluster1[k] and effectCluster1[n] != 0) or (effectCluster2[n]==effectCluster2[k] and effectCluster2[n] != 0):
				#skip
				print ""
			else:
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

	return remainGiantCluster(targetCluster,targetNet)	

def networkAction(prob,attckNum,effectNum):
	#定义网络AB
	#array: index{node}=>value{cluster}; index begin with zero,0是网络中的一号节点
	clusterAs =[]
	clusterBs =[]
	clusterCs =[]
	#dict: key{node}=>value{set(links)
	netA ={}
	netB ={}
	netC ={}
	"""
	初始网络
	"""
	#初始化array;range begin with zero
	for i in range(netSize):
		clusterAs.append(clusterAcc)
		clusterBs.append(clusterAcc)
		clusterCs.append(clusterAcc)
	#初始化dict
	initNet(netA,prob)
	initNet(netB,prob)
	initNet(netC,prob)

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
		#destroy netC node & link
		attckNet(attckNode,netC)

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
	#C
	initCluster(netC,clusterCs)
	remainGiantCluster(clusterCs,netC)


	# print "cluster acc:",clusterAcc
	# print "cluster A:",clusterAs
	# print "cluster B:",clusterBs

	"""
	A、B、C网络互相影响
	loop{
		neta effect netb
		neta effect netc
		netc & netb effect neta
	}
	"""
	finalMaxClusterA=0
	finalMaxClusterB=0
	finalMaxClusterC=0
	for i in range(effectNum):
		print ">>>>effect count: ",i+1
		#A影响B
		finalMaxClusterB= effectNet(netB,clusterBs,clusterAs)
		#A影响C
		finalMaxClusterC= effectNet(netC,clusterCs,clusterAs)

		#B&C 影响A
		finalMaxClusterA= effectNetByTwoNet(netA,clusterAs,clusterBs,clusterCs)
	
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
	# index 0: neta; index1: netb; index2: netc
	results =([0,finalMaxClusterA],[0,finalMaxClusterB],[0,finalMaxClusterC])
	if len(netA) !=0:
		results[0][0]=1
	if len(netB) !=0:
		results[1][0]=1
	if len(netC) !=0:
		results[2][0]=1
	return results
#程序入口
if __name__ == '__main__':
	print "Catastrophic cascade of failures in interdependent networks\n\n"
	#link probability 0.4%：连接概率
	prob= 4
	#effect num:相互影响次数
	effectNum=10

	results={}
	results["neta"]=[]
	results["netb"]=[]
	results["netc"]=[]

	for i in range(1,10):
		#attack num：攻击次数
		attckNum=i*100
		#neta ,netb,netc
		counter=[0,0,0]
		cluster=[0,0,0]
		#跑10次
		for i in range(10):
			print "---------------------------",attckNum,i,"--------------------"
			for i,countAndCluster in enumerate(networkAction(prob,attckNum,effectNum)):
				counter[i]=counter[i]+countAndCluster[0]
				cluster[i]=cluster[i]+countAndCluster[1]
		#除以跑的次数，这里
		results.get("neta").append((counter[0]/10.0,cluster[0]/10.0))
		results.get("netb").append((counter[1]/10.0,cluster[1]/10.0))
		results.get("netc").append((counter[2]/10.0,cluster[2]/10.0))


	print "neta results:"
	dicfile=open('./netaResult.txt','w')
	for  i,vals in enumerate(results.get("neta")):
		print("攻击次数：%s   结果1平均占比：%s  prob*(netSize-attcknum)/netSie: %s  avgMaxCluster: %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
		dicfile.write("%s %s %s %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
	dicfile.close()
	print "netb results:"
	dicfile=open('./netbResult.txt','w')
	for  i,val in enumerate(results.get("netb")):
		print("攻击次数：%s   结果1平均占比：%s  prob*(netSize-attcknum)/netSie: %s  avgMaxCluster: %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
		dicfile.write("%s %s %s %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
	dicfile.close()
	print "netc results:"
	dicfile=open('./netcResult.txt','w')
	for  i,val in enumerate(results.get("netc")):
		print("攻击次数：%s   结果1平均占比：%s  prob*(netSize-attcknum)/netSie: %s  avgMaxCluster: %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
		dicfile.write("%s %s %s %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
	dicfile.close()








