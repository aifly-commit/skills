---
name: wecom-image-sender
description: 企业微信图片发送技能。支持AI生成、URL下载、本地上传三种图片来源，自动格式转换和大小优化。适用于新闻配图、数据可视化、内容配图等场景。
version: "1.0.0"
user-invocable: true
metadata:
  openclaw:
    emoji: 📸
    category: communication
    requires:
      bins:
        - python3
      env:
        - GEMINI_API_KEY
      tools:
        - message
    tags:
      - image
      - wecom
      - enterprise-wechat
      - image-generation
      - image-upload
---

# 企业微信图片发送技能

专为 OpenClaw 设计的企业微信图片发送解决方案，支持多种图片来源和智能格式转换。

---

## ⚠️ 重要规则

1. **必须调用脚本**：用户要求发送图片时，必须执行本技能脚本，禁止用文本描述替代。
2. **检查输出产物**：执行后检查是否生成图片文件。无图片则自动重试或报错。
3. **格式验证**：自动验证图片格式和大小，确保符合企业微信要求。

---

## 🎯 触发判断

### 触发场景
- 发送图片、发送照片、发送图
- 生成图片、画图、做图
- 上传图片、传图片
- 配图、插图、新闻图片
- 图片说明、图片描述

### 不触发场景
- 图片分析、OCR、识别图片内容
- 图片评价、图片打分
- 纯文本描述图片

---

## 🚀 使用方法

### 1. AI 生成图片并发送

```bash
# 基础用法
python3 {baseDir}/scripts/send_image.py --generate --prompt "图片描述" --message "说明文字"

# 完整参数
python3 {baseDir}/scripts/send_image.py \
  --generate \
  --prompt "中东地区地图" \
  --width 1024 \
  --height 768 \
  --aspect-ratio 16:9 \
  --style natural \
  --message "地理示意图"
```

### 2. 从 URL 下载并发送

```bash
python3 {baseDir}/scripts/send_image.py \
  --url "https://example.com/image.jpg" \
  --message "新闻配图" \
  --user "FengCe"
```

### 3. 发送本地图片

```bash
python3 {baseDir}/scripts/send_image.py \
  --file "/path/to/image.png" \
  --message "本地图片说明"
```

---

## ⚙️ 参数详解

### 必选参数（三选一）

| 参数 | 说明 | 使用场景 |
|------|------|----------|
| `--generate` | 使用 AI 生成图片 | 创建新图片 |
| `--url` | 图片下载链接 | 使用网络图片 |
| `--file` | 本地图片路径 | 使用本地图片 |

### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--prompt` | 图片描述文本 | - | "美丽的风景" |
| `--message` | 配图文字说明 | 空字符串 | "今日风景" |
| `--user` | 目标用户名 | FengCe | "ZhangSan" |
| `--width` | 图片宽度 | 800 | 1024 |
| `--height` | 图片高度 | 600 | 768 |
| `--aspect-ratio` | 宽高比 | 16:9 | "4:3" |
| `--style` | 图片风格 | natural | "vivid" |

### 宽高比选项

- `1:1` - 正方形（图标、头像）
- `16:9` - 宽屏（封面、横图）
- `9:16` - 竖屏（手机封面）
- `4:3` - 标准（文档）
- `3:4` - 竖向标准

### 风格选项

- `natural` - 自然风格（默认）
- `vivid` - 生动风格
- `photorealistic` - 照片级真实感

---

## 📝 使用场景示例

### 新闻配图

```bash
# 地理示意图
python3 scripts/send_image.py --generate \
  --prompt "中东地区地图显示以色列和伊朗地理位置" \
  --aspect-ratio 16:9 \
  --message "中东地理示意图"

# 数据可视化
python3 scripts/send_image.py --generate \
  --prompt "柱状图显示AI行业发展数据" \
  --style natural \
  --message "行业数据可视化"
```

### 内容创作

```bash
# Logo 设计
python3 scripts/send_image.py --generate \
  --prompt "科技公司Logo，现代简约风格" \
  --aspect-ratio 1:1 \
  --message "公司Logo设计"

# 海报设计
python3 scripts/send_image.py --generate \
  --prompt "AI技术大会海报，科技感十足" \
  --aspect-ratio 9:16 \
  --style vivid
```

### 日常使用

```bash
# 风景图
python3 scripts/send_image.py --generate \
  --prompt "日落时分的海滩风景" \
  --aspect-ratio 16:9

# 网络图片转发
python3 scripts/send_image.py --url \
  "https://example.com/news-image.jpg" \
  --message "今日热点新闻配图"
```

---

## 🔧 技术实现

### 自动化流程

1. **图片来源处理**
   - AI 生成：调用 Gemini API
   - URL 下载：验证并下载
   - 本地文件：验证格式

2. **格式转换**
   - 自动转换为 JPEG/PNG
   - 压缩到企业微信支持的大小（< 5MB）
   - 保持图片质量

3. **发送优化**
   - 自动调整尺寸
   - 企业微信格式适配
   - 错误重试机制

### ⚠️ 重要：发送机制

**必须输出以下标记才能实际发送图片**：

```python
# 在脚本最后输出这两个标记
print("[[image]]")
print(f"MEDIA:/path/to/image.jpg")
```

**工作原理**：
- OpenClaw 自动识别 `[[image]]` 标记
- 读取 `MEDIA:` 后的图片路径
- 自动将图片发送到企业微信

**错误做法**：
```python
# ❌ 错误：只准备图片，不发送
return True, {"file": image_path}

# ✅ 正确：输出标记，实际发送
print("[[image]]")
print(f"MEDIA:{image_path}")
return True, {"sent": True}
```

### 错误处理

- **生成失败**: 提示检查 API Key 和网络
- **下载失败**: 提示检查 URL 和网络
- **格式错误**: 自动转换或提示
- **发送失败**: 重试 3 次后报错

---

## 📊 图片生成建议

### 内容建议
- **地理相关**: 地图、位置示意图
- **数据可视化**: 图表、统计图形
- **场景配图**: 新闻场景、示意图
- **教育内容**: 时间轴、流程图

### 尺寸建议
- **消息封面**: 16:9 (1200x675)
- **配图**: 4:3 (800x600)
- **图示**: 1:1 (400x400)
- **长图**: 9:16 (1080x1920)

### 文字说明
- 简洁明了，不超过 20 字
- 与图片内容相关
- 使用 Emoji 增加可读性

---

## 🛡️ 安全与隐私

### 图片内容
- 避免生成敏感或违规内容
- 遵守相关法律法规
- 尊重版权和隐私

### 数据处理
- 临时文件自动清理
- 不存储用户图片
- API Key 安全管理

---

## 🚨 故障排除

### 常见问题

#### 1. 图片生成失败
**解决方案**:
- 检查 `GEMINI_API_KEY` 环境变量
- 确认网络连接正常
- 使用更具体的描述文本

#### 2. 发送失败
**解决方案**:
- 检查企业微信配置
- 确认图片格式和大小
- 查看错误日志

#### 3. 下载失败
**解决方案**:
- 验证 URL 可访问性
- 检查网络连接
- 尝试使用本地图片

---

## 📞 支持

- **文档**: [GitHub Wiki](https://github.com/your-username/wecom-image-sender/wiki)
- **问题反馈**: [GitHub Issues](https://github.com/your-username/wecom-image-sender/issues)
- **邮箱**: your-email@example.com

---

*技能版本：1.0.0*  
*更新时间：2026-03-10*  
*维护者：OpenClaw Community*