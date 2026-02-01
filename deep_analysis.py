"""
ICLR 2026 论文深度分析

分析内容：
1. 文本分析 (text_analysis)
   - 标题长度分布（单词数）
   - 摘要长度分布（单词数）
   - 热门话题词频统计（LLM, Diffusion, Reinforcement 等）
   - 标题长度 vs 摘要长度 散点图

2. 关键词深度分析 (keyword_analysis)
   - Top 20 高频关键词
   - Top 15 关键词共现对

3. 领域交叉分析 (area_analysis)
   - 各领域论文数量分布
   - 各领域平均 replyCount 对比

4. 相关性分析 (correlation_analysis)
   - 标题长度 vs replyCount
   - 摘要长度 vs replyCount
   - 投稿顺序 vs replyCount
   - 标题热门词 vs replyCount（LLM, Learning, Diffusion, Multimodal, Vision, Agent 等）

输出图片保存在 images/ 目录下
"""

import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations

# 创建 images 目录
os.makedirs("images", exist_ok=True)

# 设置字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def count_words(text: str) -> int:
    """计算去除标点符号后的单词数量"""
    text = re.sub(r'[^\w\s]', ' ', str(text))
    words = [w for w in text.split() if w]
    return len(words)


def load_data(filepath: str) -> pd.DataFrame:
    """加载数据"""
    df = pd.read_csv(filepath)
    print(f"总论文数: {len(df)}\n")
    return df


# ============================================================
# 1. 文本分析
# ============================================================
def text_analysis(df: pd.DataFrame):
    """文本分析：标题/摘要长度分布，热门话题词频"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 计算单词数（去除标点）
    df["title_words"] = df["title"].apply(count_words)
    df["abstract_words"] = df["abstract"].apply(count_words)

    # 1.1 标题长度分布（单词数）
    axes[0, 0].hist(df["title_words"], bins=20, color="steelblue", edgecolor="black", alpha=0.7)
    axes[0, 0].axvline(df["title_words"].mean(), color="red", linestyle="--",
                       label=f'Mean: {df["title_words"].mean():.1f}')
    axes[0, 0].set_xlabel("Title Length (words)")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].set_title("Title Length Distribution", fontweight="bold")
    axes[0, 0].legend()

    # 1.2 摘要长度分布（单词数）
    axes[0, 1].hist(df["abstract_words"], bins=30, color="coral", edgecolor="black", alpha=0.7)
    axes[0, 1].axvline(df["abstract_words"].mean(), color="red", linestyle="--",
                       label=f'Mean: {df["abstract_words"].mean():.0f}')
    axes[0, 1].set_xlabel("Abstract Length (words)")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].set_title("Abstract Length Distribution", fontweight="bold")
    axes[0, 1].legend()

    # 1.3 热门话题词频（标题中）
    hot_topics = [
        'LLM', 'Transformer', 'Diffusion', 'Reinforcement', 'Graph',
        'Vision', 'Multimodal', 'Generative', 'Attention', 'Contrastive',
        'Self-supervised', 'Pre-train', 'Fine-tun', 'Prompt', 'Agent',
        'Reasoning', 'Alignment', 'RLHF', 'RAG', 'Embedding'
    ]
    topic_counts = {}
    titles_lower = df["title"].astype(str).str.lower()
    for topic in hot_topics:
        count = titles_lower.str.contains(topic.lower(), regex=False).sum()
        if count > 0:
            topic_counts[topic] = count

    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    if sorted_topics:
        topics, counts = zip(*sorted_topics)
        axes[1, 0].barh(range(len(topics)), counts, color="mediumpurple")
        axes[1, 0].set_yticks(range(len(topics)))
        axes[1, 0].set_yticklabels(topics)
        axes[1, 0].set_xlabel("Number of Papers")
        axes[1, 0].set_title("Hot Topics in Titles", fontweight="bold")
        axes[1, 0].invert_yaxis()

    # 1.4 标题长度 vs 摘要长度 散点图
    axes[1, 1].scatter(df["title_words"], df["abstract_words"], alpha=0.3, s=10, c="seagreen")
    corr = df["title_words"].corr(df["abstract_words"])
    axes[1, 1].set_xlabel("Title Length (words)")
    axes[1, 1].set_ylabel("Abstract Length (words)")
    axes[1, 1].set_title(f"Title vs Abstract Length (Corr: {corr:.3f})", fontweight="bold")

    plt.tight_layout()
    plt.savefig("images/deep_analysis_1_text.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("文本分析图已保存: deep_analysis_1_text.png\n")


# ============================================================
# 2. 关键词深度分析
# ============================================================
def keyword_analysis(df: pd.DataFrame):
    """关键词深度分析：Top 20 关键词，共现网络，与领域关联"""
    # 解析所有关键词
    all_keywords = []
    keyword_lists = []
    for kw in df["keywords"].dropna():
        words = [w.strip().lower() for w in str(kw).split() if len(w.strip()) > 2]
        all_keywords.extend(words)
        keyword_lists.append(words)

    keyword_counts = Counter(all_keywords)
    top_20 = keyword_counts.most_common(20)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 2.1 Top 20 关键词
    if top_20:
        words, counts = zip(*top_20)
        axes[0].barh(range(len(words)), counts, color="teal")
        axes[0].set_yticks(range(len(words)))
        axes[0].set_yticklabels(words)
        axes[0].set_xlabel("Frequency")
        axes[0].set_title("Top 20 Keywords", fontweight="bold")
        axes[0].invert_yaxis()

    # 2.2 关键词共现统计（Top 15 共现对）
    cooccur = Counter()
    for kw_list in keyword_lists:
        unique_kw = list(set(kw_list))
        for pair in combinations(sorted(unique_kw), 2):
            cooccur[pair] += 1

    top_pairs = cooccur.most_common(15)
    if top_pairs:
        pair_labels = [f"{p[0]} & {p[1]}" for p, _ in top_pairs]
        pair_counts = [c for _, c in top_pairs]
        axes[1].barh(range(len(pair_labels)), pair_counts, color="darkorange")
        axes[1].set_yticks(range(len(pair_labels)))
        axes[1].set_yticklabels(pair_labels, fontsize=9)
        axes[1].set_xlabel("Co-occurrence Count")
        axes[1].set_title("Top 15 Keyword Co-occurrences", fontweight="bold")
        axes[1].invert_yaxis()

    plt.tight_layout()
    plt.savefig("images/deep_analysis_2_keywords.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("关键词分析图已保存: deep_analysis_2_keywords.png\n")


# ============================================================
# 3. 领域交叉分析
# ============================================================
def area_analysis(df: pd.DataFrame):
    """领域交叉分析：各领域 replyCount 对比，各领域热门关键词"""
    def process_area(area):
        if pd.isna(area):
            return ""
        return re.sub(r'\([^)]*\)', '', str(area)).split(',')[0].strip()

    df["main_area"] = df["primary_area"].apply(process_area)

    # 按论文数量排序，作为统一的顺序
    area_order = df["main_area"].value_counts().index.tolist()

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 3.1 各领域论文数量（按论文数量排序）
    area_counts = df["main_area"].value_counts().reindex(area_order)
    axes[0].barh(range(len(area_counts)), area_counts.values, color="steelblue")
    axes[0].set_yticks(range(len(area_counts)))
    axes[0].set_yticklabels(area_counts.index, fontsize=8)
    axes[0].set_xlabel("Number of Papers")
    axes[0].set_title("Papers by Area", fontweight="bold")
    axes[0].invert_yaxis()

    # 3.2 各领域平均 replyCount（按论文数量排序）
    area_reply = df.groupby("main_area")["replyCount"].mean()
    area_reply = area_reply.reindex(area_order)

    axes[1].barh(range(len(area_reply)), area_reply.values, color="indianred")
    axes[1].set_yticks(range(len(area_reply)))
    axes[1].set_yticklabels(area_reply.index, fontsize=8)
    axes[1].set_xlabel("Average Reply Count")
    axes[1].set_title("Average Reply Count by Area", fontweight="bold")
    axes[1].invert_yaxis()

    plt.tight_layout()
    plt.savefig("images/deep_analysis_3_areas.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("领域分析图已保存: deep_analysis_3_areas.png\n")


# ============================================================
# 4. 相关性分析
# ============================================================
def correlation_analysis(df: pd.DataFrame):
    """相关性分析：长度与 replyCount，投稿顺序与 replyCount，热门词与 replyCount"""
    df["title_words"] = df["title"].apply(count_words)
    df["abstract_words"] = df["abstract"].apply(count_words)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 4.1 标题长度 vs replyCount
    axes[0, 0].scatter(df["title_words"], df["replyCount"], alpha=0.3, s=10, c="steelblue")
    axes[0, 0].set_xlabel("Title Length (words)")
    axes[0, 0].set_ylabel("Reply Count")
    axes[0, 0].set_title("Title Length vs Reply Count", fontweight="bold")
    corr1 = df["title_words"].corr(df["replyCount"])
    axes[0, 0].text(0.05, 0.95, f"Corr: {corr1:.3f}", transform=axes[0, 0].transAxes, fontsize=12)

    # 4.2 摘要长度 vs replyCount
    axes[0, 1].scatter(df["abstract_words"], df["replyCount"], alpha=0.3, s=10, c="coral")
    axes[0, 1].set_xlabel("Abstract Length (words)")
    axes[0, 1].set_ylabel("Reply Count")
    axes[0, 1].set_title("Abstract Length vs Reply Count", fontweight="bold")
    corr2 = df["abstract_words"].corr(df["replyCount"])
    axes[0, 1].text(0.05, 0.95, f"Corr: {corr2:.3f}", transform=axes[0, 1].transAxes, fontsize=12)

    # 4.3 投稿顺序 vs replyCount
    axes[1, 0].scatter(df["number"], df["replyCount"], alpha=0.3, s=10, c="mediumpurple")
    axes[1, 0].set_xlabel("Submission Number (smaller = earlier)")
    axes[1, 0].set_ylabel("Reply Count")
    axes[1, 0].set_title("Submission Order vs Reply Count", fontweight="bold")
    corr3 = df["number"].corr(df["replyCount"])
    axes[1, 0].text(0.05, 0.95, f"Corr: {corr3:.3f}", transform=axes[1, 0].transAxes, fontsize=12)

    # 4.4 标题是否包含热门词 vs replyCount
    hot_words = ['LLM', 'Learning', 'Diffusion', 'Reinforcement', 'Multimodal', 'Vision', 'video', 'Agent', 'Generation', 'reasoning']
    titles_lower = df["title"].astype(str).str.lower()

    hot_word_reply = {}
    for word in hot_words:
        mask = titles_lower.str.contains(word.lower(), regex=False)
        if mask.sum() > 0:
            hot_word_reply[word] = df[mask]["replyCount"].mean()

    if hot_word_reply:
        sorted_items = sorted(hot_word_reply.items(), key=lambda x: x[1], reverse=True)
        words, avg_replies = zip(*sorted_items)
        colors = plt.cm.RdYlGn([r / max(avg_replies) for r in avg_replies])
        axes[1, 1].barh(range(len(words)), avg_replies, color=colors)
        axes[1, 1].set_yticks(range(len(words)))
        axes[1, 1].set_yticklabels(words)
        axes[1, 1].set_xlabel("Average Reply Count")
        axes[1, 1].set_title("Hot Words in Title vs Reply Count", fontweight="bold")
        axes[1, 1].invert_yaxis()

    plt.tight_layout()
    plt.savefig("images/deep_analysis_4_correlation.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("相关性分析图已保存: deep_analysis_4_correlation.png\n")


def main():
    df = load_data("iclr26_all_papers.csv")

    print("=" * 60)
    print("1. 文本分析")
    print("=" * 60)
    text_analysis(df)

    print("=" * 60)
    print("2. 关键词深度分析")
    print("=" * 60)
    keyword_analysis(df)

    print("=" * 60)
    print("3. 领域交叉分析")
    print("=" * 60)
    area_analysis(df)

    print("=" * 60)
    print("4. 相关性分析")
    print("=" * 60)
    correlation_analysis(df)

    print("所有分析完成!")


if __name__ == "__main__":
    main()
