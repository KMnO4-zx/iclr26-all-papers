import json
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 设置全局样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# 配色方案
COLORS = {
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'accent': '#e74c3c',
    'purple': '#9b59b6',
    'orange': '#f39c12',
    'dark': '#2c3e50',
    'light': '#ecf0f1'
}

# 停用词列表
STOPWORDS = {
    'large', 'model', 'models', 'learning', 'deep', 'neural', 'network', 'networks',
    'language', 'machine', 'based', 'using', 'via', 'for', 'with', 'and', 'the',
    'of', 'in', 'to', 'a', 'an', 'on', 'by', 'from', 'as', 'is', 'are', 'be',
    'data', 'method', 'methods', 'approach', 'new', 'novel', 'efficient', 'improved'
}


def load_data(filepath: str) -> pd.DataFrame:
    """加载数据"""
    df = pd.read_csv(filepath)
    print(f"总论文数: {len(df)}")
    print(f"字段: {df.columns.tolist()}\n")
    return df


def load_ratings_data(filepath: str) -> pd.DataFrame:
    """加载带评分的完整数据（包含所有投稿）"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"总投稿数: {len(df)}")
    print(f"已接受: {df['accepted_flag'].sum()}")
    print(f"已拒绝: {(~df['accepted_flag']).sum()}\n")
    return df


def plot_keywords_wordcloud(df: pd.DataFrame, ax):
    """绘制关键词词云图"""
    all_keywords = " ".join(df["keywords"].dropna().astype(str))
    wc = WordCloud(
        width=800, height=400,
        background_color="white",
        max_words=150,
        colormap="Blues",
        stopwords=STOPWORDS,
        prefer_horizontal=0.7,
        min_font_size=8
    ).generate(all_keywords)

    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Keywords Word Cloud", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)


def plot_primary_area(df: pd.DataFrame, ax):
    """绘制 Primary Area 分布图"""
    counts = df["primary_area"].dropna().value_counts()
    print("Primary Area 分布:")
    print(counts, "\n")

    # 使用渐变色
    colors = plt.cm.Blues(0.3 + 0.5 * counts.values / counts.values.max())
    ax.barh(range(len(counts)), counts.values, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, fontsize=7)
    ax.set_xlabel("Number of Papers", fontsize=10)
    ax.set_title("Primary Area Distribution", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)
    ax.invert_yaxis()

    # 添加数值标签
    for i, v in enumerate(counts.values):
        ax.text(v + 5, i, str(v), va='center', fontsize=7, color=COLORS['dark'])


def plot_reply_count(df: pd.DataFrame, ax):
    """绘制 ReplyCount 分布图"""
    data = df["replyCount"].dropna()
    mean_val, median_val = data.mean(), data.median()

    print(f"ReplyCount 统计:")
    print(f"  最小值: {data.min()}, 最大值: {data.max()}")
    print(f"  平均值: {mean_val:.2f}, 中位数: {median_val}\n")

    ax.hist(data, bins=30, color=COLORS['orange'], edgecolor='white', alpha=0.85)
    ax.axvline(mean_val, color=COLORS['accent'], linestyle='--', linewidth=2, label=f"Mean: {mean_val:.1f}")
    ax.axvline(median_val, color=COLORS['secondary'], linestyle='--', linewidth=2, label=f"Median: {median_val:.1f}")
    ax.set_xlabel("Reply Count", fontsize=10)
    ax.set_ylabel("Number of Papers", fontsize=10)
    ax.set_title("Reply Count Distribution", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)
    ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=9)


def plot_submission_order(df: pd.DataFrame, ax):
    """绘制投稿顺序分布图"""
    data = df["number"].dropna()
    mean_val, median_val = data.mean(), data.median()

    print(f"Number (投稿顺序) 统计:")
    print(f"  最小值: {data.min()}, 最大值: {data.max()}")
    print(f"  平均值: {mean_val:.2f}, 中位数: {median_val}\n")

    ax.hist(data, bins=50, color=COLORS['purple'], edgecolor='white', alpha=0.85)
    ax.axvline(mean_val, color=COLORS['accent'], linestyle='--', linewidth=2, label=f"Mean: {mean_val:.0f}")
    ax.axvline(median_val, color=COLORS['secondary'], linestyle='--', linewidth=2, label=f"Median: {median_val:.0f}")
    ax.set_xlabel("Submission Number (smaller = earlier)", fontsize=10)
    ax.set_ylabel("Number of Accepted Papers", fontsize=10)
    ax.set_title("Submission Order vs Acceptance", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)
    ax.legend(frameon=True, fancybox=True, shadow=True, fontsize=9)


def plot_acceptance_rate_by_area(df: pd.DataFrame, ax):
    """绘制各 primary_area 的中稿率"""
    area_stats = df.groupby('primary_area').agg(
        total=('accepted_flag', 'count'),
        accepted=('accepted_flag', 'sum')
    ).reset_index()
    area_stats['acceptance_rate'] = area_stats['accepted'] / area_stats['total'] * 100
    area_stats = area_stats.sort_values('acceptance_rate', ascending=True)

    # 使用红绿渐变色表示中稿率高低
    norm_rates = area_stats['acceptance_rate'] / 100
    colors = plt.cm.RdYlGn(0.2 + 0.6 * norm_rates)

    ax.barh(range(len(area_stats)), area_stats['acceptance_rate'], color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(area_stats)))
    ax.set_yticklabels(area_stats['primary_area'], fontsize=6)
    ax.set_xlabel("Acceptance Rate (%)", fontsize=10)
    ax.set_title("Acceptance Rate by Primary Area", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)

    # 添加数值标签
    for i, (rate, total) in enumerate(zip(area_stats['acceptance_rate'], area_stats['total'])):
        ax.text(rate + 0.3, i, f'{rate:.1f}%', va='center', fontsize=6, color=COLORS['dark'])

    ax.set_xlim(0, max(area_stats['acceptance_rate']) * 1.15)


def plot_acceptance_rate_by_rating(df: pd.DataFrame, ax):
    """绘制不同评分区间的中稿率"""
    df_valid = df[df['avg_rating'].notna()].copy()

    # 创建评分区间
    bins = [0, 3, 4, 5, 6, 7, 8, 10]
    labels = ['0-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8+']
    df_valid['rating_bin'] = pd.cut(df_valid['avg_rating'], bins=bins, labels=labels)

    # 统计各区间的中稿率
    bin_stats = df_valid.groupby('rating_bin', observed=True).agg(
        total=('accepted_flag', 'count'),
        accepted=('accepted_flag', 'sum')
    ).reset_index()
    bin_stats['acceptance_rate'] = bin_stats['accepted'] / bin_stats['total'] * 100

    # 使用红绿渐变色
    norm_rates = bin_stats['acceptance_rate'] / 100
    colors = plt.cm.RdYlGn(0.2 + 0.6 * norm_rates)

    ax.bar(range(len(bin_stats)), bin_stats['acceptance_rate'], color=colors, edgecolor='white', linewidth=1)
    ax.set_xticks(range(len(bin_stats)))
    ax.set_xticklabels(bin_stats['rating_bin'], fontsize=10)
    ax.set_xlabel("Average Rating Range", fontsize=10)
    ax.set_ylabel("Acceptance Rate (%)", fontsize=10)
    ax.set_title("Acceptance Rate by Rating Range", fontsize=14, fontweight="bold", color=COLORS['dark'], pad=10)

    # 添加数值标签
    for i, (rate, total) in enumerate(zip(bin_stats['acceptance_rate'], bin_stats['total'])):
        ax.text(i, rate + 2, f'{rate:.1f}%', ha='center', fontsize=9, fontweight='bold', color=COLORS['dark'])
        ax.text(i, rate - 5, f'n={total}', ha='center', fontsize=7, color='white')

    ax.set_ylim(0, 110)


def analyze_submission_order(df: pd.DataFrame, n_bins: int = 10):
    """深入分析投稿顺序与接收的关系"""
    print("=" * 60)
    print("投稿顺序分析 (Number 越小表示投稿越早)")
    print("=" * 60)

    df_sorted = df.sort_values("number").copy()
    df_sorted["bin"] = pd.cut(df_sorted["number"], bins=n_bins, labels=False)
    bin_ranges = pd.cut(df_sorted["number"], bins=n_bins).value_counts().sort_index()

    print("\n按投稿顺序分组的接收论文数量:")
    for i, (interval, count) in enumerate(bin_ranges.items()):
        print(f"  区间 {i+1} ({interval}): {count} 篇")

    print("\n各区间平均 replyCount:")
    for i in range(n_bins):
        bin_data = df_sorted[df_sorted["bin"] == i]
        if len(bin_data) > 0:
            print(f"  区间 {i+1}: {bin_data['replyCount'].mean():.2f}")


def print_acceptance_stats(df: pd.DataFrame):
    """打印中稿率统计信息"""
    print("\n" + "=" * 60)
    print("中稿率统计分析")
    print("=" * 60)

    total = len(df)
    accepted = df['accepted_flag'].sum()
    overall_rate = accepted / total * 100
    print(f"\n总体中稿率: {overall_rate:.2f}% ({accepted}/{total})")

    # 各领域中稿率排名
    print("\n各领域中稿率排名 (从高到低):")
    area_stats = df.groupby('primary_area').agg(
        total=('accepted_flag', 'count'),
        accepted=('accepted_flag', 'sum')
    ).reset_index()
    area_stats['rate'] = area_stats['accepted'] / area_stats['total'] * 100
    area_stats = area_stats.sort_values('rate', ascending=False)

    for _, row in area_stats.iterrows():
        print(f"  {row['primary_area']}: {row['rate']:.1f}% ({row['accepted']}/{row['total']})")

    # 评分统计
    print("\n评分与中稿关系:")
    df_valid = df[df['avg_rating'].notna()]
    accepted_avg = df_valid[df_valid['accepted_flag']]['avg_rating'].mean()
    rejected_avg = df_valid[~df_valid['accepted_flag']]['avg_rating'].mean()
    print(f"  已接受论文平均评分: {accepted_avg:.2f}")
    print(f"  已拒绝论文平均评分: {rejected_avg:.2f}")


def main():
    # 加载数据
    df = load_data("iclr26_all_papers.csv")
    df_all = load_ratings_data("iclr26_all_papers_with_ratings.json")

    # 创建 3x2 图表
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    fig.suptitle('ICLR 2026 Paper Analysis', fontsize=18, fontweight='bold', color=COLORS['dark'], y=0.98)

    # 第一行：Primary Area 分布 + 词云
    plot_primary_area(df, axes[0, 0])
    plot_keywords_wordcloud(df, axes[0, 1])

    # 第二行：Reply Count + 投稿顺序
    plot_reply_count(df, axes[1, 0])
    plot_submission_order(df, axes[1, 1])

    # 第三行：中稿率相关
    plot_acceptance_rate_by_area(df_all, axes[2, 0])
    plot_acceptance_rate_by_rating(df_all, axes[2, 1])

    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.subplots_adjust(hspace=0.3, wspace=0.25)
    plt.savefig("images/iclr26_analysis.png", dpi=150, bbox_inches="tight", facecolor='white')
    plt.show()

    # 深入分析
    analyze_submission_order(df)
    print_acceptance_stats(df_all)


if __name__ == "__main__":
    main()
