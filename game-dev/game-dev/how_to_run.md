# 项目启动指南

## 环境要求

- Python 3.10+
- Node.js 18+

---

## 后端启动（Flask API）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python -m interfaces.web_api.app
```

后端默认运行在 `http://127.0.0.1:5000`

---

## 前端启动（Vue + Vite）

### 1. 进入前端目录

```bash
cd interfaces/client
```

### 2. 安装依赖

```bash
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

前端默认运行在 `http://localhost:5173`

---

## 其他命令

| 命令 | 说明 |
|------|------|
| `npm run build` | 构建前端生产版本 |
| `npm run preview` | 预览构建后的版本 |

---

## 快速启动（两个终端）

**终端 1 - 后端：**
```bash
python interfaces/web_api/app.py
```

**终端 2 - 前端：**
```bash
cd interfaces/client && npm run dev
```
