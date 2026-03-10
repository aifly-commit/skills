#!/usr/bin/env python3
"""
企业微信图片发送技能 - 完整版
支持多种图片来源，使用 message 工具可靠发送
"""
import os
import sys
import json
import requests
import tempfile
from datetime import datetime
from PIL import Image
import argparse

# 配置常量
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
TEMP_DIR = "/tmp/openclaw/images"

def ensure_directory():
    """确保临时目录存在"""
    os.makedirs(TEMP_DIR, exist_ok=True)

def log(message, level="INFO"):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

def download_image_from_url(url):
    """从 URL 下载图片"""
    try:
        log(f"开始下载图片: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 检查文件大小
        content_length = int(response.headers.get('content-length', 0))
        if content_length > MAX_FILE_SIZE:
            return None, f"图片文件过大 ({content_length} bytes)"
        
        # 保存图片
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(TEMP_DIR, f"downloaded-{timestamp}.jpg")
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(output_file)
        log(f"图片下载成功: {output_file} ({file_size} bytes)")
        return output_file, None
        
    except requests.RequestException as e:
        return None, f"下载失败: {str(e)}"
    except Exception as e:
        return None, f"保存失败: {str(e)}"

def optimize_image(input_file, max_width=1024, max_height=1024):
    """优化图片大小和格式"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(TEMP_DIR, f"optimized-{timestamp}.jpg")
        
        with Image.open(input_file) as img:
            # 转换为 RGB
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
            quality = 85
            img.save(output_file, 'JPEG', quality=quality, optimize=True)
            
            # 检查文件大小，如果过大则继续压缩
            file_size = os.path.getsize(output_file)
            while file_size > MAX_FILE_SIZE and quality > 20:
                quality -= 10
                img.save(output_file, 'JPEG', quality=quality, optimize=True)
                file_size = os.path.getsize(output_file)
                log(f"图片压缩: quality={quality}, size={file_size}")
            
            log(f"图片优化完成: {output_file} ({file_size} bytes)")
            return output_file, None
            
    except Exception as e:
        return None, f"图片处理失败: {str(e)}"

def send_image_with_message_tool(image_file, user=None, message=""):
    """
    使用 message 工具发送图片到企业微信
    
    这个函数会输出特定的 JSON 格式，供 OpenClaw 的 message 工具调用
    
    Args:
        image_file: 图片文件路径
        user: 目标用户（None=当前用户）
        message: 文字说明
    """
    try:
        # 自动获取当前用户（如果没有指定）
        if user is None:
            user = os.getenv('OPENCLAW_USER', 'FengCe')  # 默认值，但可被环境变量覆盖
        
        # 验证图片
        if not os.path.exists(image_file):
            return False, f"图片文件不存在: {image_file}"
        
        file_size = os.path.getsize(image_file)
        if file_size == 0:
            return False, "图片文件为空"
        
        # 优化图片
        optimized_file, error = optimize_image(image_file)
        if error:
            return False, error
        
        # 输出 JSON 格式供 OpenClaw 调用 message 工具
        result = {
            "tool": "message",
            "action": "send",
            "params": {
                "channel": "wecom",
                "topic": user,  # 使用参数化用户
                "message": message,
                "media": optimized_file,
                "filename": os.path.basename(optimized_file),
                "contentType": "image/jpeg"
            },
            "image_info": {
                "original": image_file,
                "optimized": optimized_file,
                "size": os.path.getsize(optimized_file),
                "user": user,
                "message": message
            }
        }
        
        # 输出 JSON 到 stdout，供 OpenClaw 解析
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        log(f"✅ 图片准备完成，等待发送")
        log(f"📁 优化文件: {optimized_file}")
        log(f"📊 文件大小: {os.path.getsize(optimized_file)} bytes")
        log(f"👤 目标用户: {user}")
        
        return True, result
        
    except Exception as e:
        log(f"发送失败: {str(e)}", "ERROR")
        return False, f"发送失败: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description='企业微信图片发送工具 - 完整版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从 URL 下载并发送
  python3 send_image_v2.py --url "https://example.com/image.jpg" --message "图片说明"
  
  # 发送本地图片
  python3 send_image_v2.py --file "/path/image.jpg" --message "图片说明" --user "FengCe"
        """
    )
    
    # 必选参数（二选一）
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--url', help='图片下载链接')
    source_group.add_argument('--file', help='本地图片文件路径')
    
    # 可选参数
    parser.add_argument('--message', default='', help='配图文字说明')
    parser.add_argument('--user', default='FengCe', help='目标用户名')
    parser.add_argument('--max-width', type=int, default=1024, help='最大宽度')
    parser.add_argument('--max-height', type=int, default=1024, help='最大高度')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_directory()
    
    image_file = None
    error = None
    
    # 1. 从 URL 下载
    if args.url:
        log(f"从 URL 下载图片: {args.url}")
        image_file, error = download_image_from_url(args.url)
    
    # 2. 使用本地文件
    elif args.file:
        if not os.path.exists(args.file):
            log(f"文件不存在: {args.file}", "ERROR")
            print(json.dumps({"error": f"文件不存在: {args.file}"}))
            sys.exit(1)
        image_file = args.file
        log(f"使用本地文件: {image_file}")
    
    # 检查图片获取是否成功
    if error:
        log(f"图片获取失败: {error}", "ERROR")
        print(json.dumps({"error": error}))
        sys.exit(1)
    
    # 发送图片
    success, result = send_image_with_message_tool(
        image_file, 
        args.user, 
        args.message
    )
    
    if not success:
        log(f"发送失败: {result}", "ERROR")
        print(json.dumps({"error": result}))
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log("用户中断操作", "INFO")
        sys.exit(0)
    except Exception as e:
        log(f"程序异常: {str(e)}", "ERROR")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)