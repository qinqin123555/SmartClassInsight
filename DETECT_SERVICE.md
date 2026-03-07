# 检测服务常驻化改造

## 改动说明

将原来每次请求启动Python进程的方式改为常驻Flask服务，模型只加载一次，大幅提升检测速度。

## 架构变化

**之前**: 前端 → Spring Boot → 启动Python进程 → 加载模型 → 检测 → 返回结果（慢）

**现在**: 前端 → Spring Boot → HTTP请求 → Flask常驻服务（模型已加载）→ 返回结果（快）

## 启动步骤

### 1. 安装Flask依赖
```bash
pip install flask
```

### 2. 启动检测服务（必须先启动）
Windows:
```bash
cd backend
start_detect_service.bat
```

Linux/Mac:
```bash
cd backend
chmod +x start_detect_service.sh
./start_detect_service.sh
```

### 3. 启动Spring Boot后端
```bash
cd backend
mvn spring-boot:run
```

### 4. 启动前端
```bash
cd frontend
npm run dev
```

## 配置说明

`backend/src/main/resources/application.yml`:
```yaml
detect:
  python:
    service:
      url: http://localhost:5001  # Flask服务地址
```

## 服务端口

- Flask检测服务: 5001
- Spring Boot后端: 8080
- Vue前端: 默认Vite端口

## 健康检查

访问 http://localhost:5001/health 检查服务状态
