from Condensation import condense
from map_reader import read_from_excel
import random
import time


def generate_test_pairs(G, num_pairs=10000):
    test_pairs: set[tuple[str, str]] = set()
    for _ in range(num_pairs):
        u = random.choice(list(G.keys()))
        while True:
            v = random.choice(list(G.keys()))
            if u != v and (u, v) not in test_pairs:
                break
        test_pairs.add((u, v))
    return test_pairs

def check_connection(C, u: str, v: str) -> bool:
    u_scc = C['mapping'][u]
    v_scc = C['mapping'][v]
    
    if u_scc == v_scc:
        return True
    else:
        return v_scc in C['adj'][u_scc]

def test(C, test_pairs: set[tuple[str, str]], print_progress=False):
    start_time = time.perf_counter()
    for u, v in test_pairs:
        if print_progress:
            print(f"\r检查 {u} 到 {v} 连通性...", end="")
        check_connection(C, u, v)
    return time.perf_counter() - start_time
        
def main():
    num_pairs = 10000
    G = read_from_excel('100Sim-4.xlsx', alt=False)
    print("地图读取完成。")
    C = condense(G)
    print("图缩点完成。")
    test_pairs = generate_test_pairs(G, num_pairs)
    print(f"已生成 {num_pairs} 组测试对。")
    test_time = test(C, test_pairs, print_progress=True)
    print("\r                             ", end="")  # 清除进度行
    print(f"\r{num_pairs} 次测试完成，总用时: {test_time:.4f} 秒")
    
if __name__ == "__main__":
    main()