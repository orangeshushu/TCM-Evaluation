import matplotlib.pyplot as plt

# 数据
labels = ["Female (n=38)", "Male (n=22)"]
sizes = [38, 22]
colors = ["#fcbba1", "#9ecae1"]   # 柔和粉/蓝
total = sum(sizes)

# 画图（稍大，避免拥挤）
fig, ax = plt.subplots(figsize=(6.5, 6.5))

# 环形图
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct="%.1f%%",
    startangle=90,
    textprops={'fontsize': 12},
    wedgeprops=dict(width=0.4),
    labeldistance=1.06,     # 调近标签，避免溢出
    pctdistance=0.75        # 百分比位置（在环里）
)

# 中心文本
ax.text(0, 0, f"Total N = {total}", ha="center", va="center", fontsize=13)

# 标题（可去掉）
# ax.set_title("Gender Composition of Participants", fontsize=14, pad=14)

# 保持圆形
ax.set_aspect('equal')

# 显示（交互环境）
plt.tight_layout()

# —— 保存：使用 bbox_inches='tight' 防止裁切 ——
plt.savefig("gender_composition_300dpi.jpg", format="jpg", dpi=300,
            bbox_inches="tight", pad_inches=0.3)
plt.savefig("gender_composition.svg", format="svg",
            bbox_inches="tight", pad_inches=0.3)
plt.close()

print("Saved: gender_composition_300dpi.jpg (300 dpi) and gender_composition.svg")
