from django.contrib.auth.models import User
from django.db import transaction

from voting.models import Section, Change, Vote

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
                new_candidates = candidates - (group)
                if len(new_candidates) == 0:
                    break
                candidates = new_candidates
        else:
            highest_n = all_n[0]
            group = dic[p][highest_n]
            new_candidates = candidates & group
            if len(new_candidates) == 0:
                break
            candidates = new_candidates
    
    if len(candidates) >= 1:
        c = random.choice(list(candidates))
        return (c, prefs_dic[c])
    
    raise Exception('AV tie break failed')

@transaction.commit_on_success
def find_winners():
    winners = {}
    sections = {}
    for section in Section.objects.all():
        sections[section] = []
        change, prefs = section_find_winner(section)
        if change:
            #print(section.name + ' winner is ' + change.name + ' (votes: ' + str(prefs) + ')')
            winners[change] = prefs
        else:
            #print(section.name + ' had no winner')
            pass
        
    for change, prefs in winners.items():
        for affected_section in change.sections.all():
            sections[affected_section].append((change, prefs))
    
    final_winners = {}
    for section, change_tuples in sections.items():
        if change_tuples:
            change, prefs = tie_break(change_tuples)
            if change not in final_winners:
                final_winners[change] = []
            final_winners[change].append((change, prefs))
            
    # if one change is the winner in several sections,
    # return the highest scoring prefs
    for change, change_tuples in final_winners.items():
        _, prefs = tie_break(change_tuples)
        if not prefs:
            raise Exception('prefs battling between identical changes failed')
        final_winners[change] = prefs
        
    return list(final_winners.items())


def section_tie_break(section, change_list, find_worst=False):
    if len(change_list) == 0:
        raise Exception('av tie break given empty change_list')
    #print('section tie break: ' + ' '.join([c.name for c in change_list]))
    
    change_tuples = []
    for change in change_list:
        prefs = {}
        for v in Vote.objects.filter(section=section, change=change).all():
            if v.priority not in prefs:
                prefs[v.priority] = 0
            prefs[v.priority] += 1
            
        change_tuples.append((change, prefs))
        
    #print('section tie break: ' + str(change_tuples))
    return tie_break(change_tuples, find_worst)
    

@transaction.commit_on_success
def section_find_winner(section):
    win_threshold = User.objects.count() / 2
    
    changes = Change.objects.filter(sections=section)
    first_votes = {}
    for c in changes:
        first_votes[c] = Vote.objects.filter(section=section, change=c, priority=1).count()

    while True:                
        lowest_count, lowest_c = None, None
        tuple_list = list(first_votes.items())
        tuple_list.sort(key=lambda x: x[1])
        
        highest_count = tuple_list[len(tuple_list)-1][1]
        if highest_count >= win_threshold:
            top = [t[0] for t in tuple_list if t[1] == highest_count]
            return section_tie_break(section, top)
        
        lowest_count = tuple_list[0][1]
        elim_cands = [t[0] for t in tuple_list if t[1] == lowest_count]
        lowest_c, _ = section_tie_break(section, elim_cands, find_worst=True)
                    
        # re-assign votes for lowest_c to next pref
        for orig_vote in Vote.objects.filter(section=section, change=lowest_c):
            alternates = Vote.objects.filter(user=orig_vote.user, section=section, priority__gt=orig_vote.priority)
            if len(alternates) > 0:
                alt = alternates[0].change
                if alt not in first_votes:
                    first_votes[alt] = 0
                first_votes[alt] += 1
        
        # eliminate lowest_c
        del first_votes[lowest_c]
        
        if len(first_votes) == 0:
            return (None, None)
