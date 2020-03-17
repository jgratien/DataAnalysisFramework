import numpy as np
import time
import copy

class Graph:
    def __init__(self):
        self.nodes = set()

    def create(self, n1, n2):
        self.nodes.add(n1)
        self.nodes.add(n2)

    def add_edge(self, n1, n2):
        if n1 in self.nodes:
            self.nodes.add(n2)
            return True

        if n2 in self.nodes:
            self.nodes.add(n1)
            return True

        return False

    def merge(self, graph):
        self.nodes = self.nodes | graph.nodes

    def __repr__(self):
        return self.nodes.__repr__();

    def __str__(self):
        return self.nodes.__str__()


class Conflicts:

    def __init__(self):
        self.mapping = {}
        self.conflicts = []

    @staticmethod
    def _fusion(graph_list):
        g = graph_list[0]
        for i in range(1, len(graph_list)):
            g.merge(graph_list[i])

        return g

    '''
    need a ascending sorted list of connected labels
    '''
    def add_connected(self, connected):
        lbl = connected[0]

        for i in range(1, len(connected)):
            self.conflicts.append((lbl, connected[i]))

    def set_connected(self, connected):
        idx_max = 0
        for t in connected:
            if t[0] > idx_max:
                idx_max = t[0]
            if t[1] > idx_max:
                idx_max = t[1]
        self.conflicts = connected
        return idx_max

    def merge(self, idx_max, with_compact_lbl = True):
        graphes = []

        for (k, v) in self.conflicts:
            connected_g = []

            # retrieves list of graph this edge is connected to
            for g in graphes:
                if g.add_edge(k, v):
                    connected_g.append(g)

            # compute union of all graphes this edge is connected to
            if len(connected_g) > 0:
                for g in connected_g:
                    graphes.remove(g)
                graphes.append(self._fusion(connected_g))
            # or create a new graph feature
            else:
                g = Graph()
                g.create(k, v)
                graphes.append(g)

        for g in graphes:
            g.nodes = sorted(g.nodes)

        #print(graphes)

        # computes correspondence table for values from 0 to idx_max
        self.mapping = {}
        for i in range(0, idx_max+1):
            self.mapping[i] = i
            for g in graphes:
                if i in g.nodes:
                    self.mapping[i] = g.nodes[0]

        if with_compact_lbl:
            cpt = 0
            compact_set = {}
            for v in sorted(self.mapping.values()):
                if v not in compact_set:
                    compact_set[v] = cpt
                    cpt += 1

            for k in self.mapping.keys():
                self.mapping[k] = compact_set[self.mapping[k]]

        return self.mapping


class CCL3D:

    def __init__(self, tuple_par):
        (self.index, self.partition) = tuple_par
        self.labels = np.zeros( self.partition.shape, dtype=int)
        self.labels[1, :, :, :] = self.partition[1, :, :, :]

    def compute(self, offset=0):

        partition = self.partition
        labels = self.labels

        conflicts = Conflicts()

        cpt = 0
        # order does matter, inner x (contiguous in memory), then y, then z
        for z in range(partition.shape[1]):
            for y in range(partition.shape[2]):
                previous = 0
                for x in range(partition.shape[3]):
                    value = partition[0, z, y, x]
                    if value == 1:

                        connected = set()
                        if x > 0 and previous > 0:
                            connected.add(previous)

                        if y > 0:
                            left_label = labels[0, z, y - 1, x]
                            if left_label > 0:
                                connected.add(left_label)

                        if z > 0:
                            up_label = labels[0, z - 1, y, x]
                            if up_label > 0:
                                connected.add(up_label)

                        if len(connected) > 0:
                            connected = sorted(connected)
                            # label is the smallest connected value.
                            labels[0, z, y, x] = connected[0]

                            conflicts.add_connected(connected)

                        else:
                            cpt += 1
                            labels[0, z, y, x] = cpt

                    previous = labels[0, z, y, x]


        t1 = time.process_time()
        #mapping = resolve_labels_conflits(conflicts.conflicts)
        mapping = []
        t2 = time.process_time() - t1
        print("TIME OF CORRECTION OF CONFLICTS SECOND VERSION:", t2)

        # order does not matter
        for i in range(partition.shape[1]):
            for j in range(partition.shape[2]):
                for k in range(partition.shape[3]):
                    for label1, label2 in mapping:
                        if label2 == labels[0, i, j, k]:
                                labels[0, i, j, k] = label1

        return self.index, self.labels



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
            #print("INDEPENDANT NODE",l,l1)
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
