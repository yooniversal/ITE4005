import sys
sys.setrecursionlimit(30000)


class Obj:
    id = 0
    x = 0.1
    y = 0.1
    processed = False
    adj = []

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.adj = []

    def isCore(self):
        return len(self.adj) >= MinPts-1


def isAdj(p, q):
    if ((p.x - q.x) * (p.x - q.x) + (p.y - q.y) * (p.y - q.y)) <= Eps*Eps:
        return True
    return False


def getDensityReachable(center, cluster):
    for adjacent in center.adj:
        if adjacent.processed == False:
            adjacent.processed = True
            cluster.append(adjacent)

            if adjacent.isCore():
                getDensityReachable(adjacent, cluster)


# input : One command line
input_name = sys.argv[1]
n = int(sys.argv[2])
Eps = float(sys.argv[3])
MinPts = int(sys.argv[4])

allObj = []

f = open(input_name, 'r')

# input data 파싱해 allObj 업데이트
while True:

    line = f.readline()
    if not line:
        break

    id, x, y = line.split()
    id = int(id)
    x = float(x)
    y = float(y)

    allObj.append(Obj(id, x, y))

f.close()

# 각 object 이웃 전처리
for p in allObj:
    for q in allObj:
        if p == q:
            continue

        if isAdj(p, q):
            p.adj.append(q)

clusters = []

# DBSCAN
for p in allObj:
    if p.processed == False and p.isCore():
        newCluster = []
        p.processed = True

        getDensityReachable(p, newCluster)
        clusters.append(newCluster)

# 만든 cluster 수 m이 n보다 큰 경우 작은 cluster (m-n)개 제거
if len(clusters) > n:
    clusters.sort(key=lambda c: len(c), reverse=True)

    while len(clusters) > n:
        clusters.pop()

for i in range(n):
    output_name = 'input' + input_name[5] + '_cluster_' + str(i) + '.txt'

    f = open(output_name, 'w')

    for o in clusters[i]:
        f.write(str(o.id) + '\n')

    f.close()