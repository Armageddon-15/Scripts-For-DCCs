import copy


def average2(a, b):
    return (a+b)/2


def average(l):
    a = copy.deepcopy(l[0])
    for i in range(len(l)-1):
        a += l[i+1]
    a /= len(l)
    return a


def getMostInList(l, func=max):
    a = copy.deepcopy(l[0])
    ans = [0]
    for i in range(len(l) - 1):
        ind = i+1
        if l[ind] == a:
            ans.append(ind)
        elif l[ind] == func(l[ind], a):
            ans = [ind]
            a = ind
            # ans.append(ind)
        # else:

            
    return ans


def uniqueList(l):
    search_set = set()
    new_list = []
    for item in l:
        if item not in search_set:
            new_list.append(item)
            search_set.add(item)
            
    return new_list


def appendToListIfUnique(l, item):
    if not item in l:
        l.append(item)