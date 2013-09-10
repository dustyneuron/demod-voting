import random

def tie_break(change_tuples, find_worst=False):
    dic = {}
    prefs_dic = {}
    candidates = set()
    for change, prefs in change_tuples:
        candidates.add(change)
        prefs_dic[change] = prefs
        
        for p, n in prefs.items():
            if p not in dic:
                dic[p] = {}
            if n not in dic[p]:
                dic[p][n] = set()
            
            dic[p][n].add(change)
        
    if len(candidates) == 1:
        c = list(candidates)[0]
        return (c, prefs_dic[c])
    elif len(candidates) == 0:
        raise Exception('AV tie break had no candidates')
    
    all_pris = list(dic.keys())
    all_pris.sort()
    for p in all_pris:
        all_n = list(dic[p].keys())
        all_n.sort()
        all_n.reverse()
                    
        if find_worst:
            for n in all_n:
                group = dic[p][n]
                candidates = candidates - (group)
            
                if len(candidates) <= 1:
                    break                    
        else:
            highest_n = all_n[0]
            group = dic[p][highest_n]
            candidates = candidates & group
        
        if len(candidates) <= 1:
            break
    
    if len(candidates) >= 1:
        c = random.choice(list(candidates))
        return (c, prefs_dic[c])
    
    raise Exception('AV tie break failed')
