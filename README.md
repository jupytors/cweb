# 图书管理系统需求文档

## 项目概述

基于 Crow C++ Web 框架的图书管理系统，使用 SQLite 数据库存储数据，Mustache 模板渲染页面。

## 技术栈

- **后端框架**: Crow C++ Web Framework
- **数据库**: SQLite3 + SQLiteCpp
- **模板引擎**: Mustache
- **编译器**: GCC (C++17)

## 数据库设计

### 表: books (图书表)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 图书ID | 主键、自增 |
| isbn | TEXT | ISBN 编号 | 唯一、非空 |
| title | TEXT | 书名 | 非空 |
| author | TEXT | 作者 | 非空 |
| publisher | TEXT | 出版社 | 可空 |
| category | TEXT | 分类 | 可空 |
| price | REAL | 价格 | 默认 0.00 |
| stock | INTEGER | 库存数量 | 默认 0 |
| description | TEXT | 简介 | 可空 |
| cover_url | TEXT | 封面图片URL | 可空 |
| created_at | TEXT | 添加时间 | 默认当前时间 |
| updated_at | TEXT | 更新时间 | 自动更新 |

### 表: users (用户表)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 用户ID | 主键、自增 |
| username | TEXT | 用户名 | 唯一、非空 |
| password | TEXT | 密码(哈希) | 非空 |
| email | TEXT | 邮箱 | 可空 |
| phone | TEXT | 电话 | 可空 |
| role | TEXT | 角色 | admin/user |
| created_at | TEXT | 注册时间 | 默认当前时间 |

### 表: borrow_records (借阅记录表)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INTEGER | 记录ID | 主键、自增 |
| book_id | INTEGER | 图书ID | 外键 |
| user_id | INTEGER | 用户ID | 外键 |
| borrow_date | TEXT | 借书日期 | 非空 |
| due_date | TEXT | 应还日期 | 非空 |
| return_date | TEXT | 实际归还日期 | 可空 |
| status | TEXT | 状态 | borrowed/returned/overdue |

## API 接口设计

### 图书管理

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/books` | GET | 获取图书列表 | page, limit, search, category |
| `/api/books/<id>` | GET | 获取图书详情 | - |
| `/api/books` | POST | 添加图书 | title, author, isbn... |
| `/api/books/<id>` | PUT | 更新图书 | title, author, stock... |
| `/api/books/<id>` | DELETE | 删除图书 | - |
| `/api/books/<id>/borrow` | POST | 借阅图书 | user_id, days |
| `/api/books/<id>/return` | POST | 归还图书 | user_id |

### 用户管理

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/users` | GET | 获取用户列表 | page, limit |
| `/api/users/<id>` | GET | 获取用户详情 | - |
| `/api/users` | POST | 添加用户 | username, password, email... |
| `/api/users/<id>` | PUT | 更新用户 | email, phone... |
| `/api/users/<id>` | DELETE | 删除用户 | - |

### 借阅管理

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/borrow` | GET | 获取借阅记录 | user_id, status |
| `/api/borrow/<id>/return` | POST | 归还图书 | - |
| `/api/borrow/overdue` | GET | 获取逾期记录 | - |

### 认证

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/login` | POST | 用户登录 | username, password |
| `/api/logout` | POST | 用户登出 | - |
| `/api/register` | POST | 用户注册 | username, password, email |

## 页面设计

### 前台页面

1. **首页** (`/`)
   - 系统标题
   - 搜索框（按书名、作者、ISBN 搜索）
   - 图书分类导航
   - 热门图书推荐
   - 最新入库图书

2. **图书列表页** (`/books`)
   - 分类筛选
   - 排序选项（按时间、价格、热度）
   - 分页导航
   - 图书卡片展示（封面、书名、作者、价格、库存状态）

3. **图书详情页** (`/books/<id>`)
   - 图书封面大图
   - 完整信息（书名、作者、ISBN、出版社、分类）
   - 库存状态
   - 借阅/预约按钮
   - 相关图书推荐

4. **个人中心** (`/user`)
   - 个人信息
   - 借阅历史
   - 当前借阅
   - 逾期提醒

### 后台管理页面

1. **管理首页** (`/admin`)
   - 统计概览（图书总数、用户总数、借出数量、逾期数量）
   - 快捷操作入口

2. **图书管理** (`/admin/books`)
   - 图书列表（支持增删改查）
   - 批量导入/导出
   - 库存管理

3. **用户管理** (`/admin/users`)
   - 用户列表
   - 角色权限管理
   - 禁用/启用用户

4. **借阅管理** (`/admin/borrow`)
   - 借阅记录列表
   - 续借操作
   - 逾期处理

## 功能模块

### 1. 图书管理
- 添加、编辑、删除图书
- 批量导入（Excel/CSV）
- 库存预警（低于阈值提醒）
- 分类管理

### 2. 用户管理
- 用户注册、登录
- 个人信息修改
- 密码修改
- 管理员功能

### 3. 借阅管理
- 借书（检查库存、设置期限）
- 还书（自动计算逾期）
- 续借（限一次，延长7天）
- 逾期处理（滞纳金计算）

### 4. 搜索功能
- 全文搜索（书名、作者、ISBN）
- 分类筛选
- 排序（时间、价格、热度）

### 5. 数据统计
- 图书借阅排行
- 用户借阅排行
- 图书分类分布
- 逾期率统计

## 页面模板文件

```
templates/
├── base.html              # 基础模板（头部、底部）
├── index.html             # 首页
├── books/
│   ├── list.html          # 图书列表
│   └── detail.html        # 图书详情
├── user/
│   ├── login.html         # 登录页
│   ├── register.html     # 注册页
│   └── profile.html       # 个人中心
└── admin/
    ├── dashboard.html     # 管理后台首页
    ├── book_form.html     # 图书编辑表单
    └── user_list.html     # 用户列表
```

## 配置文件

### config.json

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 18080
  },
  "database": {
    "path": "library.db"
  },
  "borrow": {
    "default_days": 30,
    "max_renew": 1,
    "overdue_fee_per_day": 0.5
  },
  "stock": {
    "low_threshold": 5
  }
}
```

## 安全考虑

1. **密码存储**: 使用 bcrypt/scrypt 哈希存储
2. **SQL注入**: 使用参数化查询
3. **XSS攻击**: 模板引擎自动转义
4. **CSRF**: 令牌验证
5. **权限控制**: 管理员与普通用户分离

## 扩展功能（可选）

1. **邮件通知**: 借书成功、还书提醒、逾期通知
2. **数据备份**: 自动备份数据库
3. **API文档**: Swagger/OpenAPI
4. **日志记录**: 操作日志、错误日志
5. **图片上传**: 图书封面上传

## 开发计划

### Phase 1: 基础框架
- [ ] 项目初始化
- [ ] 数据库设计
- [ ] 基础CRUD API

### Phase 2: 前端页面
- [ ] 模板开发
- [ ] 页面样式
- [ ] 交互功能

### Phase 3: 业务功能
- [ ] 借阅流程
- [ ] 用户认证
- [ ] 后台管理

### Phase 4: 完善优化
- [ ] 安全加固
- [ ] 性能优化
- [ ] 文档完善


当前目录结构：
# Crow C++ Web Framework



基于 Crow 框架的 C++ Web 服务器项目

## 目录结构

```
web/
├── main.cpp              # 主程序入口，包含路由和业务逻辑
├── CMakeLists.txt        # CMake 构建配置文件
├── test.db               # SQLite 数据库文件
├── templates/            # Mustache 模板目录
│   ├── index.html        # 首页模板
│   └── db.html           # 数据库页面模板
├── lib/                  # 第三方依赖库
│   ├── asio/             # Asio 网络库（头文件）
│   ├── boost/            # Boost 库（头文件）
│   ├── Crow/             # Crow 框架头文件
│   ├── SQLiteCpp/        # SQLite C++ 封装库
│   └── C/                # SQLite C 库
├── build/                # 编译输出目录
│   └── main              # 编译生成的可执行文件
└── .vscode/              # VSCode 配置
    └── preview.yml       # Preview 插件配置
```

## 主要文件说明

| 文件/目录 | 说明 |
