import re
import sys
from itertools import combinations

# 부분 집합 frequent 여부 확인
def checkSubsetIsFrequent(L, arr):

    for i in range(len(arr)):

        if i == 0:
            continue

        subsets = list(combinations(arr, i))
        for subset in subsets:

            s = list(subset)
            flag = False
            for l in L[len(s)-1]:
                if set(s).issubset(set(l)):
                    flag = True

            if flag is False:
                return False

    return True

# 리스트 내 조합 중 길이가 1만큼 더 긴 조합들을 찾아 반환
def combination(C, L, k):

    ret = []

    cnt = 0
    for fir in range(len(C)-1):
        cnt = cnt+1

        sec = fir + 1
        while True:

            if sec >= len(C):
                break

            uni = set(C[fir]) | set(C[sec])

            if len(uni) == k+1 and checkSubsetIsFrequent(L, list(uni)):
                ret.append(list(uni))

            sec = sec + 1

    return ret

input_min_sup = int(sys.argv[1])
input_name = sys.argv[2]
output_name = sys.argv[3]
min_sup = float(input_min_sup)

f = open(input_name, 'r')
DB = []

while True:

    line = f.readline()
    if not line:
        break

    numbers = re.findall(r'\d+', line)

    transaction = []
    for num in numbers:
        transaction.append(int(num))

    DB.append(transaction)

f.close()

C = []
L = []
cnt = []    # C[k] itemset count

# DB에서 1-itemset 추출
one_cnt = {}
one_itemsets = set()
for ts in DB:
    for num in ts:

        one_itemsets.add(num)

        if num in one_cnt:
            one_cnt[num] = one_cnt[num] + 1
        else:
            one_cnt[num] = 1

one_list_items = []
tmp = list(one_itemsets)
index = 0
for t in tmp:
    if (one_cnt[index] * 100 / len(DB)) >= min_sup:
        new_list = []
        new_list.append(t)
        one_list_items.append(new_list)
    index = index + 1

C.append(one_list_items)
L.append(one_list_items)

list_one_cnt = []
for num in one_list_items:
    list_one_cnt.append(one_cnt[num[0]])
cnt.append(list_one_cnt)

# L[k]에서 C[k+1] 생성
k = 0
while True:

    # 종료 조건
    if len(C[k]) == 0 or len(L[k]) == 0:
        break

    # C[k+1] 생성
    com = combination(C[k], L, k+1)
    C.append(com)

    # C[k+1]의 각 itemset의 support value 설정
    tmp_cnt = [0 for i in range(len(com))]
    index = 0
    for itemset in com:
        for tr in DB:
            if set(itemset).issubset(set(tr)):
                tmp_cnt[index] = tmp_cnt[index] + 1

        index = index + 1
    cnt.append(tmp_cnt)

    # frequent 여부 확인 후 L[k+1] 갱신
    tmp = []
    index = 0
    for sup in tmp_cnt:
        if (sup * 100 / len(DB)) >= min_sup:
            tmp.append(com[index])
        index = index + 1
    L.append(tmp)

    k = k + 1

# FP 중복 제거
arr = []
for i in range(len(L)):
    chk = {}
    tmp = []
    for j in range(len(L[i])):

        if j in chk:
            continue

        L[i][j].sort()
        tmp.append(L[i][j])

        for k in range(j+1, len(L[i])):
            if set(L[i][j]) == set(L[i][k]):
                chk[k] = True

    arr.append(tmp)

f = open(output_name, 'w')

for r in range(len(arr)):
    for c in range(len(arr[r])):
        for r2 in range(len(arr)):
            for c2 in range(len(arr[r2])):

                # 서로의 subset인 경우 제외
                if set(arr[r][c]).issubset(set(arr[r2][c2])) or set(arr[r2][c2]).issubset(set(arr[r][c])):
                    continue

                # support, confidence 값 얻기
                sup_cnt = 0
                conf_cnt = 0
                conf_all = 0

                union_set = set(arr[r][c]).union(set(arr[r2][c2]))

                for tr in DB:

                    tr_set = set(tr)
                    if union_set.issubset(tr_set):
                        sup_cnt = sup_cnt + 1
                        conf_cnt = conf_cnt + 1

                    if set(arr[r][c]).issubset(tr_set):
                        conf_all = conf_all + 1

                # association rule이 의미없는 경우 제외
                if conf_cnt == 0 or conf_all == 0:
                    continue

                # association rule : A->B
                A = '{'
                B = '{'

                index = 0
                for item in arr[r][c]:
                    if index < len(arr[r][c])-1:
                        A += str(item) + ','
                    else:
                        A += str(item)
                    index = index + 1
                A += '}'

                index = 0
                for item in arr[r2][c2]:
                    if index < len(arr[r2][c2])-1:
                        B += str(item) + ','
                    else:
                        B += str(item)
                    index = index + 1
                B += '}'

                sup = sup_cnt / len(DB) * 100
                conf = conf_cnt / conf_all * 100

                if sup < min_sup:
                    continue

                f.write(A + '\t' + B + '\t' + str(f"{sup:.2f}") + '\t' + str(f"{conf:.2f}") + '\n')

f.close()