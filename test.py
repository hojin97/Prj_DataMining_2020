import time

def get_input_data(filename):
    with open(filename) as file:
        graph = dict()

        for line in file:
            sp = line.replace('-', '').strip().split('\t')

            for s in sp:
                if s not in graph:
                    graph[s] = set()

            graph[sp[0]].update([sp[1]])
            graph[sp[1]].update([sp[0]])

    return graph

def copyList(graph):
    return_graph = []
    for data in graph:
        return_graph.append(data)
    return return_graph


def find_all_the_subgraphs(graph):
    import time
    start = time.time()
    result_subgraphs = []
    subgraphs = []

    for key in graph.keys():
        s = set([key])
        s.update(graph[key])
        subgraphs.append(s)
    remain_graph = copyList(subgraphs)
    while True:
        if len(remain_graph) == 0 :
            break
        s1 = remain_graph.pop()

        tmp_set = set()
        tmp_set.update(s1)
        while True:
            if len(s1) == 0:
                break
            s2 = s1.pop()

            for set_list in copyList(remain_graph):
                if s2 in set_list:
                    for ver in set_list:
                        if ver not in tmp_set:
                            s1.add(ver)
                    tmp_set.update(set_list)
                    remain_graph.remove(set_list)

        result_subgraphs.append(tmp_set.copy())

    print(f"time : {time.time() - start}")
    # 0.36
    # 8.87
    return result_subgraphs


def get_density(subgraph, graph):
    num_of_edeg = 0

    for v1 in subgraph:
        for v2 in subgraph:
            if v1 == v2:
                continue
            if v2 in graph[v1]:
                num_of_edeg += 1

    return num_of_edeg / (len(subgraph) * (len(subgraph) - 1))


def get_jaccard_index(e1, e2):
    return len(e1 & e2) / len(e1 | e2)


def find_smallest_jaccard_edge(graph):
    smallest_jaccard = len(graph.keys())
    edge = []

    for v1 in graph.keys():
        # if v1 not in graph.keys():
        #     continue

        for v2 in graph[v1]:
            # if v2 not in graph.keys():
            #     continue

            jaccard_index = get_jaccard_index(set(graph[v1]), set(graph[v2]))

            if jaccard_index < smallest_jaccard:
                smallest_jaccard = jaccard_index
                edge = [v1, v2]

    return edge


def apply_hierarchical_algorithm(graph):
    clusters = []
    subgraphs = find_all_the_subgraphs(graph)

    for subgraph in copy.deepcopy(subgraphs):
        density = get_density(subgraph, graph)

        if density >= 0.5:
            for vertex in subgraph:
                del graph[vertex]

            for key in graph.keys():
                if vertex in graph[key]:
                    graph[key].remove(vertex)

            clusters.append(subgraph)
            subgraphs.remove(subgraph)

    for subgraph in subgraphs:
        sub_dict = dict()

        for vertex in subgraph:
            sub_dict[vertex] = graph[vertex]

        target_edge = find_smallest_jaccard_edge(sub_dict)
        print(target_edge)


def main():
    st = time.time()
    input_filename = 'gene_data.txt'
    graph = get_input_data(input_filename)
    clusters = apply_hierarchical_algorithm(graph)
    # print(time.time()-st)


if __name__ == "__main__":
    main()