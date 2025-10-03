# -*- coding: utf-8 -*-
# Reproduce: "Difference from Human Baseline (Sorted by Average, Nature-style Labels)"
# Requirements: pandas, seaborn, matplotlib
#   pip install pandas seaborn matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ========= 1) 路径与读取 =========
csv_path = Path("final_summary_avg_scores_human_merge.csv")  # 修改为你的实际路径
df = pd.read_csv(csv_path)

# ========= 2) 以 Human 为基线计算差值，并添加 Average =========
heatmap_data = df.set_index("Physician")
if "Human" not in heatmap_data.index:
    raise ValueError("未找到 'Human' 行，请确认 CSV 中的 Physician 列包含 Human。")

diff = heatmap_data - heatmap_data.loc["Human"]
diff["Average"] = diff.mean(axis=1)

# ========= 3) 按 Average 从高到低排序 =========
diff_sorted = diff.sort_values(by="Average", ascending=False)

# ========= 4) 控制标注精度：Average 4 位，其余 2 位 =========
formatted = diff_sorted.copy()
for col in formatted.columns:
    if col == "Average":
        formatted[col] = formatted[col].map(lambda x: f"{x:.4f}")
    else:
        formatted[col] = formatted[col].map(lambda x: f"{x:.2f}")

# ========= 5) 作图 =========
plt.figure(figsize=(13, 8))
ax = sns.heatmap(
    diff_sorted,
    annot=formatted,      # 用字符串控制精度
    fmt="",
    center=0,
    cmap="bwr",
    linewidths=0.5, linecolor="gray",
    cbar_kws={"label": "Score Difference vs Human"}
)

# plt.title(
#     "Difference from Human Baseline (Sorted by Average, Nature-style Labels)",
#     fontsize=14, pad=15
# )
# plt.xlabel("Evaluation Category + Average", fontsize=12)
# plt.ylabel("Physician/Model (sorted by Average difference)", fontsize=12)

# 横轴标签轻微倾斜（类似 Nature 图风）
plt.xticks(rotation=30, ha="right", fontsize=11)
plt.yticks(fontsize=11)

# 加粗纵轴的 Human 标签
yticklabels = ax.get_yticklabels()
for lab in yticklabels:
    if lab.get_text() == "Human":
        lab.set_weight("bold")
ax.set_yticklabels(yticklabels)

plt.tight_layout()

# ========= 6) 保存 PNG + SVG =========
png_path = Path("human_baseline_diff_heatmap.png")
svg_path = Path("human_baseline_diff_heatmap.svg")

plt.savefig(png_path, dpi=300, bbox_inches="tight")          # 位图（投稿/报告常用）
plt.savefig(svg_path, format="svg", bbox_inches="tight")     # 矢量图（排版/放大更清晰）

print(f"Figure saved to: {png_path.resolve()}")
print(f"Figure saved to: {svg_path.resolve()}")

plt.show()
