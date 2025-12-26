# 服务器部署指南

## ✅ 服务器部署可行性

**好消息！这个项目完全可以在服务器上部署，不需要Chrome或浏览器依赖。**

### 🔧 技术原理

项目使用 **Kaleido** 引擎进行图像渲染：
- **Kaleido**: 纯Python跨平台图像渲染库
- **无需浏览器**: 不依赖Chrome、Firefox或任何浏览器
- **无需GUI**: 可以在无头服务器环境中运行
- **高兼容性**: 支持Linux、Windows、macOS等操作系统

## 🚀 服务器部署步骤

### 1. 系统要求

- **操作系统**: Linux/Windows/macOS
- **Python版本**: >= 3.9
- **内存**: 建议512MB以上
- **磁盘**: 100MB以上（不含生成的图表文件）

### 2. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/qingfeng0512/chart-mcp-server.git
cd chart-mcp-server

# 安装依赖
pip install -e .

# 或使用requirements.txt
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 后台运行
nohup python src/main_optimized.py > /var/log/chart-mcp-server.log 2>&1 &

# 或使用systemd服务
sudo systemctl start chart-mcp-server
```

### 4. 验证部署

```bash
# 检查进程
ps aux | grep main_optimized

# 检查端口
netstat -tlnp | grep 8080
netstat -tlnp | grep 8081
```

## 🌐 网络配置

### 端口说明

- **8080**: MCP服务端口（用于API调用）
- **8081**: 静态文件服务端口（用于访问生成的图片）

### 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 8080
sudo ufw allow 8081

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

### Nginx反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # MCP API代理
    location /mcp/ {
        proxy_pass http://127.0.0.1:8080/mcp/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态图片代理
    location /images/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
    }
}
```

## 📦 使用Docker部署（推荐）

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY images/ ./images/

EXPOSE 8080 8081

CMD ["python", "src/main_optimized.py"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t chart-mcp-server .

# 运行容器
docker run -d \
  --name chart-mcp \
  -p 8080:8080 \
  -p 8081:8081 \
  -v $(pwd)/images:/app/images \
  chart-mcp-server
```

## 🔐 安全配置

### 1. 访问控制

项目已内置访问控制：
- 仅允许访问`.png`文件
- 其他文件返回404错误

### 2. IP白名单（可选）

如需限制访问IP，可在Nginx层配置：

```nginx
location /mcp/ {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://127.0.0.1:8080/mcp/;
}
```

### 3. HTTPS配置

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # ... 其他配置同上
}
```

## 📊 监控和维护

### 1. 日志监控

```bash
# 实时查看日志
tail -f /var/log/chart-mcp-server.log

# 查看错误日志
grep ERROR /var/log/chart-mcp-server.log
```

### 2. 性能监控

```bash
# 查看内存使用
ps aux | grep main_optimized

# 查看磁盘使用
du -sh images/
```

### 3. 定期清理

```bash
# 清理7天前的图片文件
find images/ -name "*.png" -mtime +7 -delete

# 或添加定时任务
echo "0 2 * * * find /path/to/images/ -name '*.png' -mtime +7 -delete" | crontab -
```

## 🐛 常见问题

### Q1: 图像生成失败
```bash
# 检查kaleido安装
pip show kaleido

# 重新安装kaleido
pip install --upgrade kaleido
```

### Q2: 端口被占用
```bash
# 查找占用进程
lsof -i :8080
lsof -i :8081

# 杀死进程
kill -9 <PID>
```

### Q3: 权限错误
```bash
# 修复images目录权限
chmod 755 images/
chown -R $USER:$USER images/
```

### Q4: 内存不足
```bash
# 增加swap空间
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 💡 优化建议

### 1. 资源限制

```bash
# 限制内存使用
ulimit -v 524288

# 限制进程数
ulimit -u 1000
```

### 2. 缓存优化

可以考虑添加Redis缓存来存储频繁生成的图表。

### 3. 负载均衡

如果需要高可用，可以部署多个实例并使用Nginx负载均衡。

## 📞 技术支持

如遇问题，请检查：
1. 服务器日志文件
2. 依赖库版本兼容性
3. 系统资源使用情况
4. 网络和防火墙配置

---

**总结**: 这个项目设计时就考虑了服务器部署，使用Kaleido引擎无需浏览器依赖，可以轻松部署在任何Linux/Windows服务器上。
