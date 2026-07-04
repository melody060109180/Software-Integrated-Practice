# 在线商城桌面客户端

基于Electron开发的在线商城桌面应用程序。

## 功能特性

- **用户端**：浏览商品、购物车、下单、查看订单
- **商家端**：数据概览、商品管理、订单管理
- **管理员**：跳转到Web管理后台

## 技术栈

- **后端**：Django + Django REST Framework
- **前端**：Electron + Bootstrap 5
- **数据库**：SQLite

## 开发环境搭建

### 1. 后端启动

```bash
cd software_comprehensive_practice
pip install -r requirements.txt
python manage.py runserver
```

### 2. Electron启动

```bash
cd electron-shop
npm install
npm start
```

## 打包发布

```bash
cd electron-shop
npm run build:win    # Windows
npm run build:mac    # Mac
```

## 项目结构

```
electron-shop/
├── main.js              # Electron主进程
├── package.json         # 项目配置
├── renderer/            # 前端界面
│   ├── index.html       # 主页面
│   └── js/
│       └── app.js       # 前端逻辑
└── assets/              # 资源文件
```

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/users/login/ | POST | 用户登录 |
| /api/goods/ | GET | 商品列表 |
| /api/cart/ | GET | 购物车 |
| /api/cart/add/ | POST | 加入购物车 |
| /api/orders/ | GET | 订单列表 |
| /api/merchants/dashboard/ | GET | 商家数据概览 |

## 测试账号

- 管理员：admin / admin123
- 普通用户：需注册
- 商家：需注册
