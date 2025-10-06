# FontAwesome 7 LaTeX Package Makefile
# Auto-generated on 2025-10-06 12:10:40

STY_FILE = fontawesome7.sty
FONT_FILES := $(wildcard fonts/*)

MAIN_TEX = example.tex
MAIN_PDF = example.pdf
LATEX_ENGINE = xelatex

.PHONY: all clean

# 默认目标
all: $(MAIN_PDF)

# 编译PDF
$(MAIN_PDF): $(MAIN_TEX) $(STY_FILE) $(FONT_FILES)
	$(LATEX_ENGINE) $(MAIN_TEX)

# 清理临时文件
clean:
	rm -f *.aux *.log *.out *.synctex.gz *.fls *.fdb_latexmk
