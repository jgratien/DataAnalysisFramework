import numpy as np
import time
import copy


def resolve_labels_conflits(ref_conflits):
    conflits = copy.deepcopy(ref_conflits)
    labels = []
    label_conflits = {}
    c_index = 0
    for c in conflits:
        if c[0] not in labels:
            labels.append(c[0])
            label_conflits[c[0]] = [c_index]
        else:
            label_conflits[c[0]].append(c_index)

        if c[1] not in labels:
            labels.append(c[1])
            label_conflits[c[1]] = [c_index]
        else:
            label_conflits[c[1]].append(c_index)
        c_index = c_index + 1
    ordered_labels = []
    ic = 0
    for c in conflits:
        l = c[0]
        ordered_labels.append(l)
        l1 = c[1]
        for k in label_conflits[l]:
            if k > ic:
                lc = conflits[k]
                lc0 = lc[0]
                lc1 = lc[1]
                if lc[0] == l:
                    conflits[k] = copy.deepcopy((l1, lc1))
                else:
                    conflits[k] = copy.deepcopy((lc0, l1))

        ic = ic + 1
    independant_labels = []
    new_labels = {}
    for l in labels:
        if l not in ordered_labels:
            independant_labels.append(l)
            new_labels[l] = l

    res_list = []
    nc = len(conflits)
    for i in range(nc):
        c = conflits[nc - i - 1]
        if c[1] not in new_labels:
            if c[1] != c[0]:
                print("UNXPECTED ERROR", c[1], "NOT EQUAL", c[0])
            new_labels[c[1]] = c[1]
        res_list.append((c[0], new_labels[c[1]]))
        new_labels[c[0]] = new_labels[c[1]]
    return res_list


def resolve_labels_conflits_v2(ref_conflits, nb_conflits):
    #print("REF CONFLITS",ref_conflits[:nb_conflits])
    t0 = time.process_time()
    conflits = copy.deepcopy(ref_conflits[:nb_conflits])
    t1 = time.process_time() - t0
    print("TIME OF DEEP COPY :", t1)
    labels = []
    label_conflits = {}
    c_index = 0
    for i in range(nb_conflits):
        c = conflits[i]
        if c[0] not in labels: 
            labels.append(c[0])
            label_conflits[c[0]] = [c_index]
        else:
            label_conflits[c[0]].append(c_index)

        if c[1] not in labels:
            labels.append(c[1])
            label_conflits[c[1]] = [c_index]
        else:
            label_conflits[c[1]].append(c_index)
        c_index = c_index + 1
    print("NB LABELS;",len(labels))
    print("NB CONFLITS:",nb_conflits)
    #print("LABELS:\n",labels)
    ordered_labels = []
    ic = 0
    for i in range(nb_conflits):
        c = conflits[i]
        l = c[0]
        ordered_labels.append(l)
        l1 = c[1]
        #print("ITER(",i,")=",l,l1)
        if l==l1:
            print("INDEPENDANT NODE",l,l1)
            ic += 1
            continue
        for k in label_conflits[l]:
            if k > ic:
                lc = conflits[k]

                lc0 = lc[0]
                lc1 = lc[1]
                if lc[0] == l:
                    conflits[k] = copy.deepcopy((l1, lc1))
                    label_conflits[l1].append(k)
                else:
                    conflits[k] = copy.deepcopy((lc0, l1))
                    label_conflits[l1].append(k)

        ic = ic + 1
    #print("ORD LABELS",ordered_labels)
    #print("CONFLITS",conflits[:nb_conflits])
    independant_labels = []
    new_labels = {}
    for l in labels:
        if l not in ordered_labels:
            independant_labels.append(l)
            new_labels[l] = l

    #print("IND LABELS",independant_labels)

    res_list = []
    nc = len(conflits)
    for i in range(nc):
        c = conflits[nc - i - 1]
        if c[1] not in new_labels:
            if c[1] != c[0]:
                print("UNXPECTED ERROR", c[1], "NOT EQUAL", c[0])
            new_labels[c[1]] = c[1]
        res_list.append((c[0], new_labels[c[1]]))
        new_labels[c[0]] = new_labels[c[1]]
    return res_list
