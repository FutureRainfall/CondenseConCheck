from Condensation import condense
from map_reader import read_from_excel
from typing import Any
import random
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy


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
    count = 0
    for u, v in test_pairs:
        if print_progress:
            print(f"\r检查 {u} 到 {v} 连通性...", end="")
        check_connection(C, u, v)
        count += 1
    elapsed = time.perf_counter() - start_time
    # 计算每次查询的平均耗时（纳秒）
    avg_ns_per_query = (elapsed / count * 1e9) if count > 0 else 0
    return elapsed, count, avg_ns_per_query
        
def main_test(args):
    """多进程工作函数"""
    G, num_pairs, dyn_scale, task_id = args
    
    # 随机删除边
    for e_dict in G.values():
        for e in list(e_dict.keys()):
            if random.uniform(0, 1) < dyn_scale:
                del e_dict[e]
    
    # 缩点
    s_c = time.perf_counter()
    C = condense(G)
    e_c = time.perf_counter()
    condensation_time = e_c - s_c
    
    # 生成测试对并测试
    test_pairs = generate_test_pairs(G, num_pairs)
    test_time, query_count, avg_ns_per_query = test(C, test_pairs, print_progress=False)
    
    return task_id, condensation_time, test_time, avg_ns_per_query
    
def main():
    G = read_from_excel('Ohtc-Map-15.xlsx', alt=True)
    print("地图读取完成。")
    test_per_map = 10000
    map_count = 100
    dyn_scale = 0.02
    
    # 获取CPU核心数
    cpu_count = multiprocessing.cpu_count()
    print(f"检测到 {cpu_count} 个CPU核心")
    
    # 存储测试结果
    condensation_times = [0.0] * map_count
    test_times = [0.0] * map_count
    avg_ns_per_queries = [0.0] * map_count
    
    print(f"开始执行 {map_count} 次多进程并行测试...")
    
    # 准备参数列表
    args_list = []
    for i in range(map_count):
        G_copy = deepcopy(G)
        args_list.append((G_copy, test_per_map, dyn_scale, i))
    
    # 使用进程池并行执行
    start_total = time.perf_counter()
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        # 使用map来执行，可以保持顺序
        for task_id, condensation_time, test_time, avg_ns_per_query in executor.map(main_test, args_list):
            condensation_times[task_id] = condensation_time
            test_times[task_id] = test_time
            avg_ns_per_queries[task_id] = avg_ns_per_query
            completed_count = sum(1 for t in test_times if t > 0)
            print(f"\r完成进度: {completed_count}/{map_count} - 最新: 缩点时间 {condensation_time:.4f}s, 测试时间 {test_time:.4f}s, 每次查询 {avg_ns_per_query:.1f}ns", end="")
    
    end_total = time.perf_counter()
    total_elapsed = end_total - start_total
    
    print("\n\n" + "="*60)
    print("测试结果统计:")
    print("="*60)
    print(f"总耗时(多进程): {total_elapsed:.2f}s")
    print(f"使用CPU核心数: {cpu_count}")
    print(f"缩点图建立时间 - 平均: {np.mean(condensation_times):.4f}s, "
          f"最小: {np.min(condensation_times):.4f}s, "
          f"最大: {np.max(condensation_times):.4f}s")
    print(f"测试总时间 - 平均: {np.mean(test_times):.4f}s, "
          f"最小: {np.min(test_times):.4f}s, "
          f"最大: {np.max(test_times):.4f}s")
    print(f"每次查询耗时 - 平均: {np.mean(avg_ns_per_queries):.2f}ns, "
          f"最小: {np.min(avg_ns_per_queries):.2f}ns, "
          f"最大: {np.max(avg_ns_per_queries):.2f}ns")
    print("="*60)
    
    # 生成图表
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文
    plt.rcParams['axes.unicode_minus'] = False  # 用于显示负号
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'多进程并行测试结果统计 (共{map_count}次测试, 每次{test_per_map}组测试对, 使用{cpu_count}核心)', 
                 fontsize=16, fontweight='bold')
    
    # 图1: 缩点图建立时间分布
    axes[0, 0].hist(condensation_times, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('时间 (秒)', fontsize=12)
    axes[0, 0].set_ylabel('频数', fontsize=12)
    axes[0, 0].set_title('(a) 缩点图建立时间分布', fontsize=14)
    axes[0, 0].axvline(np.mean(condensation_times), color='red', linestyle='--', 
                       linewidth=2, label=f'平均值: {np.mean(condensation_times):.4f}s')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 图2: 测试总时间分布
    axes[0, 1].hist(test_times, bins=30, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[0, 1].set_xlabel('时间 (秒)', fontsize=12)
    axes[0, 1].set_ylabel('频数', fontsize=12)
    axes[0, 1].set_title('(b) 测试总时间分布', fontsize=14)
    axes[0, 1].axvline(np.mean(test_times), color='red', linestyle='--', 
                       linewidth=2, label=f'平均值: {np.mean(test_times):.4f}s')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 图3: 缩点图建立时间趋势
    axes[1, 0].plot(range(1, map_count+1), condensation_times, marker='o', 
                    markersize=3, linewidth=1, color='blue', alpha=0.6)
    axes[1, 0].set_xlabel('测试次数', fontsize=12)
    axes[1, 0].set_ylabel('时间 (秒)', fontsize=12)
    axes[1, 0].set_title('(c) 缩点图建立时间趋势', fontsize=14)
    axes[1, 0].axhline(np.mean(condensation_times), color='red', linestyle='--', 
                       linewidth=2, label=f'平均值: {np.mean(condensation_times):.4f}s')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 图4: 测试总时间趋势
    axes[1, 1].plot(range(1, map_count+1), test_times, marker='o', 
                    markersize=3, linewidth=1, color='green', alpha=0.6)
    axes[1, 1].set_xlabel('测试次数', fontsize=12)
    axes[1, 1].set_ylabel('时间 (秒)', fontsize=12)
    axes[1, 1].set_title('(d) 测试总时间趋势', fontsize=14)
    axes[1, 1].axhline(np.mean(test_times), color='red', linestyle='--', 
                       linewidth=2, label=f'平均值: {np.mean(test_times):.4f}s')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_filename = f'test_results_{map_count}maps_{test_per_map}pairs.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存至: {output_filename}")
    
    # 显示图表
    plt.show()
    
if __name__ == "__main__":
    main()
