#!/usr/bin/env python3
"""
为 ICLR 2026 论文数据文件添加评分信息。

本脚本功能：
1. 将评分信息（ratings, min_rating, max_rating, avg_rating, reviewer_count）
   添加到 iclr26_all_papers.json 和 iclr26_all_papers.csv
2. 为 iclr26_all_papers_with_ratings.json 中的每篇论文添加 accepted_flag 字段
"""

import json
import csv
from pathlib import Path


def load_json(filepath):
    """加载 JSON 文件。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath):
    """保存数据到 JSON 文件。"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_csv(filepath):
    """加载 CSV 文件。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_csv(data, filepath, fieldnames):
    """保存数据到 CSV 文件。"""
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main():
    base_dir = Path(__file__).parent

    # 文件路径
    all_papers_json_path = base_dir / 'iclr26_all_papers.json'
    all_papers_csv_path = base_dir / 'iclr26_all_papers.csv'
    papers_with_ratings_path = base_dir / 'iclr26_all_papers_with_ratings.json'

    # 加载数据
    print("正在加载数据文件...")
    all_papers_json = load_json(all_papers_json_path)
    all_papers_csv = load_csv(all_papers_csv_path)
    papers_with_ratings = load_json(papers_with_ratings_path)

    # 创建 paper_id 到评分信息的映射
    print("正在创建评分映射...")
    ratings_map = {}
    for paper in papers_with_ratings:
        paper_id = paper.get('paper_id')
        if paper_id:
            ratings_map[paper_id] = {
                'ratings': paper.get('ratings', []),        # 各审稿人评分列表
                'min_rating': paper.get('min_rating'),      # 最低评分
                'max_rating': paper.get('max_rating'),      # 最高评分
                'avg_rating': paper.get('avg_rating'),      # 平均评分
                'reviewer_count': paper.get('reviewer_count')  # 审稿人数量
            }

    # 更新 iclr26_all_papers.json 的评分信息
    print("正在更新 iclr26_all_papers.json...")
    updated_count_json = 0
    for paper in all_papers_json:
        paper_id = paper.get('id')
        if paper_id and paper_id in ratings_map:
            paper['ratings'] = ratings_map[paper_id]['ratings']
            paper['min_rating'] = ratings_map[paper_id]['min_rating']
            paper['max_rating'] = ratings_map[paper_id]['max_rating']
            paper['avg_rating'] = ratings_map[paper_id]['avg_rating']
            paper['reviewer_count'] = ratings_map[paper_id]['reviewer_count']
            updated_count_json += 1

    save_json(all_papers_json, all_papers_json_path)
    print(f"  已更新 {updated_count_json} 篇论文（JSON 文件）")

    # 更新 iclr26_all_papers.csv 的评分信息
    print("正在更新 iclr26_all_papers.csv...")
    updated_count_csv = 0
    for paper in all_papers_csv:
        paper_id = paper.get('id')
        if paper_id and paper_id in ratings_map:
            # CSV 中将 ratings 列表转为 JSON 字符串存储
            paper['ratings'] = json.dumps(ratings_map[paper_id]['ratings'])
            paper['min_rating'] = ratings_map[paper_id]['min_rating']
            paper['max_rating'] = ratings_map[paper_id]['max_rating']
            paper['avg_rating'] = ratings_map[paper_id]['avg_rating']
            paper['reviewer_count'] = ratings_map[paper_id]['reviewer_count']
            updated_count_csv += 1
        else:
            # 对于没有评分信息的论文，设置空值
            paper['ratings'] = '[]'
            paper['min_rating'] = ''
            paper['max_rating'] = ''
            paper['avg_rating'] = ''
            paper['reviewer_count'] = ''

    # 获取字段名列表，包含新增的评分列
    fieldnames = list(all_papers_csv[0].keys()) if all_papers_csv else []
    for field in ['ratings', 'min_rating', 'max_rating', 'avg_rating', 'reviewer_count']:
        if field not in fieldnames:
            fieldnames.append(field)

    save_csv(all_papers_csv, all_papers_csv_path, fieldnames)
    print(f"  已更新 {updated_count_csv} 篇论文（CSV 文件）")

    # 为 iclr26_all_papers_with_ratings.json 添加 accepted_flag
    # 判断逻辑：如果论文存在于 iclr26_all_papers.json 中，则为已接受
    print("正在为 iclr26_all_papers_with_ratings.json 添加 accepted_flag...")
    accepted_ids = {paper.get('id') for paper in all_papers_json}
    accepted_count = 0
    for paper in papers_with_ratings:
        paper_id = paper.get('paper_id')
        if paper_id in accepted_ids:
            paper['accepted_flag'] = True
            accepted_count += 1
        else:
            paper['accepted_flag'] = False

    save_json(papers_with_ratings, papers_with_ratings_path)
    print(f"  论文总数: {len(papers_with_ratings)}")
    print(f"  已接受论文数: {accepted_count}")
    print(f"  已拒绝论文数: {len(papers_with_ratings) - accepted_count}")

    print("\n完成!")


if __name__ == '__main__':
    main()
