#!/bin/bash

# Ebook-MCP 测试运行脚本

echo "=========================================="
echo "Ebook-MCP 单元测试运行器"
echo "=========================================="

# 检查是否安装了 pytest
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest 未安装，请先安装: pip install pytest"
    exit 1
fi

# 设置测试目录
TEST_DIR="src/ebook_mcp/tests"

echo "📁 测试目录: $TEST_DIR"
echo ""

# 运行基本测试（推荐）
echo "🧪 运行基本测试（不需要外部依赖）..."
python -m pytest $TEST_DIR/test_basic.py -v
BASIC_RESULT=$?

echo ""
echo "🧪 运行 EPUB 章节提取修复版本测试..."
python -m pytest $TEST_DIR/test_epub_chapter_extraction_fixed.py -v
FIXED_RESULT=$?

echo ""
echo "🧪 运行 AZW 测试（如果模块可用）..."
python -m pytest $TEST_DIR/test_azw.py -v
AZW_RESULT=$?

echo ""
echo "=========================================="
echo "测试结果总结:"
echo "=========================================="

if [ $BASIC_RESULT -eq 0 ]; then
    echo "✅ 基本测试: 通过"
else
    echo "❌ 基本测试: 失败"
fi

if [ $FIXED_RESULT -eq 0 ]; then
    echo "✅ EPUB 章节提取修复测试: 通过"
else
    echo "❌ EPUB 章节提取修复测试: 失败"
fi

if [ $AZW_RESULT -eq 0 ]; then
    echo "✅ AZW 测试: 通过或跳过"
else
    echo "❌ AZW 测试: 失败"
fi

echo ""
echo "💡 提示:"
echo "   - 要运行完整测试，请先安装项目依赖: pip install -e ."
echo "   - 查看详细测试指南: cat HOW-TO-TEST.md"
echo ""

# 返回总体结果
if [ $BASIC_RESULT -eq 0 ] && [ $FIXED_RESULT -eq 0 ] && [ $AZW_RESULT -eq 0 ]; then
    echo "🎉 所有可用测试通过！"
    exit 0
else
    echo "⚠️  部分测试失败，请检查上述输出"
    exit 1
fi 