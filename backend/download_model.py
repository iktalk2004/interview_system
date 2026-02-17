"""
Hugging Face 模型下载脚本

使用方法：
1. 配置代理（如果需要）
2. 运行脚本下载模型
"""

import os
import sys

# 配置 Hugging Face 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 如果你有代理，取消下面的注释并填入你的代理地址
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

try:
    from sentence_transformers import SentenceTransformer
    
    print("=" * 60)
    print("开始下载中文句子嵌入模型...")
    print("=" * 60)
    print()
    
    model_name = 'DMetaSoul/sbert-chinese-general-v2'
    
    print(f"模型名称: {model_name}")
    print(f"使用镜像: {os.environ.get('HF_ENDPOINT', '官方源')}")
    print()
    
    print("正在下载模型，这可能需要几分钟...")
    print("请耐心等待...")
    print()
    
    # 下载模型
    model = SentenceTransformer(model_name)
    
    print()
    print("=" * 60)
    print("✓ 模型下载成功！")
    print("=" * 60)
    print()
    print("模型已缓存到本地，下次启动将直接使用缓存。")
    print("现在可以启动 Django 服务器了。")
    print()
    print("启动命令：")
    print("  python manage.py runserver")
    
except ImportError:
    print("错误：sentence-transformers 未安装")
    print()
    print("请先安装依赖：")
    print("  pip install sentence-transformers")
    sys.exit(1)
    
except Exception as e:
    print()
    print("=" * 60)
    print("✗ 模型下载失败")
    print("=" * 60)
    print()
    print(f"错误信息: {e}")
    print()
    print("可能的解决方案：")
    print("1. 检查网络连接")
    print("2. 配置代理（修改脚本中的代理设置）")
    print("3. 使用其他镜像源")
    print("4. 禁用智能评分功能（见下方说明）")
    print()
    print("如果无法下载模型，可以禁用智能评分功能：")
    print("  在 .env 文件中添加：DISABLE_LLM_SCORING=True")
    sys.exit(1)
