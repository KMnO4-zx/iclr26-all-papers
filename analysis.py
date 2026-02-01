import re
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 设置字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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


def plot_keywords_wordcloud(df: pd.DataFrame, ax):
    """绘制关键词词云图"""
    all_keywords = " ".join(df["keywords"].dropna().astype(str))
    wc = WordCloud(
        width=800, height=400,
        background_color="white",
        max_words=200,
        colormap="viridis",
        stopwords=STOPWORDS
    ).generate(all_keywords)

    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Keywords Word Cloud", fontsize=14, fontweight="bold")


def plot_primary_area(df: pd.DataFrame, ax):
    """绘制 Primary Area 分布图"""
    def process_area(area):
        if pd.isna(area):
            return []
        area = re.sub(r'\([^)]*\)', '', str(area))
        return [a.strip() for a in area.split(',') if a.strip()]

    all_areas = []
    for area in df["primary_area"]:
        all_areas.extend(process_area(area))

    counts = pd.Series(all_areas).value_counts()
    print("Primary Area 分布:")
    print(counts, "\n")

    ax.barh(range(len(counts)), counts.values, color="steelblue")
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, fontsize=8)
    ax.set_xlabel("Number of Papers")
    ax.set_title("Primary Area Distribution", fontsize=14, fontweight="bold")
    ax.invert_yaxis()


def plot_reply_count(df: pd.DataFrame, ax):
    """绘制 ReplyCount 分布图"""
    data = df["replyCount"].dropna()
    mean_val, median_val = data.mean(), data.median()

    print(f"ReplyCount 统计:")
    print(f"  最小值: {data.min()}, 最大值: {data.max()}")
    print(f"  平均值: {mean_val:.2f}, 中位数: {median_val}\n")

    ax.hist(data, bins=30, color="coral", edgecolor="black", alpha=0.7)
    ax.axvline(mean_val, color="red", linestyle="--", label=f"Mean: {mean_val:.1f}")
    ax.axvline(median_val, color="green", linestyle="--", label=f"Median: {median_val:.1f}")
    ax.set_xlabel("Reply Count")
    ax.set_ylabel("Number of Papers")
    ax.set_title("Reply Count Distribution", fontsize=14, fontweight="bold")
    ax.legend()


def plot_submission_order(df: pd.DataFrame, ax):
    """绘制投稿顺序分布图"""
    data = df["number"].dropna()
    mean_val, median_val = data.mean(), data.median()

    print(f"Number (投稿顺序) 统计:")
    print(f"  最小值: {data.min()}, 最大值: {data.max()}")
    print(f"  平均值: {mean_val:.2f}, 中位数: {median_val}\n")

    ax.hist(data, bins=50, color="mediumpurple", edgecolor="black", alpha=0.7)
    ax.axvline(mean_val, color="red", linestyle="--", label=f"Mean: {mean_val:.0f}")
    ax.axvline(median_val, color="green", linestyle="--", label=f"Median: {median_val:.0f}")
    ax.set_xlabel("Submission Number (smaller = earlier)")
    ax.set_ylabel("Number of Accepted Papers")
    ax.set_title("Submission Order vs Acceptance", fontsize=14, fontweight="bold")
    ax.legend()


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


def main():
    # 加载数据
    df = load_data("iclr26_all_papers.csv")

    # 创建 2x2 图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 绘制四个图表
    plot_keywords_wordcloud(df, axes[0, 0])
    plot_primary_area(df, axes[0, 1])
    plot_reply_count(df, axes[1, 0])
    plot_submission_order(df, axes[1, 1])

    # 保存并显示
    plt.tight_layout()
    plt.savefig("images/iclr26_analysis.png", dpi=150, bbox_inches="tight")
    plt.show()

    # 深入分析
    analyze_submission_order(df)


if __name__ == "__main__":
    main()
