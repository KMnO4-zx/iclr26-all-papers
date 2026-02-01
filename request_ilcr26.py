import requests
import json
import time
import csv
from typing import List, Dict, Optional, Union
from urllib.parse import urlencode

try:
    from tqdm import tqdm
except ImportError:
    print("提示: 安装 tqdm 库以获得进度条显示: pip install tqdm")
    # 创建假的 tqdm 函数
    def tqdm(iterable, **kwargs):
        return iterable

# API 配置
API_BASE_URL = "https://api2.openreview.net/notes"
LIMIT = 25  # 每页论文数量
INITIAL_DELAY = 0.0  # 初始请求延迟（秒）


PAPER_VENUE = "ICLR 2026"  # 已接收论文的 venue 标识

# API 请求参数配置
API_PARAMS = {
    "content.venue": PAPER_VENUE,
    "details": "replyCount,presentation,writable",
    "domain": "ICLR.cc/2026/Conference",
    "invitation": "ICLR.cc/2026/Conference/-/Submission",
    "limit": LIMIT
    # "offset" 参数会在请求时动态添加
}

# 请求头
HEADERS = {
    "Accept": "application/json,text/*;q=0.99",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://openreview.net/",
    "Origin": "https://openreview.net"
}


class ICLR26Crawler:
    """ICLR 2026 Papers Crawler"""

    def __init__(self, limit: int = 25, delay: float = 0.8):
        """
        初始化爬虫

        Args:
            limit: 每页获取的论文数量
            delay: API请求延迟时间（秒）
        """
        self.limit = limit
        self.delay = delay
        self.total_papers = 0
        self.output_file = ""

    def construct_api_url(self, offset: int = 0) -> str:
        """
        构建API请求URL

        Args:
            offset: 分页偏移量

        Returns:
            完整的API URL
        """
        # 使用 API_PARAMS 配置，并动态添加 offset 参数
        params = API_PARAMS.copy()
        params["offset"] = offset
        params["limit"] = self.limit  # 使用实例的 limit 值
        return f"{API_BASE_URL}?{urlencode(params)}"

    def fetch_page(self, offset: int) -> Optional[Dict]:
        """
        获取指定分页的数据

        Args:
            offset: 分页偏移量

        Returns:
            API响应数据或None（请求失败时）
        """
        url = self.construct_api_url(offset)

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 如果是第一页，获取总数
            if offset == 0:
                self.total_papers = data.get("count", 0)

            return data

        except requests.exceptions.RequestException as e:
            print(f"\n❌ 请求失败 (offset={offset}): {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败 (offset={offset}): {e}")
            return None
        except Exception as e:
            print(f"\n❌ 未知错误 (offset={offset}): {e}")
            return None

    def extract_paper_info(self, paper: Union[Dict, object]) -> Dict:
        """
        从论文对象中提取所需信息

        Args:
            paper: 论文对象

        Returns:
            包含提取的信息的字典
        """
        paper_data = {}
        content = paper.get("content", {})

        # 基本信息
        paper_data["id"] = paper.get("id", "")
        paper_data["number"] = paper.get("number")

        # title
        title = content.get("title", {})
        paper_data["title"] = title.get("value", "") if isinstance(title, dict) else (title or "")

        # abstract
        abstract = content.get("abstract", {})
        paper_data["abstract"] = abstract.get("value", "") if isinstance(abstract, dict) else (abstract or "")

        # keywords
        keywords = content.get("keywords", {})
        keywords_list = keywords.get("value", []) if isinstance(keywords, dict) else (keywords if isinstance(keywords, list) else [])
        paper_data["keywords"] = " ".join(keywords_list)

        # primary_area
        primary_area = content.get("primary_area", {})
        paper_data["primary_area"] = primary_area.get("value", "") if isinstance(primary_area, dict) else (primary_area or "")

        # PDF URL
        paper_data["pdf_url"] = f"https://openreview.net/attachment?id={paper_data['id']}&name=pdf" if paper_data["id"] else ""

        # OpenReview URL
        paper_data["openreview_url"] = f"https://openreview.net/forum?id={paper_data['id']}" if paper_data["id"] else ""

        # replyCount
        details = paper.get("details", {})
        paper_data["replyCount"] = details.get("replyCount", 0) if details else 0

        return paper_data

    def process_response(self, data: Dict) -> List[Dict]:
        """
        处理API响应数据，提取论文列表

        Args:
            data: API响应数据

        Returns:
            论文信息列表
        """
        papers = []
        notes = data.get("notes", [])

        for paper in notes:
            paper_info = self.extract_paper_info(paper)
            papers.append(paper_info)

        return papers

    def fetch_all_papers(self) -> List[Dict]:
        """
        获取所有论文数据

        Returns:
            所有论文的信息列表
        """
        all_papers = []
        offset = 0
        successful_requests = 0
        failed_requests = 0

        print("=" * 60)
        print(" ICLR 2026 Papers Crawler")
        print("=" * 60)
        print(f"论文类型: {API_PARAMS.get('content.venue')}")
        print("输出格式: JSON + CSV")
        print("-" * 60)
        print("🔍 正在获取第一批数据以确定总数量...")

        # 第一页请求
        first_page = self.fetch_page(offset)
        if not first_page:
            print("❌ 无法获取第一批数据，请检查网络连接或API状态")
            return []

        print(f"✅ 发现 {self.total_papers} 篇论文")

        if self.total_papers == 0:
            print("⚠️ 未找到任何论文")
            return []

        total_pages = (self.total_papers + self.limit - 1) // self.limit

        print(f"📄 需要获取 {total_pages} 页数据 (每页 {self.limit} 篇)")
        print("⏳ 开始获取数据...")
        print("-" * 60)

        try:
            from tqdm import tqdm
            use_tqdm = True
        except ImportError:
            use_tqdm = False

        if use_tqdm:
            pbar = tqdm(total=self.total_papers, desc="获取进度", unit="paper")
        else:
            pbar = None

        current_count = 0

        # 处理第一页数据
        papers = self.process_response(first_page)
        all_papers.extend(papers)
        successful_requests += 1
        current_count += len(papers)

        if pbar:
            pbar.update(len(papers))
        else:
            print(f"  进度: {current_count}/{self.total_papers} 篇")

        offset += self.limit

        # 处理剩余页面
        while offset < self.total_papers:
            page_data = self.fetch_page(offset)

            if page_data:
                papers = self.process_response(page_data)
                all_papers.extend(papers)
                successful_requests += 1
                current_count += len(papers)

                if pbar:
                    pbar.update(len(papers))
                else:
                    print(f"  进度: {current_count}/{self.total_papers} 篇")
            else:
                failed_requests += 1
                print(f"\n⚠️  跳过 offset={offset} (请求失败)")

            offset += self.limit
            time.sleep(min(self.delay + offset * 0.0001, 2.0))

        if pbar:
            pbar.close()

        print("-" * 60)
        print(f"✅ 数据获取完成!")
        print(f"   - 成功: {successful_requests} 页")
        print(f"   - 失败: {failed_requests} 页")
        print(f"   - 总计: {len(all_papers)} / {self.total_papers} 篇论文")

        return all_papers

    def save_as_json(self, papers: List[Dict]) -> None:
        """
        保存数据为 JSON 格式

        Args:
            papers: 论文数据列表
        """
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(papers, f, indent=2, ensure_ascii=False)
            print(f"💾 JSON 文件已保存: {self.output_file}")
            print(f"   文件大小: {len(json.dumps(papers)) / 1024:.2f} KB")
        except Exception as e:
            print(f"❌ 保存 JSON 文件失败: {e}")

    def save_as_csv(self, papers: List[Dict]) -> None:
        """
        保存数据为 CSV 格式

        Args:
            papers: 论文数据列表
        """
        if not papers:
            print("⚠️ 没有数据可保存")
            return

        try:
            fieldnames = [
                "id", "number", "title", "abstract",
                "keywords", "primary_area", "pdf_url", "openreview_url", "replyCount"
            ]

            with open(self.output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for paper in papers:
                    writer.writerow(paper)

            print(f"💾 CSV 文件已保存: {self.output_file}")

            # 计算文件大小
            import os
            file_size = os.path.getsize(self.output_file)
            print(f"   文件大小: {file_size / 1024:.2f} KB")

        except Exception as e:
            print(f"❌ 保存 CSV 文件失败: {e}")

    def save_data(self, papers: List[Dict]) -> None:
        """
        保存数据为 JSON 和 CSV 两种格式

        Args:
            papers: 论文数据列表
        """
        # 保存 JSON
        self.output_file = "iclr26_all_papers.json"
        self.save_as_json(papers)

        # 保存 CSV
        self.output_file = "iclr26_all_papers.csv"
        self.save_as_csv(papers)


def main():
    """主函数"""

    try:
        # 创建爬虫实例
        crawler = ICLR26Crawler(limit=LIMIT, delay=INITIAL_DELAY)

        # 获取所有论文
        papers = crawler.fetch_all_papers()

        if papers:
            # 保存数据
            crawler.save_data(papers)
            print("-" * 60)
            print("✨ 所有任务完成!")
            print("=" * 60)
        else:
            print("⚠️ 未获取到任何数据")
            return 1

    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
        print("⚠️ 部分数据可能已获取但未保存")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())