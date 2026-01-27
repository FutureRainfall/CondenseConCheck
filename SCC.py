from typing import Any

def strongly_connected_components(G: dict[Any, dict[Any, dict[str, Any]]]):
    """Generate nodes in strongly connected components of graph.

    Parameters
    ----------
    G : Adjacency dict, {node: {neighbor: {attr_name: attr_data}}}.
    """
    preorder = {}
    lowlink = {}
    scc_found = set()
    scc_queue = []
    i = 0  # Preorder counter
    neighbors_iters = {v: iter(G[v]) for v in G}
    for source in G:
        if source not in scc_found:
            queue = [source]    # DFS 栈
            while queue:
                v = queue[-1]   # 出栈
                if v not in preorder:
                    i = i + 1
                    preorder[v] = i     # 未被访问，设置 preorder 编号
                done = True     # 标记是否访问完所有邻居，假设已完成
                for w in neighbors_iters[v]:    # 访问邻居
                    if w not in preorder:       # 未被访问
                        queue.append(w)         # 入栈
                        done = False            # 标记当前邻居未完成
                        break                   # 中断，回到 v=queue[-1]，直接处理子节点
                if done:                        # 所有邻居均已访问完
                    lowlink[v] = preorder[v]    # 初始化 lowlink 值
                    for w in G[v].keys():       # 遍历邻居，更新 lowlink 值
                        if w not in scc_found:  # 仅考虑未归类的节点
                            if preorder[w] > preorder[v]:
                                # 树边，w 为新探索，则 lowlink[v] 指向二者中最早的祖先
                                lowlink[v] = min(lowlink[v], lowlink[w])
                            else:
                                # 回边或横向边，此时 w 可能没有处理完成，则 lowlink[v] 暂时指向 preorder[w]，认为 w 是 v 的最早祖先
                                lowlink[v] = min(lowlink[v], preorder[w])
                    queue.pop()     # v 处理完成，出栈
                    if lowlink[v] == preorder[v]:
                        # v 能回溯到的最早祖先是自己，代表找到一个强连通分量
                        scc = {v}       # v 是这个强连通分量的根
                        while scc_queue and preorder[scc_queue[-1]] > preorder[v]:  
                            # 如果 v 是根，将栈中 preorder 编号比 v 大的节点都弹出，归入当前强连通分量
                            k = scc_queue.pop()
                            scc.add(k)
                        scc_found.update(scc)
                        yield scc               # 产出当前强连通分量
                    else:
                        scc_queue.append(v)     # v 不是强连通分量根，加入栈中等待归类，继续查找它的祖先