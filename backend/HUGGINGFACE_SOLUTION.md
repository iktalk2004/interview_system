# Hugging Face 模型下载问题解决方案

## 问题描述

启动 Django 服务器时出现以下错误：
```
MaxRetryError: HTTPSConnectionPool(host='huggingface.co', port=443): Max retries exceeded
```

这是因为无法从 Hugging Face 下载 `DMetaSoul/sbert-chinese-general-v2` 模型。

## 解决方案

### 方案1：禁用智能评分功能（推荐，最快）

如果你暂时不需要智能评分功能，可以禁用它：

1. 打开 `backend/.env` 文件
2. 添加以下配置：
   ```env
   DISABLE_LLM_SCORING=True
   ```
3. 保存文件
4. 重新启动服务器：
   ```bash
   python manage.py runserver
   ```

**优点**：
- 无需下载模型
- 服务器可以正常启动
- 其他功能不受影响

**缺点**：
- 无法使用智能评分功能
- 用户答案需要手动评分

---

### 方案2：使用 Hugging Face 镜像（推荐）

使用国内镜像源加速模型下载：

1. 打开 `backend/.env` 文件
2. 添加以下配置：
   ```env
   HF_ENDPOINT=https://hf-mirror.com
   ```
3. 保存文件
4. 重新启动服务器：
   ```bash
   python manage.py runserver
   ```

**优点**：
- 国内镜像，速度快
- 可以使用智能评分功能
- 配置简单

**缺点**：
- 首次启动仍需下载模型（约 400MB）

---

### 方案3：配置代理

如果你有代理（VPN），可以配置代理：

1. 打开 `backend/.env` 文件
2. 添加以下配置（根据你的代理地址修改）：
   ```env
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```
3. 保存文件
4. 重新启动服务器：
   ```bash
   python manage.py runserver
   ```

**注意**：
- `7890` 是常见的代理端口，请根据你的实际情况修改
- 如果使用 socks5 代理，格式为：`socks5://127.0.0.1:7890`

**优点**：
- 可以使用智能评分功能
- 下载速度快

**缺点**：
- 需要有代理
- 需要配置代理地址

---

### 方案4：手动下载模型

使用专门的下载脚本下载模型：

1. 打开终端，进入 backend 目录：
   ```bash
   cd backend
   ```

2. 运行下载脚本：
   ```bash
   python download_model.py
   ```

3. 等待模型下载完成（可能需要几分钟）

4. 下载完成后，启动服务器：
   ```bash
   python manage.py runserver
   ```

**优点**：
- 可以看到下载进度
- 可以单独下载模型
- 下载一次后永久缓存

**缺点**：
- 需要等待下载完成
- 需要网络连接

---

### 方案5：组合使用镜像和代理

如果镜像源仍然无法访问，可以组合使用镜像和代理：

1. 打开 `backend/.env` 文件
2. 添加以下配置：
   ```env
   HF_ENDPOINT=https://hf-mirror.com
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```
3. 保存文件
4. 重新启动服务器：
   ```bash
   python manage.py runserver
   ```

---

## 推荐操作流程

### 快速启动（不需要智能评分）

```bash
# 1. 编辑 .env 文件，添加：
# DISABLE_LLM_SCORING=True

# 2. 启动服务器
python manage.py runserver
```

### 完整功能（需要智能评分）

```bash
# 1. 编辑 .env 文件，添加：
# HF_ENDPOINT=https://hf-mirror.com

# 2. 启动服务器（首次会下载模型）
python manage.py runserver
```

### 使用代理下载模型

```bash
# 1. 编辑 .env 文件，添加：
# HF_ENDPOINT=https://hf-mirror.com
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890

# 2. 启动服务器
python manage.py runserver
```

### 手动下载模型

```bash
# 1. 运行下载脚本
python download_model.py

# 2. 等待下载完成

# 3. 启动服务器
python manage.py runserver
```

---

## 验证配置

### 检查 .env 文件

确保 `.env` 文件包含以下配置之一：

**禁用智能评分：**
```env
DISABLE_LLM_SCORING=True
```

**使用镜像：**
```env
HF_ENDPOINT=https://hf-mirror.com
```

**使用代理：**
```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 检查模型是否已下载

模型会被缓存到以下位置：
- Windows: `C:\Users\<用户名>\.cache\huggingface\hub\`
- Linux/Mac: `~/.cache/huggingface/hub/`

如果模型已下载，再次启动服务器时会直接使用缓存，不会重新下载。

---

## 常见问题

### Q1: 下载模型需要多长时间？

A: 取决于网络速度，通常需要 5-15 分钟。模型大小约 400MB。

### Q2: 模型下载失败怎么办？

A: 尝试以下方法：
1. 检查网络连接
2. 使用镜像源（方案2）
3. 配置代理（方案3）
4. 禁用智能评分（方案1）

### Q3: 可以在禁用智能评分后启用吗？

A: 可以。修改 `.env` 文件中的 `DISABLE_LLM_SCORING=False`，然后重启服务器即可。

### Q4: 模型下载到哪里了？

A: 模型会被缓存到：
- Windows: `C:\Users\<用户名>\.cache\huggingface\hub\`
- Linux/Mac: `~/.cache/huggingface/hub/`

### Q5: 如何清理模型缓存？

A: 删除缓存目录：
```bash
# Windows
rmdir /s /q %USERPROFILE%\.cache\huggingface\hub

# Linux/Mac
rm -rf ~/.cache/huggingface/hub
```

### Q6: 智能评分功能是必须的吗？

A: 不是必须的。禁用后，系统仍然可以正常运行，只是无法使用智能评分功能。

---

## 技术说明

### 模型懒加载

系统使用懒加载机制，只有在第一次使用智能评分功能时才会加载模型。这样可以：
- 加快服务器启动速度
- 节省内存资源
- 避免不必要的模型加载

### 模型缓存

模型会被缓存到本地，下次使用时直接从缓存加载，无需重新下载。

### 错误处理

如果模型加载失败，系统会返回友好的错误信息，不会影响其他功能。

---

## 联系支持

如果以上方案都无法解决问题，请：
1. 检查网络连接
2. 查看完整的错误日志
3. 联系技术支持

---

## 更新日志

- 2026-02-12: 添加智能评分禁用功能
- 2026-02-12: 添加镜像源支持
- 2026-02-12: 添加代理支持
- 2026-02-12: 创建模型下载脚本
