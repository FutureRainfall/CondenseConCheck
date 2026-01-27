# CondenseConCheck

## 强连通分支（SCC）缩点图的连通性检查。

- **算法输入**：原图G的邻接表字典，格式：{u_id: {v_id: {attr_name: attr_data}}}，其中 u_id ***必须包含图中所有节点***，v_id 可为空（表示没有子节点的节点），属性字典也可为空，没有实际应用

- **`SCC.py`**：产生原图的强连通分支（SCC）缩点图。

- **`Condensation.py`**：输入图 G，调用 `SCC.py`输出 G 的缩点图 C ，返回字典，其中包括键 'abj', 'mapping', 'members'。

  - **'adj'** 的值为缩点图 C 邻接表，格式为 'adj': {SCC1_id: set(SCC2_id)}，即所有 SCC -> 邻居 SCC
  - **'mapping'** 为节点 id -> SCC_id 映射字典，格式为 'mapping': {node_id: SCC_id}，记录原图节点在哪个 SCC 中
  - **'members'** 为 SCC_id -> 节点 id 的映射字典，格式为 'members': {SCC_id: set(node_id)}，记录一个 SCC 中包含原图的哪些节点
- **`map_reader.py`**：读取`100Sim-4.xlsx`地图并建立地图字典
- **`test.py`**：读取地图、建立缩点图、在原图上随机抽取 10000 个测试点对，并使用缩点图测试连通性，记录总用时