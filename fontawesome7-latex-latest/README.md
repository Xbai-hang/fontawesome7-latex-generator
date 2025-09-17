# FontAwesome 7.0.1 LaTeX Package

Auto-generated LaTeX package for FontAwesome 7.0.1 with 2089 icons.

## Installation

1. Copy the `fontawesome7.sty` file to your LaTeX project directory
2. Copy the `fonts/` directory to your project
3. Compile with XeLaTeX or LuaLaTeX (required for fontspec)

## Usage

```latex
\documentclass{article}
\usepackage{fontawesome7}

\begin{document}
\far{house} House icon
\fas{star} Solid star
\fab{github} GitHub brand icon
\end{document}
```

## Commands

- `\far{icon-name}` - Regular style icon
- `\fas{icon-name}` - Solid style icon  
- `\fab{icon-name}` - Brands style icon

## Compilation

This package requires XeTeX or LuaTeX:

```bash
xelatex example.tex
# or
lualatex example.tex
```

## Files Generated

- `fontawesome7.sty` - Main package file
- `fonts/` - Font files directory
- `example.tex` - Example document
- `README.md` - This file

Generated on: 2025-09-17 21:59:27
