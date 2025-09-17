# FontAwesome7 LaTeX Package Generator

🎨 **自动生成最新版本的 FontAwesome LaTeX 包**

## 🚀 Quick Start

### 1. 在 LaTeX 中使用

```latex
\documentclass{article}
\usepackage{fontawesome7}

\begin{document}

\begin{itemize}
    \item \far{house} House
    \item \far{user} User  
    \item \far{envelope} Email
    \item \fas{phone} Phone (The free plan does not include the regular phone icon)
    \item \far{calendar} Calendar
\end{itemize}

\end{document}
```

### 2. 编译文档

```bash
xelatex document.tex
# 或者
lualatex document.tex
```

## 🔧 本地运行

如果你想在本地运行生成脚本：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行脚本
python generator.py
```

## 📄 许可证

本项目采用 MIT 许可证。FontAwesome 字体和图标遵循其官方许可证。

## 🔗 相关链接

- [FontAwesome 官方网站](https://fontawesome.com/)
- [FontAwesome GitHub](https://github.com/FortAwesome/Font-Awesome)
- [LaTeX FontSpec 文档](https://ctan.org/pkg/fontspec)

## 🤝 特别鸣谢

- Claude Sonnet 4

---

⭐ 如果这个项目对你有帮助，请考虑给个 Star！