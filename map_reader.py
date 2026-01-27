from pathlib import Path
import pandas as pd
from typing import Any

def read_from_excel(filepath: str, scale = 1, alt=False):
    def read_excel(filepath: str):
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                raise FileNotFoundError(f"Excel文件不存在: {file_path}")

            # 读取Excel文件所有sheet
            excel_data = pd.read_excel(file_path, sheet_name=None)
            return excel_data
        except Exception as e:
            raise Exception(f"读取Excel文件时出错: {str(e)}")

    if alt:
        node_label = 'map_point_data'
        node_id_row = 'PointCode'
        edge_label = 'map_segment_data'
        edge_type = 'type'
        edge_start = 'StartPointCode'
        edge_end = 'EndPointCode'
        weight_row = 'Weight'
        length_row = 'Length'
        bay_row = 'BayCode'
        edge_status_row = 'Status'
    else:
        node_label = 'ControlNode'
        node_id_row = 'id'
        edge_label = 'Rail'
        edge_type = 'Type'
        edge_start = 'start_node'
        edge_end = 'end_node'
        weight_row = 'Weight'
        length_row = 'Length'
        bay_row = 'BayCode'
        edge_status_row = 'Status'
    
    G: dict[str, dict[str, dict[str, Any]]] = {}
    df = read_excel(filepath)

    node_table = df[node_label]
    node_table.dropna()
    for _, row in node_table.iterrows():
        if not G.get(f'{row[node_id_row]}'):
            G[f'{row[node_id_row]}'] = {}

    rail_path_table = df[edge_label]
    rail_path_table.dropna()
    for _, row in rail_path_table.iterrows():
        
        if not G.get(f'{row[edge_start]}'):
            G[f'{row[edge_start]}'] = {}
        G[f'{row[edge_start]}'][f'{row[edge_end]}'] = {'weight': row[weight_row], 'length': row[length_row], 'bay': row[bay_row], 'status': str(row[edge_status_row]), 'type': row[edge_type]}
    
    return G

def _repr(G: dict[Any, dict[Any, dict[str, Any]]]) -> str:
    result = []
    for u in G:
        string = f"{u}: "
        neighbors = []
        for v in G[u]:
            neighbors.append(f"{{{v}: {G[u][v]}}}")
        result.append(string + ", ".join(neighbors))
    return "\n".join(result)
    
if __name__ == "__main__":
    G = read_from_excel('100Sim-4.xlsx', alt=False)
    print(_repr(G))