
def average2(a, b):
    return (a+b)/2


def uniqueList(l):
    search_set = set()
    new_list = []
    for item in l:
        if item not in search_set:
            new_list.append(item)
            search_set.add(item)
            
    return new_list


def appendListIfUnique(l, item):
    if not item in l:
        l.append(item)