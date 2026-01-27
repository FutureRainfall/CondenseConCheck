from SCC import strongly_connected_components
from typing import Any

def condense(G: dict[Any, dict[Any, dict[str, Any]]]):
    scc = list(strongly_connected_components(G))    # 强连通分量列表
    
    mapping = {}    # 原节点 -> SCC 编号的映射
    members = {}    # SCC 编号 -> 原节点集合的映射
    
    for i, component in enumerate(scc):
        # 遍历所有强连通分量，建立映射关系
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

    C = condensation
    return {
        "adj": C,      # 缩点后的邻接表
        "mapping": mapping,    # 原始映射表
        "members": members     # 节点分组成员
    }