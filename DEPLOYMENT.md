# 基于协同过滤的程序员八股文答题训练系统 - 部署文档

## 目录

1. [系统要求](#系统要求)
2. [本地开发环境搭建](#本地开发环境搭建)
3. [Docker 部署](#docker-部署)
4. [生产环境部署](#生产环境部署)
5. [常见问题](#常见问题)

---

## 系统要求

### 后端
- Python 3.11+
- MySQL 8.0+
- Redis (可选，用于缓存)

### 前端
- Node.js 20.19.0+ 或 >= 22.12.0
- npm 或 yarn

### Docker 部署
- Docker 20.10+
- Docker Compose 2.0+

---

## 本地开发环境搭建

### 1. 克隆项目

```bash
git clone <repository-url>
cd 04_Interview_system
```

### 2. 后端环境配置

#### 2.1 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DB_NAME=interview_system
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

SECRET_KEY=your-secret-key-here
DEBUG=True

DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
```

#### 2.4 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 2.5 创建超级用户

```bash
python manage.py createsuperuser
```

#### 2.6 启动开发服务器

```bash
python manage.py runserver
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端环境配置

#### 3.1 安装依赖

```bash
cd frontend
npm install
```

#### 3.2 配置 API 地址

编辑 `frontend/.env` 文件：

```env
VITE_API_URL=http://localhost:8000/api
```

#### 3.3 启动开发服务器

```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

---

## Docker 部署

### 1. 准备环境变量

在项目根目录创建 `.env` 文件：

```env
DB_NAME=interview_system
DB_USER=root
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=3306

SECRET_KEY=your-production-secret-key
DEBUG=False

DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
```

### 2. 构建并启动服务

```bash
docker-compose up -d
```

### 3. 查看服务状态

```bash
docker-compose ps
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 5. 执行数据库迁移

```bash
docker-compose exec backend python manage.py migrate
```

### 6. 创建超级用户

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 7. 停止服务

```bash
docker-compose down
```

### 8. 停止并删除所有数据

```bash
docker-compose down -v
```

---

## 生产环境部署

### 1. 使用 Nginx 反向代理

#### 1.1 安装 Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 1.2 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/interview-system`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 文档
    location /swagger/ {
        proxy_pass http://localhost:8000/swagger/;
        proxy_set_header Host $host;
    }

    location /redoc/ {
        proxy_pass http://localhost:8000/redoc/;
        proxy_set_header Host $host;
    }
}
```

#### 1.3 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/interview-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. 使用 Gunicorn 部署后端

#### 2.1 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2.2 创建 Systemd 服务

创建文件 `/etc/systemd/system/interview-backend.service`：

```ini
[Unit]
Description=Interview System Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 core.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 2.3 启动服务

```bash
sudo systemctl start interview-backend
sudo systemctl enable interview-backend
```

### 3. 使用 PM2 部署前端

#### 3.1 安装 PM2

```bash
npm install -g pm2
```

#### 3.2 构建前端

```bash
cd frontend
npm run build
```

#### 3.3 使用 PM2 启动

```bash
pm2 start npm --name "interview-frontend" -- start
pm2 save
pm2 startup
```

### 4. SSL 证书配置

使用 Let's Encrypt 免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 常见问题

### 1. 数据库连接失败

**问题**: `Can't connect to MySQL server`

**解决方案**:
- 检查 MySQL 服务是否运行
- 验证 `.env` 文件中的数据库配置
- 确保数据库用户有足够的权限

### 2. 前端无法连接后端 API

**问题**: `Network Error` 或 `CORS Error`

**解决方案**:
- 检查后端服务是否运行
- 验证 `VITE_API_URL` 配置
- 检查 CORS 配置

### 3. 评分功能不工作

**问题**: DeepSeek API 调用失败

**解决方案**:
- 验证 `DEEPSEEK_API_KEY` 配置
- 检查 API 密钥是否有效
- 查看后端日志获取详细错误信息

### 4. Docker 容器启动失败

**问题**: `Container exited with code 1`

**解决方案**:
- 查看容器日志：`docker-compose logs <service-name>`
- 检查环境变量配置
- 确保端口未被占用

### 5. 静态文件无法加载

**问题**: 404 错误

**解决方案**:
- 运行 `python manage.py collectstatic`
- 配置 Nginx 静态文件路径
- 检查文件权限

---

## 监控和维护

### 1. 日志管理

```bash
# 后端日志
tail -f /var/log/interview-backend.log

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. 数据库备份

```bash
# 备份数据库
docker-compose exec db mysqldump -u root -p interview_system > backup.sql

# 恢复数据库
docker-compose exec -T db mysql -u root -p interview_system < backup.sql
```

### 3. 更新代码

```bash
# 拉取最新代码
git pull

# 更新后端依赖
cd backend
pip install -r requirements.txt
python manage.py migrate

# 更新前端依赖
cd ../frontend
npm install
npm run build

# 重启服务
docker-compose restart
```

---

## 性能优化建议

1. **启用 Redis 缓存**: 减少数据库查询
2. **使用 CDN**: 加速静态文件加载
3. **数据库索引**: 优化常用查询
4. **负载均衡**: 使用多个后端实例
5. **监控工具**: 使用 Prometheus + Grafana 监控系统性能

---

## 安全建议

1. **定期更新**: 保持系统和依赖包最新
2. **强密码**: 使用复杂的数据库密码和 SECRET_KEY
3. **防火墙**: 限制不必要的端口访问
4. **HTTPS**: 始终使用 SSL/TLS 加密
5. **备份**: 定期备份数据库和重要文件

---

## 联系方式

如有问题，请联系项目维护者或提交 Issue。

---

*最后更新: 2026-02-02*
