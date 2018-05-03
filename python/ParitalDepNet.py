#networks.py
# -*- coding: utf-8 -*- 
import random
import sys  
import numpy
from random import choice
#增加递归深度,与netSize一致就可以
sys.setrecursionlimit(50000)  

#cluster accumulation
global clusterAcc
clusterAcc=0
netSize=1000

def initNet(net,prob):
	#初始化dict
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

def extractLinksByCluster(node,net,links):
	for n in net.get(node,set([])):
		#防止重复加边
		if ((n,node) not in links) and ((node,n) not in links):
			links.add((node,n))
			extractLinksByCluster(n,net,links)

def getClusterSize(ci,cluster):
	length=0
	for v in cluster:
		if v==ci:
			length+=1
	return length

def effectNet(targetNet,targetCluster,effectCluster1,effectCluster2,depColl):
	if len(targetNet) == 0 :
		print "net no cluster anymore"
		return 0
	# 方式一：随机从net从选取一个节点（网络中的节点都有cluster）
	# node = choice(targetNet.keys())

	# 方式二：随机从net从选取一个节点,此节点有可能是孤立节点
	node =random.randint(0,netSize-1)
	print ("select node: %s ; cluster: %s" % (node,targetCluster[node]))
	if targetCluster[node]==0:
		return 0

	links =set(())
	extractLinksByCluster(node,targetNet,links)
	for i,link in enumerate(links):
		#连边2点至少有一个点在depColl中时：当该边在effectNet中是连边则跳过，不是连边则断开；否则跳过
		if ((link[0] in depColl) or (link[1] in depColl)) and ( \
		effectCluster1[link[0]]==0 or effectCluster1[link[1]]==0 or effectCluster1[link[0]!=effectCluster1[link[1]]] \
		or \
		effectCluster2[link[0]]==0 or effectCluster2[link[1]]==0 or effectCluster2[link[0]!=effectCluster2[link[1]]]):
			print "link:",link
			targetNet.get(link[0]).remove(link[1])
			targetNet.get(link[1]).remove(link[0])

	#去除网络中没有连边的点
	for k in targetNet.keys():
		if len(targetNet.get(k))==0:
			targetNet.pop(k)

	#更新cluster,TODO: 这是偷懒写法，是可优化点，将这个操作放在断边时做
	initCluster(targetNet,targetCluster)

	if node in targetNet:
		ci=targetCluster[node]
		return getClusterSize(ci,targetCluster)
	else :
		return 0

def networkAction(prob,effectCount,depNum):
	#定义网络ABC
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

	"""
	遍历网络，统计各节点的cluster归属情况
	最终生成cluster名不是顺序的，但不影响后续计算
	"""
	#A
	initCluster(netA,clusterAs)
	#B
	initCluster(netB,clusterBs)
	#C
	initCluster(netC,clusterCs)

	"""
	随机得到${depNum}个不重复依赖节点
	"""
	depColl=set()
	while(len(depColl)<depNum):
		depColl.add(random.randint(0,netSize-1))
	print "dep coll: ",depColl,"\n"

	"""
	A、B、C网络互相影响
	loop{
		netb & netc effect neta
		neta $ netc effect netb
		neta $ netb effect netc
	}
	"""
	finalNumOfClusterA=0
	finalNumOfClusterB=0
	finalNumOfClusterC=0
	for i in range(effectCount):
		print ">>>>effect count: ",i+1
		#B,C影响A
		finalNumOfClusterA= effectNet(netA,clusterAs,clusterBs,clusterCs,depColl)
		#A,C影响B
		finalNumOfClusterB= effectNet(netB,clusterBs,clusterAs,clusterCs,depColl)
		#A,B影响C
		finalNumOfClusterC= effectNet(netC,clusterCs,clusterAs,clusterBs,depColl)
		print "length:",finalNumOfClusterA,finalNumOfClusterB,finalNumOfClusterC
	
	return finalNumOfClusterA

#程序入口
if __name__ == '__main__':
	print "partial dependent network for 栋子小宝"
	#link probability 0.4%：连接概率
	#effect num:相互影响次数
	effectNum=10
	step =0.5
	#依赖比例
	q=0.1

	counterAs=[]
	for p in numpy.arange(0,6,step):
		counterA=0
		for i in range(1,10):
			print "---------------------------",p,i,"--------------------"
			counterA+=networkAction(p,effectNum,q*netSize)
		counterAs.append(counterA/10.0)

	for i,v in enumerate(counterAs):
		print ("p: %s; counterA: %s;" % (i*step,v))

	# print "neta results:"
	# dicfile=open('./netaResult.txt','w')
	# for  i,vals in enumerate(results.get("neta")):
	# 	print("攻击次数：%s   结果1平均占比：%s  prob*(netSize-attcknum)/netSie: %s  avgMaxCluster: %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
	# 	dicfile.write("%s %s %s %s" % ((i+1)*100, vals[0],prob*(netSize-(i+1)*100)*1.0/netSize,vals[1]))
	# dicfile.close()
