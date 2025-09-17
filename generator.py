#!/usr/bin/env python3
"""
FontAwesome LaTeX Generator

This script downloads the latest FontAwesome release, processes the font files,
and generates a LaTeX .sty package for easy icon usage.
"""

import sys
import json
import requests
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import re


class FontAwesomeGenerator:

    def __init__(self, output_dir="./fontawesome-latex"):
        self.output_dir = Path(output_dir)
        self.github_api_url = (
            "https://api.github.com/repos/FortAwesome/Font-Awesome/releases/latest"
        )
        self.temp_dir = Path("./.temp_fontawesome")

    def get_latest_release_info(self):
        """获取最新版本信息"""
        print("🔍 获取最新版本信息...")
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            data = response.json()

            version = data["tag_name"]
            print(f"📦 最新版本: {version}")

            # 查找 desktop 下载链接
            desktop_url = None
            for asset in data["assets"]:
                if "desktop" in asset["name"].lower() and asset["name"].endswith(
                    ".zip"
                ):
                    desktop_url = asset["browser_download_url"]
                    break

            if not desktop_url:
                raise ValueError("未找到 desktop 版本下载链接")

            return version, desktop_url

        except Exception as e:
            print(f"❌ 获取版本信息失败: {e}")
            sys.exit(1)

    def download_and_extract(self, download_url, version):
        """下载并解压文件"""
        print(f"📥 下载 {download_url}")

        # 创建临时目录
        self.temp_dir.mkdir(exist_ok=True)

        # 下载文件
        zip_path = self.temp_dir / f"fontawesome-{version}.zip"
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {percent:.1f}%", end="", flush=True)
            print()

        # 解压文件
        print("📂 解压文件...")
        extract_path = self.temp_dir / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # 查找解压后的主目录
        extracted_dirs = [d for d in extract_path.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise ValueError("解压后未找到目录")

        main_dir = extracted_dirs[0]  # 通常只有一个主目录
        return main_dir

    def process_font_files(self, main_dir):
        """处理字体文件，重命名去除空格"""
        print("🔤 处理字体文件...")

        otfs_dir = main_dir / "otfs"
        if not otfs_dir.exists():
            raise ValueError("未找到 otfs 目录")

        # 创建输出目录
        output_fonts_dir = self.output_dir / "fonts"
        output_fonts_dir.mkdir(parents=True, exist_ok=True)

        font_files = []
        for otf_file in otfs_dir.glob("*.otf"):
            # 重命名：去除空格
            new_name = otf_file.name.replace(" ", "")
            new_path = output_fonts_dir / new_name

            # 复制并重命名文件
            shutil.copy2(otf_file, new_path)
            font_files.append(
                {"original": otf_file.name, "renamed": new_name, "path": new_path}
            )
            print(f"   📄 {otf_file.name} -> {new_name}")

        return font_files

    def load_icons_metadata(self, main_dir):
        """加载图标元数据"""
        print("📋 加载图标元数据...")

        metadata_dir = main_dir / "metadata"
        icons_file = metadata_dir / "icons.json"

        if not icons_file.exists():
            raise ValueError("未找到 icons.json 文件")

        with open(icons_file, "r", encoding="utf-8") as f:
            icons_data = json.load(f)

        print(f"   📊 加载了 {len(icons_data)} 个图标定义")
        return icons_data

    def generate_sty_file(self, version, font_files, icons_data):
        """生成 LaTeX .sty 文件"""
        print("📝 生成 LaTeX .sty 文件...")

        # 提取版本号数字
        version_num = re.search(r"(\d+)", version)
        version_major = version_num.group(1) if version_num else "6"

        package_name = f"fontawesome{version_major}"
        sty_content = self._generate_sty_content(
            version, version_major, font_files, icons_data
        )

        # 写入 .sty 文件
        sty_file = self.output_dir / f"{package_name}.sty"
        with open(sty_file, "w", encoding="utf-8") as f:
            f.write(sty_content)

        print(f"   ✅ 生成 {sty_file}")
        return sty_file

    def _generate_sty_content(self, version, version_major, font_files, icons_data):
        """生成 .sty 文件内容"""
        global icon_count
        global current_datetime
        current_datetime = datetime.now()
        # 文件头
        content = f"""%%
%% FontAwesome {version} LaTeX Package
%% Auto-generated on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}
%%
%% This package provides easy access to FontAwesome {version} icons in LaTeX documents.
%% 
%% Usage:
%%   \\usepackage{{fontawesome{version_major}}}
%%   \\fab{{github}} % for brands icon github
%%   \\far{{user}} % for regular icon user
%%   \\fas{{user}} % for solid icon user
%%

\\NeedsTeXFormat{{LaTeX2e}}
\\ProvidesPackage{{fontawesome{version_major}}}[{current_datetime.strftime('%Y/%m/%d')} FontAwesome {version} icons]

%% Required packages
\\RequirePackage{{fontspec}}
\\RequirePackage{{xparse}}

%% Check for XeTeX or LuaTeX
\\@ifundefined{{XeTeXversion}}{{%
  \\@ifundefined{{directlua}}{{%
    \\PackageError{{fontawesome{version_major}}}{{%
      This package requires XeTeX or LuaTeX.\\MessageBreak
      Please compile with xelatex or lualatex.%
    }}{{}}%
  }}{{}}%
}}{{}}

%% Font definitions
"""
        # 定义字体
        for font in font_files:
            font_name = font["renamed"]
            if "Brands" in font_name:
                content += (
                    f"\\newfontfamily{{\\FABrands}}{{{font_name}}}[Path=fonts/]\n"
                )
            elif "Regular" in font_name:
                content += (
                    f"\\newfontfamily{{\\FARegular}}{{{font_name}}}[Path=fonts/]\n"
                )
            elif "Solid" in font_name:
                content += f"\\newfontfamily{{\\FASolid}}{{{font_name}}}[Path=fonts/]\n"
        content += """

%% Commands for displaying icons
\\newcommand*{\\fab}[1]{{\\FABrands\\csname fabicon@#1\\endcsname}}
\\newcommand*{\\far}[1]{{\\FARegular\\csname faricon@#1\\endcsname}}
\\newcommand*{\\fas}[1]{{\\FASolid\\csname fasicon@#1\\endcsname}}


%% Icon definitions
"""
        # 生成图标定义
        # 初始化三个空字典, 分类图标
        brands_icons = {}
        regular_icons = {}
        solid_icons = {}

        for icon_name, icon_data in icons_data.items():
            # 检查图标是否支持 Brands/Regular/Solid 风格
            has_brands = "brands" in icon_data["styles"]
            has_regular = "regular" in icon_data["styles"]
            has_solid = "solid" in icon_data["styles"]
            if has_brands:
                brands_icons[icon_name] = icon_data
            if has_regular:
                regular_icons[icon_name] = icon_data
            if has_solid:
                solid_icons[icon_name] = icon_data

        # Brands icons
        content += """
%% Brands icons definitions
"""
        for icon_name, icon_data in brands_icons.items():
            if "unicode" in icon_data:
                unicode_hex = icon_data["unicode"]
                # 定义基础图标字符
                content += f'\\expandafter\\def\\csname fabicon@{icon_name}\\endcsname {{\\symbol{{"{unicode_hex.upper()}}}}}\n'
        # Regular icons
        content += """
%% Regular icons definitions
"""
        for icon_name, icon_data in regular_icons.items():
            if "unicode" in icon_data:
                unicode_hex = icon_data["unicode"]
                # 定义基础图标字符
                content += f'\\expandafter\\def\\csname faricon@{icon_name}\\endcsname {{\\symbol{{"{unicode_hex.upper()}}}}}\n'
        # Regular icons
        content += """
%% Solid icons definitions
"""
        for icon_name, icon_data in solid_icons.items():
            if "unicode" in icon_data:
                unicode_hex = icon_data["unicode"]
                # 定义基础图标字符
                content += f'\\expandafter\\def\\csname fasicon@{icon_name}\\endcsname {{\\symbol{{"{unicode_hex.upper()}}}}}\n'
        icon_count = len(brands_icons) + len(regular_icons) + len(solid_icons)
        content += f"""
%% Package info
\\PackageInfo{{fontawesome{version_major}}}{{Loaded {icon_count} FontAwesome {version} icons}}

\\endinput
"""
        return content

    def generate_example_document(self, version_major):
        """生成示例文档"""
        print("📄 生成示例文档...")

        example_content = f"""\\documentclass{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{fontawesome{version_major}}}
\\usepackage{{xcolor}}
\\usepackage{{hyperref}}

\\hypersetup{{
    colorlinks=true,
    urlcolor=cyan
}}

\\title{{FontAwesome {version_major} LaTeX Package Example}}
\\author{{Auto-generated}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

You can get all free icons from \\href{{https://fontawesome.com/search?ic=free}}{{https://fontawesome.com/search?ic=free}}


\\section{{Basic Usage}}

Here are some basic icons:
\\begin{{itemize}}
    \\item \\far{{house}} House
    \\item \\far{{user}} User  
    \\item \\far{{envelope}} Email
    \\item \\fas{{phone}} Phone (The free plan does not include the regular phone icon)
    \\item \\far{{calendar}} Calendar
\\end{{itemize}}

\\section{{Different Styles}}

\\begin{{itemize}}
    \\item Regular: \\far{{star}} \\far{{heart}} \\far{{cloud}}
    \\item Solid: \\fas{{star}} \\fas{{heart}} \\fas{{cloud}}
    \\item Brands: \\fab{{github}} \\fab{{twitter}} \\fab{{linkedin}}
\\end{{itemize}}

\\section{{Colored Icons}}

\\begin{{itemize}}
    \\item Regular: \\textcolor{{red}}{{\\far{{heart}}}} \\textcolor{{blue}}{{\\far{{star}}}} \\textcolor{{green}}{{\\far{{cloud}}}}
    \\item Solid: \\textcolor{{red}}{{\\far{{heart}}}} \\textcolor{{blue}}{{\\far{{star}}}} \\textcolor{{green}}{{\\far{{cloud}}}}
    \\item Brands: \\textcolor{{red}}{{\\fab{{github}}}} \\textcolor{{blue}}{{\\fab{{twitter}}}} \\textcolor{{green}}{{\\fab{{linkedin}}}}
\\end{{itemize}}

\\section{{Contact Information Example}}

\\begin{{tabular}}{{ll}}
\\far{{envelope}} & example@gmail.com \\\\
\\fas{{phone}} & +1 (555) 123-4567 \\\\
\\far{{house}} & 123 Main St, City, State \\\\
\\fab{{github}} & github.com/example \\\\
\\fab{{linkedin}} & linkedin.com/in/example \\\\
\\end{{tabular}}

\\end{{document}}
"""
        example_file = self.output_dir / "example.tex"
        with open(example_file, "w", encoding="utf-8") as f:
            f.write(example_content)

        print(f"   ✅ 生成示例文档 {example_file}")

    def generate_readme(self, version, version_major):
        """生成 README 文件"""
        print("📖 生成 README...")

        readme_content = f"""# FontAwesome {version} LaTeX Package

Auto-generated LaTeX package for FontAwesome {version} with {icon_count} icons.

## Installation

1. Copy the `fontawesome{version_major}.sty` file to your LaTeX project directory
2. Copy the `fonts/` directory to your project
3. Compile with XeLaTeX or LuaLaTeX (required for fontspec)

## Usage

```latex
\\documentclass{{article}}
\\usepackage{{fontawesome{version_major}}}

\\begin{{document}}
\\far{{house}} House icon
\\fas{{star}} Solid star
\\fab{{github}} GitHub brand icon
\\end{{document}}
```

## Commands

- `\\far{{icon-name}}` - Regular style icon
- `\\fas{{icon-name}}` - Solid style icon  
- `\\fab{{icon-name}}` - Brands style icon

## Compilation

This package requires XeTeX or LuaTeX:

```bash
xelatex example.tex
# or
lualatex example.tex
```

## Files Generated

- `fontawesome{version_major}.sty` - Main package file
- `fonts/` - Font files directory
- `example.tex` - Example document
- `README.md` - This file

Generated on: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}
"""
        readme_file = self.output_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"   ✅ 生成 README {readme_file}")

    def generate_makefile(self, version_major, example_filename="example"):
        """生成 Makefile 文件"""
        print("🔨 生成 Makefile...")
        
        makefile_content = f"""# FontAwesome {version_major} LaTeX Package Makefile
# Auto-generated on {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}

STY_FILE = fontawesome{version_major}.sty
FONT_FILES := $(wildcard fonts/*)

MAIN_TEX = {example_filename}.tex
MAIN_PDF = {example_filename}.pdf
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
"""
        makefile_path = self.output_dir / "Makefile"
        with open(makefile_path, "w", encoding="utf-8") as f:
            f.write(makefile_content)
        
        print(f"   ✅ 生成 Makefile {makefile_path}")
        return makefile_path

    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 清理临时文件")

    def run(self):
        """运行主流程"""
        try:
            print("🚀 开始生成 FontAwesome LaTeX 包...\n")

            # 获取最新版本
            version, download_url = self.get_latest_release_info()

            # 下载并解压
            main_dir = self.download_and_extract(download_url, version)

            # 处理字体文件
            font_files = self.process_font_files(main_dir)

            # 加载图标元数据
            icons_data = self.load_icons_metadata(main_dir)

            # 生成 .sty 文件
            version_num = re.search(r"(\d+)", version)
            version_major = version_num.group(1) if version_num else "6"

            self.generate_sty_file(version, font_files, icons_data)

            # 生成示例和文档
            self.generate_example_document(version_major)
            self.generate_readme(version, version_major)

            # 生成 Makefile
            self.generate_makefile(version_major)

            print(f"\n✅ 成功生成 FontAwesome {version} LaTeX 包!")
            print(f"📁 输出目录: {self.output_dir.absolute()}")
            print(f"📦 包名: fontawesome{version_major}")
            print(f"🔤 字体文件: {len(font_files)} 个")
            print(f"🎨 图标数量: {icon_count} 个")

            print("\n使用方法:")
            print("1. 将生成的文件复制到你的 LaTeX 项目目录")
            print(f"2. 在文档中使用: \\usepackage{{fontawesome{version_major}}}")
            print("3. 用 xelatex 或 lualatex 编译")

        except KeyboardInterrupt:
            print("\n❌ 用户中断")
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate FontAwesome7 LaTeX package from latest release"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./fontawesome7-latex-latest",
        help="Output directory (default: ./fontawesome7-latex-latest)",
    )

    args = parser.parse_args()

    generator = FontAwesomeGenerator(args.output)
    generator.run()
