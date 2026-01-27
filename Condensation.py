from SCC import strongly_connected_components

def condensation_native(G, scc=None):
    # 如果没有提供 SCC，则调用之前写好的原生 SCC 算法
    if scc is None:
        scc = list(strongly_connected_components(G))
    
    mapping = {}    # 原节点 -> SCC 编号的映射
    members = {}    # SCC 编号 -> 原节点集合的映射
    
    for i, component in enumerate(scc):
        members[i] = set(component)
        for node in component:
            mapping[node] = i

    num_components = len(scc)
    condensation = {i: set() for i in range(num_components)}

    for u in G:
        for v in G[u]:
            u_scc = mapping[u]
            v_scc = mapping[v]
            if u_scc != v_scc:
                condensation[u_scc].add(v_scc)

    C = {k: list(v) for k, v in condensation.items()}

    return {
        "adj": C,      # 缩点后的邻接表
        "mapping": mapping,    # 原始映射表
        "members": members     # 节点分组成员
    }