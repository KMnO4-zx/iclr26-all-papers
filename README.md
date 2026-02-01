# ICLR 2026 Accepted Papers Simple Analysis

<div align="center">

[中文版](README_CN.md) | English

</div>

This repository contains all accepted papers from ICLR 2026, along with analysis scripts and visualizations.

![Overview Analysis](images/iclr26_analysis.png)

---

## Quick Start

### 1. Fetch All Papers

Run the following command to fetch all accepted papers from OpenReview:

```bash
pip install requests tqdm
python request_ilcr26.py
```

This will generate:
- `iclr26_all_papers.json` - All papers in JSON format
- `iclr26_all_papers.csv` - All papers in CSV format

### 2. Run Analysis

```bash
pip install pandas matplotlib wordcloud
python analysis.py
python deep_analysis.py
```

---

## Analysis Results

### Deep Analysis

#### 1. Text Analysis

![Text Analysis](images/deep_analysis_1_text.png)

- Title length distribution (word count)
- Abstract length distribution (word count)
- Hot topics frequency in titles (LLM, Diffusion, Reinforcement, etc.)
- Title length vs Abstract length correlation

#### 2. Keyword Analysis

![Keyword Analysis](images/deep_analysis_2_keywords.png)

- Top 20 most frequent keywords
- Top 15 keyword co-occurrence pairs

#### 3. Area Analysis

![Area Analysis](images/deep_analysis_3_areas.png)

- Number of papers by research area
- Average reply count by research area

#### 4. Correlation Analysis

![Correlation Analysis](images/deep_analysis_4_correlation.png)

- Title length vs Reply count
- Abstract length vs Reply count
- Submission order vs Reply count
- Hot words in title vs Reply count

---

## Feedback

If you find this analysis helpful, please leave a star or say thanks in the [Issues](../../issues)! Your support means a lot to me.

---

## Citation

If you use this repository in your research, please cite it as:

```bibtex
@misc{iclr2026analysis,
  author       = {kmno4-zx},
  title        = {ICLR 2026 Papers Simple Analysis},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/kmno4-zx/iclr26-all-papers}}
}
```

---

## License

Apache License 2.0
