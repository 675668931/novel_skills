#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节字数检查脚本
检查指定章节文件的字数，低于2000字时提示需要扩充，超过3000字时提示偏长
"""

import os
import re
import sys
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def count_chinese_words(text: str) -> int:
    """统计中文字数（排除标点符号和空格）"""
    # 统计中文字符（汉字），排除括号内的结构标记
    # 过滤掉形如（开篇：...）（发展：...）等结构标记
    clean_text = re.sub(r'（[^）]+）', '', text)
    chinese_chars = re.findall(r'[一-鿿]', clean_text)
    return len(chinese_chars)


def extract_content_from_chapter(file_path: Path) -> str:
    """从章节文件中提取正文内容

    固定模板格式：
    第XX章 [章节名]

    【本章概要】...
    【本章爽点】...
    【情绪曲线】...
    【涉及角色】...
    【涉及地点】...

    （开篇：...）
    （发展：...）
    （高潮：...）
    （收束：...）

    【章末钩子】...
    【下章预告】...
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 1. 找到【涉及地点】那一行，正文从下一行开始
    line_index = 0
    found_meta = False
    while line_index < len(lines):
        line = lines[line_index].strip()
        if line.startswith('【涉及地点】'):
            found_meta = True
            line_index += 1
            break
        line_index += 1

    if not found_meta:
        # 兜底：跳过前5行（章节标题 + 空行 + 4个元数据行）
        line_index = 0
        while line_index < len(lines) and not lines[line_index].strip():
            line_index += 1
        if line_index < len(lines) and re.match(r'第\d+章', lines[line_index].strip()):
            line_index += 1
        while line_index < len(lines) and lines[line_index].strip():
            line_index += 1
        while line_index < len(lines) and not lines[line_index].strip():
            line_index += 1

    # 2. 跳过空行
    while line_index < len(lines) and not lines[line_index].strip():
        line_index += 1

    # 3. 提取正文，直到【章末钩子】或【下章预告】
    main_content_lines = []
    for i in range(line_index, len(lines)):
        line = lines[i].strip()
        if line.startswith('【章末钩子】') or line.startswith('【下章预告】'):
            break
        main_content_lines.append(lines[i])

    return '\n'.join(main_content_lines)


def check_chapter(file_path: str, min_words: int = 2000, max_words: int = 3000) -> dict:
    """检查单个章节的字数"""
    path = Path(file_path)

    if not path.exists():
        return {
            'file': str(path),
            'exists': False,
            'word_count': 0,
            'status': 'error',
            'message': f'文件不存在: {file_path}'
        }

    main_content = extract_content_from_chapter(path)
    word_count = count_chinese_words(main_content)

    if word_count < min_words:
        status = 'fail'
        message = f'字数: {word_count}' + f' (✗ 不足，需要至少 {min_words} 字)'
    elif word_count > max_words:
        status = 'fail'
        message = f'字数: {word_count}' + f' (✗ 超过 {max_words} 字，需要精简)'
    else:
        status = 'pass'
        message = f'字数: {word_count}' + f' (✓ 达标)'

    return {
        'file': str(path),
        'exists': True,
        'word_count': word_count,
        'status': status,
        'message': message
    }


def check_all_chapters(directory: str, pattern: str = '第*.md', min_words: int = 2000, max_words: int = 3000) -> list:
    """检查目录下所有符合模式的章节文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f'错误: 目录不存在 - {directory}')
        return []

    chapter_files = sorted(dir_path.glob(pattern))
    results = []

    for chapter_file in chapter_files:
        result = check_chapter(str(chapter_file), min_words, max_words)
        results.append(result)

    return results


def print_results(results: list, min_words: int = 2000, max_words: int = 3000):
    """打印检查结果"""
    if not results:
        print('没有找到章节文件')
        return

    total_words = 0
    passed = 0
    failed = 0

    print('\n' + '=' * 60)
    print('章节字数检查报告')
    print('=' * 60)

    for result in results:
        if not result['exists']:
            print(f'\n❌ {result["file"]}')
            print(f'   {result["message"]}')
            continue

        total_words += result['word_count']
        if result['status'] == 'pass':
            passed += 1
            icon = '✅'
        else:
            failed += 1
            icon = '❌'

        print(f'\n{icon} {Path(result["file"]).name}')
        print(f'   {result["message"]}')

    print('\n' + '-' * 60)
    print(f'总计: {len(results)} 章 | {passed} 章达标 | {failed} 章需调整 | 总字数: {total_words:,}')
    print('-' * 60)

    if failed > 0:
        print(f'\n⚠️  有 {failed} 章字数不在 {min_words}-{max_words} 字范围内，需要调整:')
        print('   - 字数不足时：添加细节描写（环境、心理、动作）、增加对话场景、扩展人物内心活动')
        print('   - 字数过多时：精简描写、合并对话、压缩场景')


def main():
    """主函数"""
    min_words = 2000
    max_words = 3000

    if len(sys.argv) < 2:
        print('用法:')
        print('  检查单个章节: python check_chapter_wordcount.py <章节文件路径> [最小字数] [最大字数]')
        print('  检查所有章节: python check_chapter_wordcount.py --all <目录路径> [最小字数] [最大字数]')
        print('')
        print('示例:')
        print('  python check_chapter_wordcount.py output/第01章.md')
        print('  python check_chapter_wordcount.py output/第01章.md 2000 3000')
        print('  python check_chapter_wordcount.py --all output/')
        print('  python check_chapter_wordcount.py --all output/ 2000 3000')
        return

    if sys.argv[1] == '--all':
        if len(sys.argv) < 3:
            print('错误: 使用 --all 时需要指定目录路径')
            return
        directory = sys.argv[2]
        min_words = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
        max_words = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
        results = check_all_chapters(directory, min_words=min_words, max_words=max_words)
        print_results(results, min_words, max_words)
    else:
        file_path = sys.argv[1]
        min_words = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
        max_words = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
        result = check_chapter(file_path, min_words, max_words)
        print_results([result], min_words, max_words)


if __name__ == '__main__':
    main()
