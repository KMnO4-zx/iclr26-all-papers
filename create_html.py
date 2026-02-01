#!/usr/bin/env python3
"""
创建 ICLR 2026 论文的 HTML 页面
从 iclr26_all_papers.csv 读取数据
"""

import pandas as pd


def create_papers_html():
    """创建论文列表的HTML页面"""

    # 读取论文数据
    df = pd.read_csv('iclr26_all_papers.csv')
    papers_data = df.to_dict('records')

    # 创建HTML内容
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICLR 2026 Accepted Papers</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #2c3e50;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #3498db;
        }}

        .header h1 {{
            font-size: 2.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header .subtitle {{
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-bottom: 15px;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section-title {{
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
            font-weight: 600;
        }}

        .section-count {{
            color: #7f8c8d;
            font-size: 1rem;
            font-weight: normal;
        }}

        .paper-card {{
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            page-break-inside: avoid;
        }}

        .paper-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            line-height: 1.3;
        }}

        .paper-authors {{
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }}

        .paper-keywords {{
            color: #3498db;
            font-size: 0.85rem;
            margin-bottom: 8px;
        }}

        .paper-area {{
            color: #27ae60;
            font-size: 0.85rem;
            margin-bottom: 10px;
        }}

        .paper-abstract {{
            color: #2c3e50;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 12px;
            text-align: justify;
        }}

        .paper-link {{
            display: inline-block;
            padding: 6px 12px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: background-color 0.3s ease;
            margin-right: 8px;
        }}

        .paper-link:hover {{
            background: #2980b9;
        }}

        .reply-count {{
            display: inline-block;
            padding: 4px 10px;
            background: #f39c12;
            color: white;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-left: 10px;
        }}

        .analysis-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .analysis-section h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}

        .analysis-image {{
            width: 80%;
            max-width: 80%;
            display: block;
            margin: 0 auto 20px auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .analysis-desc {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .analysis-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}

        .analysis-item h4 {{
            margin: 0 0 8px 0;
            color: #2c3e50;
        }}

        .analysis-item p {{
            margin: 0;
            color: #7f8c8d;
            font-size: 0.9rem;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}

        .download-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
            text-align: center;
        }}

        .download-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }}

        .download-btn:hover {{
            background: #229954;
        }}

        @media print {{
            body {{
                background: white !important;
                padding: 10px !important;
            }}

            .container {{
                box-shadow: none !important;
                padding: 10px !important;
            }}

            .paper-card {{
                break-inside: avoid;
                page-break-inside: avoid;
                margin-bottom: 10px !important;
                padding: 15px !important;
            }}

            .section {{
                page-break-before: always;
            }}

            .download-section {{
                display: none !important;
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .stats {{
                flex-direction: column;
                align-items: center;
            }}

            .paper-card {{
                padding: 15px;
            }}
        }}
    </style>
    <!-- Marked.js for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- MathJax for LaTeX rendering -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }},
            svg: {{
                fontCache: 'global'
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ICLR 2026 Accepted Papers</h1>
            <div class="subtitle">共 {len(papers_data)} 篇论文</div>
        </div>

        <div class="analysis-section">
            <h2>📊 数据分析概览</h2>
            <img src="images/iclr26_analysis.png" alt="ICLR 2026 Analysis" class="analysis-image">
            <div class="analysis-desc">
                <div class="analysis-item">
                    <h4>Keywords Word Cloud（左上）</h4>
                    <p>关键词词云图，展示论文关键词的词频分布，词越大表示出现频率越高</p>
                </div>
                <div class="analysis-item">
                    <h4>Primary Area Distribution（右上）</h4>
                    <p>各研究领域的论文数量分布，展示不同研究方向的热度</p>
                </div>
                <div class="analysis-item">
                    <h4>Reply Count Distribution（左下）</h4>
                    <p>论文回复数分布直方图，红线为均值，绿线为中位数</p>
                </div>
                <div class="analysis-item">
                    <h4>Submission Order vs Acceptance（右下）</h4>
                    <p>投稿顺序与接收论文的关系，number 越小表示投稿越早</p>
                </div>
            </div>
        </div>
'''

    # 添加论文列表
    html_content += f'''
        <div class="section">
            <h2 class="section-title">
                论文列表 <span class="section-count">({len(papers_data)}篇)</span>
            </h2>
'''

    for i, paper in enumerate(papers_data):
        title = paper['title']
        abstract = paper['abstract']
        keywords = paper.get('keywords', '')
        primary_area = paper.get('primary_area', '')
        reply_count = paper.get('replyCount', 0)
        openreview_url = paper.get('openreview_url', '')
        pdf_url = paper.get('pdf_url', '')

        html_content += f'''
            <div class="paper-card">
                <div class="paper-title">{i+1}. {title}
                    <span class="reply-count">💬 {reply_count}</span>
                </div>
                <div class="paper-area">📁 {primary_area}</div>
                <div class="paper-keywords">🏷️ {keywords}</div>
                <div class="paper-abstract">{abstract}</div>
                <a href="{openreview_url}" class="paper-link" target="_blank">📄 OpenReview</a>
                <a href="{pdf_url}" class="paper-link" target="_blank">📄 PDF</a>
            </div>
        '''

    html_content += '''
        </div>

        <div class="footer">
            <p><strong>ICLR 2026 Accepted Papers</strong></p>
            <p>数据来源: OpenReview</p>
        </div>
    </div>

    <script>
        // Render markdown in all abstract elements
        document.querySelectorAll('.paper-abstract').forEach(function(el) {
            el.innerHTML = marked.parse(el.textContent);
        });
    </script>
</body>
</html>'''

    # 保存HTML文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML页面已创建: index.html")
    print(f"共 {len(papers_data)} 篇论文")

    return 'index.html'


if __name__ == "__main__":
    create_papers_html()