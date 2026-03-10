# 快速提交指南 - 5 分钟完成

## 🚀 快速开始

### 前提条件
- GitHub 账号
- Git 已安装
- OpenClaw 技能已准备就绪

---

## 📝 提交步骤（5 分钟）

### 步骤 1：Fork 官方仓库（1 分钟）

1. 访问：https://github.com/openclaw/skills
2. 点击右上角 **"Fork"**
3. 等待 Fork 完成（约 30 秒）

### 步骤 2：克隆到本地（1 分钟）

```bash
# 替换 YOUR_USERNAME
git clone https://github.com/YOUR_USERNAME/skills.git
cd skills
```

### 步骤 3：添加技能（1 分钟）

```bash
# 创建目录
mkdir -p skills/wecom-image-sender

# 复制文件（一行命令）
cp -r /root/.openclaw/workspace/skills/wecom-image-sender/* skills/wecom-image-sender/

# 验证文件
ls skills/wecom-image-sender/
```

**应该看到**：
```
SKILL.md  README.md  LICENSE  requirements.txt  scripts/  docs/
```

### 步骤 4：提交推送（1 分钟）

```bash
# 添加文件
git add skills/wecom-image-sender/

# 提交
git commit -m "feat: 添加企业微信图片发送技能"

# 推送
git push origin main
```

### 步骤 5：创建 PR（1 分钟）

1. 访问你的仓库：https://github.com/YOUR_USERNAME/skills
2. 点击 **"Pull Request"**
3. 标题：`feat: 添加企业微信图片发送技能`
4. 点击 **"Create Pull Request"**

---

## ✅ 完整命令（复制粘贴）

```bash
# 一键执行所有步骤
cd /tmp
git clone https://github.com/YOUR_USERNAME/skills.git
cd skills
mkdir -p skills/wecom-image-sender
cp -r /root/.openclaw/workspace/skills/wecom-image-sender/* skills/wecom-image-sender/
git add skills/wecom-image-sender/
git commit -m "feat: 添加企业微信图片发送技能"
git push origin main
```

**然后**：
1. 访问 GitHub
2. 创建 Pull Request
3. 等待审核

---

## 📋 检查清单

提交前确认：
- [ ] 已 Fork 官方仓库
- [ ] 已克隆到本地
- [ ] 已复制所有技能文件
- [ ] 已提交到你的仓库
- [ ] 已创建 Pull Request

---

## 🎯 预期时间线

- **提交**: 立即
- **审核**: 1-3 工作日
- **合并**: 审核通过后
- **发布**: 合并后自动发布

---

## 💡 提示

### 如果没有 GitHub 账号
1. 访问：https://github.com/signup
2. 注册（免费）
3. 验证邮箱
4. 继续上述步骤

### 如果遇到权限问题
```bash
# 配置 Git 用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 使用 SSH（推荐）
git clone git@github.com:YOUR_USERNAME/skills.git
```

---

**5 分钟后，你的技能就能被全世界使用了！** 🌍