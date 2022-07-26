import sys
import math


# Decision Tree를 구성하는 Node
class Node:
    def __init__(self, feat):
        self.feat = feat
        self.next = []
        self.result = 'invalid'

    def append(self, newNode):
        self.next.append(newNode)

    def setFeat(self, feat):
        self.feat = feat

    def setResult(self, result):
        self.result = result

    def getFeat(self):
        return self.feat

    def getNext(self, index):
        return self.next[index]

    def getResult(self):
        return self.result


def Info(values):
    sum = 0
    ret = 0.0

    for v in values:
        sum = sum + v

    for x in values:
        if x == 0 or sum == 0:
            continue

        p = x / sum
        ret = ret - p * math.log2(p)

    return ret

# n번째 attribute에 속한 각 domain의 count List
def DomainCnt(DB, kind, n):
    ret = [0 for i in range(len(kind[n]))]
    domain_idx = {}

    i = 0
    for k in kind[n]:
        domain_idx[k] = i
        i = i + 1

    # 각 tuple에서 n-attr에 해당되는 값의 count 체크
    for tuple in DB:
        ret[domain_idx[tuple[n]]] = ret[domain_idx[tuple[n]]] + 1

    return ret


def setCriteria(DB, attr, attr_chk, kind):
    ret = Node(-1)

    # Info(D)
    ret_cnt = DomainCnt(DB, kind, -1)
    all_info = Info(ret_cnt)

    # 종료 조건 : entropy = 0
    if all_info == 0:
        ret.setResult(DB[0][-1])
        return ret

    # Info(D_a), Gain(D_a) 구하기
    gain_list = []
    for a in range(len(attr) - 1):

        # 이미 체크된 attribute pass
        if attr_chk[a] == True:
            gain_list.append(-123456789)
            continue

        # attribute a의 값 k를 갖는 tuple 개수 카운트 및 Information Gain 구하기
        info_a = 0.0
        for k in kind[a]:

            idx = 0
            ret_domain = {}                               # 결과값을 인덱스로 변환하는 dict
            cond_cnt = [0 for i in range(len(kind[-1]))]  # k가 속한 tuple의 각 결과값 카운트

            for tuple in DB:
                if tuple[a] != k:
                    continue

                if tuple[-1] not in ret_domain:
                    ret_domain[tuple[-1]] = idx
                    cond_cnt[idx] = cond_cnt[idx] + 1
                    idx = idx + 1
                else:
                    cond_cnt[ret_domain[tuple[-1]]] = cond_cnt[ret_domain[tuple[-1]]] + 1

            info_a_k = Info(cond_cnt)                             # attribute a의 k category info
            info_a = info_a + sum(cond_cnt) / len(DB) * info_a_k  # attribute a의 info

        gain_a = all_info - info_a  # attribute a의 Information Gain
        gain_list.append(gain_a)

    # 최대 Information Gain을 갖는 attribute를 feature로 설정
    max_gain_idx = gain_list.index(max(gain_list))
    ret.setFeat(max_gain_idx)

    # 하위 Node 생성
    dc = DomainCnt(DB, kind, -1)            # 결과값 등장 list
    max_dc_idx = dc.index(max(dc))          # 가장 많이 등장하는 label index
    max_label = list(kind[-1])[max_dc_idx]  # 가장 많이 등장하는 label

    for k, i in zip(kind[max_gain_idx], range(len(kind[max_gain_idx]))):

        # 하위 Node에 쓰일 DB 생성
        newDB = []
        for tuple in DB:
            if tuple[max_gain_idx] == k:
                newDB.append(tuple)

        # 하위 case 없으므로 가장 많이 등장하는 label 설정
        if len(newDB) == 0:
            newNode = Node(-1)
            newNode.setResult(max_label)
            ret.append(newNode)
            continue

        # 하위 Decision Tree에 쓰일 attribute check 생성
        new_attr_chk = attr_chk.copy()
        new_attr_chk[max_gain_idx] = True

        subNode = setCriteria(newDB, attr, new_attr_chk, kind)
        ret.append(subNode)

    return ret


# Decision Tree 통해 각 tuple 결과 구하기
def SearchResult(node, kind, tuple):
    # 종료 조건 : leaf node
    if node.feat == -1:
        return node.getResult()

    # 조건에 맞춰 탐색하면서 최종 결과 얻기
    for k, i in zip(kind[node.getFeat()], range(len(kind[node.getFeat()]))):

        if k == tuple[node.getFeat()]:
            ret = SearchResult(node.getNext(i), kind, tuple)
            return ret

    return 'invalid'

# input : One command line
input_train = sys.argv[1]
input_test = sys.argv[2]
output_name = sys.argv[3]

f = open(input_train, 'r')
attr = f.readline().split()  # attribute
attr_chk = [False for i in range(len(attr))]  # 사용된 attribute 체크
DB = []  # input의 tuples
kind = []  # 각 attribute

# input data 파싱해 DB, kind 업데이트
while True:

    line = f.readline()
    if not line:
        break

    category_list = line.split()
    category_idx = {}
    category_cnt = 0

    for i, category in zip(range(len(category_list)), category_list):
        if len(kind) != len(attr):
            category_set = set()
            category_set.add(category)
            kind.append(category_set)
        else:
            kind[i].add(category)

    DB.append(category_list)

f.close()

# decision tree 설정
dt_root = setCriteria(DB, attr, attr_chk, kind)

# 위에서 얻은 decision tree로 test
f = open(input_test, 'r')
test_attr = f.readline().split()  # attribute
TDB = []  # test DB
test_result = []  # 각 tuple output

# test 파일을 파싱해 TDB 업데이트
while True:

    line = f.readline()
    if not line:
        break

    TDB.append(line.split())

f.close()

# 위에서 구한 Decision Tree 통해 결과 얻기
for tuple in TDB:
    test_result.append(SearchResult(dt_root, kind, tuple))

# 얻은 결과 작성
f = open(output_name, 'w')

# attributes 작성
attrs = ''
for a, i in zip(attr, range(len(attr))):
    if i == (len(attr) - 1):
        attrs = attrs + a
    else:
        attrs = attrs + a + '\t'
f.write(attrs + '\n')

# tuple 및 test 결과 작성
for tuple, i in zip(TDB, range(len(TDB))):

    tuple_line = ''

    for v, j in zip(tuple, range(len(tuple))):
        if j == (len(tuple) - 1):
            tuple_line = tuple_line + v + '\t' + test_result[i]
        else:
            tuple_line = tuple_line + v + '\t'

    f.write(tuple_line + '\n')

f.close()
