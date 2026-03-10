# 通用性指南 - 快速开始

## 🚀 5 分钟了解通用性

### 问题：这个技能只给 FengCe 用吗？

**答案：不！这是一个通用的技能，任何用户都可以使用！**

---

## 📝 快速验证

### 1. 查看代码

```python
# send_image_v2.py 中的用户参数
def send_image_with_message_tool(image_file, user=None, message=""):
    # ✅ user=None 表示自动检测当前用户
    if user is None:
        user = os.getenv('OPENCLAW_USER', 'FengCe')  # 默认值
```

### 2. 实际测试

**Alice 使用**：
```bash
# Alice 登录 OpenClaw
export OPENCLAW_USER="alice"
python3 send_image_v2.py --file photo.jpg
# → 发送给 Alice
```

**Bob 使用**：
```bash
# Bob 登录 OpenClaw
export OPENCLAW_USER="bob"
python3 send_image_v2.py --file photo.jpg
# → 发送给 Bob
```

### 3. 手动指定用户

```bash
# Alice 发送给 Bob
python3 send_image_v2.py --file photo.jpg --user "bob"
# → 发送给 Bob（不是 Alice）
```

---

## ✅ 通用性检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| **参数化用户** | ✅ | user 参数可选 |
| **自动检测** | ✅ | 从环境变量获取 |
| **手动指定** | ✅ | --user 参数 |
| **无硬编码** | ✅ | 只作为默认值 |
| **多平台** | ✅ | 支持多个平台 |

---

## 🎯 使用建议

### 推荐：让系统自动检测

```bash
# ✅ 最简单的方式
python3 send_image_v2.py --file photo.jpg --message "图片说明"
```

### 特殊场景：手动指定用户

```bash
# ✅ 需要发给其他人时
python3 send_image_v2.py --file photo.jpg --user "其他用户" --message "图片"
```

---

## 💡 核心原理

**用户获取优先级**：
1. **命令行参数** `--user` (最高优先级)
2. **环境变量** `OPENCLAW_USER`
3. **默认值** `'FengCe'` (最低优先级)

**流程图**：
```
开始
 ↓
有 --user 参数? → Yes → 使用指定用户
 ↓ No
有环境变量? → Yes → 使用环境变量用户
 ↓ No
使用默认用户
 ↓
发送图片
 ↓
结束
```

---

## 📞 有问题？

- **查看详细文档**: [UNIVERSAL_DESIGN.md](UNIVERSAL_DESIGN.md)
- **提交问题**: [GitHub Issues](https://github.com/your-username/wecom-image-sender/issues)
- **社区讨论**: OpenClaw Discord

---

**总结：这个技能完全通用，任何用户都可以使用！** ✅