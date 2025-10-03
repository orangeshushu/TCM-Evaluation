import matplotlib.pyplot as plt

# ======================
# 1) 数据（最后一类为 Brain Disorders）
# ======================
departments = [
    "General TCM",
    "Pediatrics",
    "Tuina",
    "Acupuncture",
    "Gastroenterology",
    "Otolaryngology (ENT)",
    "Endocrinology",
    "Neurology",
    "Pulmonology",
    "Brain Disorders",
]
counts = [22, 11, 10, 8, 3, 2, 1, 1, 1, 1]

# ======================
# 2) 按人数从大到小排序（保持部门与人数对应）
# ======================
pairs = sorted(zip(counts, departments), reverse=True)
sorted_counts, sorted_departments = zip(*pairs)

# ======================
# 3) 作图（Nature-like 极简风格）
# ======================
plt.figure(figsize=(9, 6))

# 单色低饱和蓝（与前图一致）
bar_color = "#4C78A8"
bars = plt.barh(sorted_departments, sorted_counts, color=bar_color, alpha=0.9)

# 在条形末端标注人数
for bar, c in zip(bars, sorted_counts):
    plt.text(c + 0.2, bar.get_y() + bar.get_height()/2,
             f"{c}", va="center", fontsize=10)

# 轴标签（无标题）
plt.xlabel("Number of clinicians", fontsize=10)
plt.ylabel("Department", fontsize=12)
plt.yticks(fontsize=12)

# 轴与网格的细节（去掉上/右脊，横向虚线网格）
ax = plt.gca()
ax.tick_params(axis="both", which="both", direction="out", length=4, width=0.8)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_linewidth(1.0)
ax.xaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.35)
ax.set_axisbelow(True)

plt.tight_layout()

# ======================
# 4) 导出文件
# ======================
# 矢量图（论文友好）
svg_path = "department_distribution_brain_disorders_clinicians.svg"
plt.savefig(svg_path, format="svg")

# 如需位图（可选）
# png_path = "department_distribution_brain_disorders_clinicians.png"
# plt.savefig(png_path, dpi=300)

plt.close()
print(f"Saved SVG to: {svg_path}")
# print(f"Saved PNG to: {png_path}")
