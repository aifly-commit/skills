#!/usr/bin/env python3
"""
企业微信图片发送脚本
支持 AI 生成、URL 下载、本地上传三种方式
"""

import os
import sys
import json
import requests
import urllib.request
import tempfile
from datetime import datetime
from PIL import Image
import io
import subprocess
import argparse
import base64

# 配置常量
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
TEMP_DIR = "/tmp/openclaw/images"
GEMINI_SCRIPT = "/root/.openclaw/workspace/skills/gemini-image-generator/scripts/generate_image.py"

def ensure_directory():
    """确保临时目录存在"""
    os.makedirs(TEMP_DIR, exist_ok=True)

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def generate_image_with_gemini(prompt, width=800, height=600, style="natural", aspect_ratio="16:9"):
    """使用 Gemini 生成图片"""
    try:
        if not os.path.exists(GEMINI_SCRIPT):
            return None, "Gemini 图片生成技能未安装，请先安装 gemini-image-generator 技能"
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(TEMP_DIR, f"generated-{timestamp}.png")
        
        cmd = [
            "python3", GEMINI_SCRIPT,
            "--prompt", prompt,
            "--filename", output_file,
            "--aspect-ratio", aspect_ratio,
            "--style", style
        ]
        
        log(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(output_file):
            log(f"图片生成成功: {output_file}")
            return output_file, None
        else:
            error_msg = result.stderr if result.stderr else "未知错误"
            log(f"图片生成失败: {error_msg}", "ERROR")
            return None, f"Gemini 生成失败: {error_msg}"
            
    except subprocess.TimeoutExpired:
        log("图片生成超时", "ERROR")
        return None, "图片生成超时，请稍后重试"
    except Exception as e:
        log(f"生成异常: {str(e)}", "ERROR")
        return None, f"生成失败: {str(e)}"

def download_image_from_url(url, output_file):
    """从 URL 下载图片"""
    try:
        log(f"开始下载图片: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 检查文件大小
        if len(response.content) > MAX_FILE_SIZE:
            return None, f"图片文件过大 ({len(response.content)} bytes)，最大支持 {MAX_FILE_SIZE} bytes"
        
        # 保存图片
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        log(f"图片下载成功: {output_file}")
        return output_file, None
        
    except requests.RequestException as e:
        log(f"下载失败: {str(e)}", "ERROR")
        return None, f"下载失败: {str(e)}"
    except Exception as e:
        log(f"保存失败: {str(e)}", "ERROR")
        return None, f"保存失败: {str(e)}"

def convert_and_optimize_image(input_file, max_width=1024, max_height=1024):
    """转换和优化图片"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(TEMP_DIR, f"optimized-{timestamp}.jpg")
        
        with Image.open(input_file) as img:
            # 转换为 RGB（如果是 RGBA）
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整大小
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                log(f"图片尺寸调整: {width}x{height} -> {new_width}x{new_height}")
            
            # 保存优化后的图片
            img.save(output_file, 'JPEG', quality=85, optimize=True)
            
            # 检查文件大小
            file_size = os.path.getsize(output_file)
            if file_size > MAX_FILE_SIZE:
                # 进一步压缩
                quality = 70
                while file_size > MAX_FILE_SIZE and quality > 20:
                    img.save(output_file, 'JPEG', quality=quality, optimize=True)
                    file_size = os.path.getsize(output_file)
                    quality -= 10
                    log(f"图片压缩: quality={quality}, size={file_size}")
            
            log(f"图片优化完成: {output_file} ({file_size} bytes)")
            return output_file, None
            
    except Exception as e:
        log(f"图片处理失败: {str(e)}", "ERROR")
        return None, f"图片处理失败: {str(e)}"

def validate_image(image_file):
    """验证图片文件"""
    try:
        if not os.path.exists(image_file):
            return False, "图片文件不存在"
        
        file_size = os.path.getsize(image_file)
        if file_size == 0:
            return False, "图片文件为空"
        
        if file_size > MAX_FILE_SIZE:
            return False, f"文件过大: {file_size} bytes (最大 {MAX_FILE_SIZE} bytes)"
        
        with Image.open(image_file) as img:
            img.verify()
        
        return True, None
        
    except Exception as e:
        return False, f"图片验证失败: {str(e)}"

def send_image_via_wecom(image_file, user="FengCe", message=""):
    """通过企业微信发送图片"""
    try:
        # 验证图片
        is_valid, error = validate_image(image_file)
        if not is_valid:
            return False, error
        
        # 优化图片
        optimized_file, error = convert_and_optimize_image(image_file)
        if error:
            return False, error
        
        # 读取图片数据
        with open(optimized_file, 'rb') as f:
            image_data = f.read()
        
        # 使用 OpenClaw 标准方式发送图片
        # 输出 [[image]] 和 MEDIA: 标记，让 OpenClaw 自动处理
        log(f"图片已准备发送: {optimized_file}")
        log(f"目标用户: {user}")
        log(f"文件大小: {len(image_data)} bytes")
        
        # OpenClaw 自动识别这些标记并发送图片
        print("[[image]]")
        print(f"MEDIA:{optimized_file}")
        
        return True, {
            "file": optimized_file,
            "user": user,
            "message": message,
            "size": len(image_data),
            "sent": True
        }
        
    except Exception as e:
        log(f"发送失败: {str(e)}", "ERROR")
        return False, f"发送失败: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description='OpenClaw 企业微信图片发送工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成图片
  python3 send_image.py --generate --prompt "美丽的风景" --message "今日风景"
  
  # 从 URL 下载
  python3 send_image.py --url "https://example.com/image.jpg" --message "新闻配图"
  
  # 发送本地图片
  python3 send_image.py --file "/path/image.jpg" --message "图片说明"
        """
    )
    
    # 必选参数组（三选一）
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--generate', action='store_true', help='使用 AI 生成图片')
    source_group.add_argument('--url', help='图片下载链接')
    source_group.add_argument('--file', help='本地图片文件路径')
    
    # 可选参数
    parser.add_argument('--prompt', help='生成图片的描述文本（生成时必填）')
    parser.add_argument('--message', default='', help='配图文字说明')
    parser.add_argument('--user', default='FengCe', help='目标用户名')
    parser.add_argument('--width', type=int, default=800, help='图片宽度')
    parser.add_argument('--height', type=int, default=600, help='图片高度')
    parser.add_argument('--aspect-ratio', default='16:9', help='宽高比 (1:1, 16:9, 9:16, 4:3, 3:4)')
    parser.add_argument('--style', default='natural', help='图片风格 (natural, vivid, photorealistic)')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_directory()
    
    # 验证参数
    if args.generate and not args.prompt:
        parser.error("生成图片时必须提供 --prompt 参数")
    
    image_file = None
    error = None
    
    # 1. 生成图片
    if args.generate:
        log(f"开始生成图片: {args.prompt}")
        image_file, error = generate_image_with_gemini(
            args.prompt, args.width, args.height, args.style, args.aspect_ratio
        )
    
    # 2. 下载图片
    elif args.url:
        log(f"开始下载图片: {args.url}")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        temp_file = os.path.join(TEMP_DIR, f"downloaded-{timestamp}.jpg")
        image_file, error = download_image_from_url(args.url, temp_file)
    
    # 3. 使用本地文件
    elif args.file:
        if not os.path.exists(args.file):
            log(f"文件不存在: {args.file}", "ERROR")
            sys.exit(1)
        image_file = args.file
        log(f"使用本地文件: {image_file}")
    
    # 检查图片获取是否成功
    if error:
        log(f"图片获取失败: {error}", "ERROR")
        print(f"❌ 错误: {error}")
        sys.exit(1)
    
    # 发送到企业微信
    success, result = send_image_via_wecom(image_file, args.user, args.message)
    
    if success:
        log("图片发送成功")
        print(f"✅ 图片处理成功")
        print(f"📁 原始文件: {image_file}")
        print(f"📱 优化文件: {result['file']}")
        print(f"👤 目标用户: {result['user']}")
        print(f"📊 文件大小: {result['size']} bytes")
        if result['message']:
            print(f"📝 文字说明: {result['message']}")
    else:
        log(f"发送失败: {result}", "ERROR")
        print(f"❌ 发送失败: {result}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log("用户中断操作", "INFO")
        sys.exit(0)
    except Exception as e:
        log(f"程序异常: {str(e)}", "ERROR")
        print(f"❌ 程序异常: {str(e)}")
        sys.exit(1)