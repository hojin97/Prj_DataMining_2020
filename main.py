import pandas as pd
import numpy as np
import copy
import math

# gene_id : 버텍스들의 집합
def initial_data(filename):
    input_file = open(filename, 'r')
    adjacent_vertex = dict()
    gene_id = set()
    for line in input_file:
        for value in line.split():
            gene_id.add(value)

    gene_id = list(gene_id)
    gene_id.sort()

    zero_graph = np.zeros((len(gene_id), len(gene_id)), dtype=int)
    original_graph = pd.DataFrame(zero_graph, index=gene_id, columns=gene_id)

    # 원본 그래프 만들기.
    # 그래프는 알파벳 순으로 만들어졌다.
    input_file = open(filename, 'r')
    for line in input_file:
        con = line.split()
        original_graph._set_value(con[0], con[1], 1)
        original_graph._set_value(con[1], con[0], 1)

        if adjacent_vertex.get(con[0]) == None: adjacent_vertex[con[0]] = con[1]
        else: adjacent_vertex[con[0]] = adjacent_vertex[con[0]] + "," + con[1]

        if adjacent_vertex.get(con[1]) == None: adjacent_vertex[con[1]] = con[0]
        else: adjacent_vertex[con[1]] = adjacent_vertex[con[1]] + "," + con[0]

    return original_graph, adjacent_vertex, gene_id

def make_weight_graph(original_graph, adjacent_vertex, gene_id):
    initial_graph = np.array([-1] * len(gene_id)*len(gene_id)).reshape(len(gene_id), len(gene_id))
    weight_graph = pd.DataFrame(initial_graph, index=gene_id, columns=gene_id)

    for base_ver in gene_id:
        adj = adjacent_vertex[base_ver].split(',')
        base_degree = original_graph.__getitem__(base_ver).sum()
        for adj_ver in adj:
            adj_degree = original_graph.__getitem__(adj_ver).sum()
            if weight_graph._get_value(base_ver, adj_ver) == -1:
                if base_degree == 1 or adj_degree == 1:
                    weight_graph._set_value(base_ver, adj_ver, 0)
                    weight_graph._set_value(adj_ver, base_ver, 0)
                else:
                    weight_graph._set_value(base_ver, adj_ver, abs(base_degree - adj_degree))
                    weight_graph._set_value(adj_ver, base_ver, abs(base_degree - adj_degree))
    return weight_graph

def check_value(cnt_value):
    keys = list(cnt_value.keys())
    used_lv = list()
    for key in keys:
        if cnt_value[key][0] < 2:
            del(cnt_value[key])
        else:
            used_lv.append(key)
    return cnt_value, used_lv

def conversion_adj(cnt_value):
    keys = list(cnt_value.keys())
    tmp_cnt_value = dict()
    cnt_value_list = list()
    for key in keys:
        tmp_cnt_value[cnt_value[key][1]] = cnt_value[key].copy()
        # 처음 값은 빈번 횟수, 두 번째 값은 row 값이다. 필요없는 값이라 제거한다.
        tmp_cnt_value[cnt_value[key][1]].pop(1)
        tmp_cnt_value[cnt_value[key][1]].pop(0)
        cnt_value_list.append(copy.deepcopy(tmp_cnt_value))
    return cnt_value_list

def find_adj_id(weight_graph, cnt_value, used_lv):
    curr_adj = list()
    index = weight_graph.index
    cnt_value_list = conversion_adj(cnt_value)
    tmp_cluster = copy.deepcopy(cnt_value_list)
    for u_idx, step in enumerate(cnt_value_list):
        level = used_lv[u_idx]
        s_idx = cnt_value_list.index(step)
        for k in cnt_value_list[s_idx].keys():
            for d in cnt_value_list[s_idx][k]:
                curr_adj.append(d)
        while True:
            if len(curr_adj) == 0:
                break
            curr_id = curr_adj.pop()

            # 가로줄 탐색
            for i, col in enumerate(weight_graph.get(index[curr_id])):
                if i <= curr_id:
                    # print(col)
                    continue
                # adj_data = weight_graph._get_value(index[curr_id], index[i])
                if col == level:
                    weight_graph._set_value(index[curr_id], index[i], -1)
                    curr_adj.append(i)
                    if tmp_cluster[s_idx].get(curr_id) == None:
                        tmp_cluster[s_idx][curr_id] = list()
                        tmp_cluster[s_idx][curr_id].append(i)
                    else:
                        tmp_cluster[s_idx][curr_id].append(i)

            # 세로줄 탐색
            for row in range(len(index)):
                if row > curr_id - 1:
                    break
                adj_data = weight_graph._get_value(index[row], index[curr_id])
                if adj_data == level:
                    if row in tmp_cluster[s_idx].keys():
                        continue
                    else:
                        weight_graph._set_value(index[row], index[curr_id], -1)
                        curr_adj.append(row)
                        if tmp_cluster[s_idx].get(curr_id) == None:
                            tmp_cluster[s_idx][curr_id] = list()
                            tmp_cluster[s_idx][curr_id].append(row)
                        else:
                            tmp_cluster[s_idx][curr_id].append(row)

    return tmp_cluster

def grouping_weight_id(weight_graph):
    final_cluster_list = list()
    cnt_value = dict()
    index = weight_graph.index

    for row in range(len(index)):
        cnt_value.clear()
        # 가로 한 줄 체크.
        for col in range(row+1, len(index)):
            value = weight_graph._get_value(index[row], index[col])
            if value == -1:
                continue
            else:
                if cnt_value.get(value) == None :
                    cnt_value[value] = list()
                    cnt_value[value].append(1)
                    cnt_value[value].append(row)
                    cnt_value[value].append(col)
                else:
                    cnt_value[value][0] += 1
                    cnt_value[value].append(col)

        # 세로 한 줄 체크
        for ver in range(0, row):
            value = weight_graph._get_value(index[ver], index[row])
            if value == -1:
                continue
            else:
                if cnt_value.get(value) == None:
                    cnt_value[value] = list()
                    cnt_value[value].append(1)
                    cnt_value[value].append(row)
                    cnt_value[value].append(ver)
                else:
                    cnt_value[value][0] += 1
                    cnt_value[value].append(ver)

        cnt_value, used_lv = check_value(cnt_value)
        if len(cnt_value) == 0:
            continue
        tmp = find_adj_id(weight_graph, cnt_value, used_lv)
        clustered_set = make_form(tmp, used_lv, weight_graph)
        if clustered_set in final_cluster_list:
            pass
        else:
            final_cluster_list.append(clustered_set)

    return final_cluster_list

def make_form(clustered_set, used_lv, weight_graph):
    index = weight_graph.index
    result_dict = dict()
    cluster_genes_set = set()
    tmp_set = set()
    for i, group in enumerate(clustered_set):
        level = used_lv[i]
        tmp_set.clear()
        cluster_genes_set.clear()
        for key in group.keys():
            tmp_set.add(key)
            for data in group[key]:
                tmp_set.add(data)

        for idx in tmp_set:
            cluster_genes_set.add(index[idx])

        result_dict[level] = list(cluster_genes_set)
        result_dict[level].sort()

    return result_dict

def output_to_file(filename, result_dict):
    file = open(filename, 'w')
    merge_data = list()
    for group in result_dict:
        for key in group.keys():
            merge_data.append(group[key].copy())
            merge_data[merge_data.index(group[key])].insert(0, key)

    merge_data.sort()
    for data in merge_data:
        file.write(f"{data[0]} {len(data) - 1} ")
        for d in data[1:]:
            file.write(f"{d} ")
        file.write('\n')

    file.close()

# The main function
def main():
    import time
    start = time.time()
    input_filename = 'gene_data.txt'
    original_graph, adjacent_vertex, gene_id = initial_data(input_filename)
    weight_graph = make_weight_graph(original_graph, adjacent_vertex, gene_id)
    #print(original_graph)
    #print()
    #print(weight_graph)
    result_dict = grouping_weight_id(weight_graph)

    # 결과 값 출력 ------------
    output_filename = 'result.txt'
    output_to_file(output_filename, result_dict)
    print(time.time()-start)


if __name__ == '__main__':
    main()