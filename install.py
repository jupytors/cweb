#!/usr/bin/env python3
"""
install.py - Crow Web 框架自动安装脚本
运行方式: python3 install.py
"""

import os
import shutil
import subprocess
import sys

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "lib")
CROW_DIR = os.path.join(BASE_DIR, "Crow")
ASIO_DIR = os.path.join(BASE_DIR, "asio")
SQLITECPP_DIR = os.path.join(BASE_DIR, "SQLiteCpp")
BUILD_DIR = os.path.join(BASE_DIR, "build")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def run(cmd, cwd=None, check=True):
    """执行命令并打印"""
    print(f"\n{'='*60}")
    print(f"[RUN] {cmd}")
    print(f"[CWD] {cwd or BASE_DIR}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if check and result.returncode != 0:
        print(f"[ERROR] 命令执行失败，返回码: {result.returncode}")
        sys.exit(1)
    return result


def main():
    print("=" * 60)
    print("  Crow Web 框架自动安装脚本")
    print("=" * 60)

    # 1. 下载 Crow (standalone 版本，不需要 Boost)
    if not os.path.exists(CROW_DIR):
        print("\n[1/6] 下载 Crow...")
        run("git clone https://github.com/CrowCpp/Crow.git", cwd=BASE_DIR)
    else:
        print("\n[1/6] Crow 目录已存在，跳过下载")

    # 2. 下载 Asio (Crow 的依赖)
    if not os.path.exists(ASIO_DIR):
        print("\n[2/6] 下载 Asio...")
        run("git clone https://github.com/chriskohlhoff/asio.git", cwd=BASE_DIR)
    else:
        print("\n[2/6] Asio 目录已存在，跳过下载")

    # 3. 下载并编译 SQLiteCpp
    if not os.path.exists(SQLITECPP_DIR):
        print("\n[3/6] 下载 SQLiteCpp...")
        run("git clone https://github.com/SRombauts/SQLiteCpp.git", cwd=BASE_DIR)
    else:
        print("\n[3/6] SQLiteCpp 目录已存在，跳过下载")

    print("\n[3/6] 编译 SQLiteCpp...")
    sqlite_build = os.path.join(SQLITECPP_DIR, "build")
    os.makedirs(sqlite_build, exist_ok=True)
    run(f"cmake .. -DSQLITECPP_BUILD_EXAMPLES=OFF -DSQLITECPP_BUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX={LIB_DIR}", cwd=sqlite_build)
    run("make -j$(nproc)", cwd=sqlite_build)
    run("make install", cwd=sqlite_build)

    # 4. 创建 lib 目录结构
    print("\n[4/6] 创建 lib 目录结构...")
    os.makedirs(os.path.join(LIB_DIR, "include"), exist_ok=True)
    os.makedirs(os.path.join(LIB_DIR, "lib"), exist_ok=True)

    # 复制 Crow 头文件到 lib/include
    crow_include_src = os.path.join(CROW_DIR, "include")
    if os.path.exists(crow_include_src):
        for f in os.listdir(crow_include_src):
            src = os.path.join(crow_include_src, f)
            dst = os.path.join(LIB_DIR, "include", f)
            if os.path.isdir(src):
                os.system(f"cp -r {src} {dst}")
            else:
                os.system(f"cp {src} {dst}")

    # 复制 Asio 头文件
    asio_include_src = os.path.join(ASIO_DIR, "asio", "include")
    # 复制 asio.hpp 到 include 根目录
    shutil.copy(os.path.join(asio_include_src, "asio.hpp"), os.path.join(LIB_DIR, "include"))
    # 复制 asio 子目录
    asio_sub_src = os.path.join(asio_include_src, "asio")
    asio_sub_dst = os.path.join(LIB_DIR, "include", "asio")
    if os.path.exists(asio_sub_src):
        shutil.copytree(asio_sub_src, asio_sub_dst, dirs_exist_ok=True)

    # 复制 SQLiteCpp 头文件
    sqlitecpp_include_src = os.path.join(SQLITECPP_DIR, "include")
    if os.path.exists(sqlitecpp_include_src):
        os.system(f"cp -r {sqlitecpp_include_src}/* {LIB_DIR}/include/")

    # 复制 SQLiteCpp 库
    sqlite_lib_src = os.path.join(sqlite_build, "libSQLiteCpp.a")
    if os.path.exists(sqlite_lib_src):
        os.system(f"cp {sqlite_lib_src} {LIB_DIR}/lib/")
    sqlite3_lib_src = os.path.join(sqlite_build, "sqlite3", "libsqlite3.a")
    if os.path.exists(sqlite3_lib_src):
        os.system(f"cp {sqlite3_lib_src} {LIB_DIR}/lib/")

    # 5. 创建 main.cpp
    print("\n[5/6] 创建 main.cpp...")
    main_cpp = '''#include "crow.h"
#include "SQLiteCpp/SQLiteCpp.h"
#include <iostream>

int main()
{
    std::string current_dir = getcwd(NULL, 0);
    std::string templates_dir = current_dir.substr(0, current_dir.find_last_of("/")) + "/templates/";
    crow::mustache::set_global_base(templates_dir);

    std::cout << "=== SQLite 测试 ===" << std::endl;
    try {
        SQLite::Database db("test.db", SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE);
        db.exec("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)");
        db.exec("DELETE FROM users");
        db.exec("INSERT INTO users (name, age) VALUES ('Alice', 25)");
        db.exec("INSERT INTO users (name, age) VALUES ('Bob', 30)");
        db.exec("INSERT INTO users (name, age) VALUES ('Charlie', 22)");

        SQLite::Statement query(db, "SELECT id, name, age FROM users");
        while (query.executeStep()) {
            std::cout << "  用户: id=" << query.getColumn(0) << ", name=" << query.getColumn(1) << ", age=" << query.getColumn(2) << std::endl;
        }
        std::cout << "SQLite 测试通过！" << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "SQLite 错误: " << e.what() << std::endl;
        return 1;
    }

    crow::SimpleApp app;

    CROW_ROUTE(app, "/")([](){
        crow::json::wvalue ctx;
        ctx["title"] = "Crow + SQLite";
        ctx["items"] = crow::json::wvalue::list({
            {{"name", "首页"}, {"url", "/"}},
            {{"name", "API"}, {"url", "/api"}},
            {{"name", "数据库"}, {"url", "/db"}}
        });
        ctx["show"] = true;
        return crow::mustache::load("index.html").render(ctx);
    });

    CROW_ROUTE(app, "/api")([](){
        crow::json::wvalue x;
        x["message"] = "Hello from Crow!";
        x["framework"] = "Crow C++ Web Framework";
        x["database"] = "SQLite3";
        x["status"] = "running";
        return x;
    });

    CROW_ROUTE(app, "/db")([](){
        crow::json::wvalue ctx;
        try {
            SQLite::Database db("test.db", SQLite::OPEN_READONLY);
            SQLite::Statement query(db, "SELECT id, name, age FROM users");
            crow::json::wvalue::list users;
            while (query.executeStep()) {
                crow::json::wvalue user;
                user["id"] = query.getColumn(0).getInt();
                user["name"] = query.getColumn(1).getString();
                user["age"] = query.getColumn(2).getInt();
                users.push_back(std::move(user));
            }
            ctx["users"] = std::move(users);
            ctx["count"] = (int)users.size();
        } catch (const std::exception& e) {
            ctx["error"] = e.what();
        }
        ctx["title"] = "数据库查询";
        ctx["show"] = true;
        return crow::mustache::load("db.html").render(ctx);
    });

    std::cout << "Crow 服务器启动: http://0.0.0.0:18080" << std::endl;
    app.port(18080).multithreaded().run();
}
'''
    with open(os.path.join(BASE_DIR, "main.cpp"), "w") as f:
        f.write(main_cpp)

    # 6. 创建 CMakeLists.txt
    print("\n[6/6] 创建 CMakeLists.txt...")
    cmake_txt = f'''cmake_minimum_required(VERSION 3.18)
project(CrowWeb)

add_executable(main main.cpp)
target_compile_features(main PRIVATE cxx_std_17)

# 头文件路径
include_directories("{LIB_DIR}/include")
include_directories("{BASE_DIR}")

# 库路径
link_directories("{LIB_DIR}/lib")

# pthread
find_package(Threads REQUIRED)
target_link_libraries(main PRIVATE
    Threads::Threads
    {LIB_DIR}/lib/libSQLiteCpp.a
    {LIB_DIR}/lib/libsqlite3.a
    dl
)
'''
    with open(os.path.join(BASE_DIR, "CMakeLists.txt"), "w") as f:
        f.write(cmake_txt)

    # 创建 templates 目录和模板文件
    print("\n[EXTRA] 创建 templates 目录...")
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .card {
            background: #fff;
            border-radius: 16px;
            padding: 48px;
            box-shadow: 0 20px 60px rgba(0,0,0,.3);
            text-align: center;
        }
        h1 { color: #1a1a2e; font-size: 2.5em; margin-bottom: 16px; }
        p { color: #666; font-size: 1.2em; margin-bottom: 24px; }
        ul { list-style: none; padding: 0; }
        li { display: inline-block; margin: 0 10px; }
        a { color: #1a73e8; text-decoration: none; font-size: 1.1em; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Crow Web</h1>
        <p>C++ Web 框架 Crow + SQLite3 运行成功！</p>
        <ul>
            {{#items}}
            <li><a href="{{url}}">{{name}}</a></li>
            {{/items}}
        </ul>
        {{#show}}
        <p>Mustache 模板渲染正常！</p>
        {{/show}}
    </div>
</body>
</html>
'''
    with open(os.path.join(TEMPLATES_DIR, "index.html"), "w") as f:
        f.write(index_html)

    db_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        .card {
            background: #fff;
            border-radius: 16px;
            padding: 48px;
            box-shadow: 0 20px 60px rgba(0,0,0,.3);
            text-align: center;
            min-width: 400px;
        }
        h1 { color: #1a1a2e; font-size: 2em; margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background: #667eea; color: white; }
        tr:nth-child(even) { background: #f5f5f5; }
        a { color: #1a73e8; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>{{title}}</h1>
        {{#error}}
        <p style="color: red;">错误: {{error}}</p>
        {{/error}}
        {{^error}}
        <p>共有 {{count}} 个用户</p>
        <table>
            <tr><th>ID</th><th>姓名</th><th>年龄</th></tr>
            {{#users}}
            <tr><td>{{id}}</td><td>{{name}}</td><td>{{age}}</td></tr>
            {{/users}}
        </table>
        {{/error}}
        <p style="margin-top: 24px;"><a href="/">返回首页</a></p>
    </div>
</body>
</html>
'''
    with open(os.path.join(TEMPLATES_DIR, "db.html"), "w") as f:
        f.write(db_html)

    # 7. 创建 README.md
    print("\n[7/7] 创建 README.md...")
    readme_content = '''# 图书管理系统

基于 Crow C++ Web 框架的图书管理系统，使用 SQLite 数据库存储数据，Mustache 模板渲染页面。

## 技术栈

- **后端框架**: Crow C++ Web Framework
- **数据库**: SQLite3 + SQLiteCpp
- **模板引擎**: Mustache
- **编译器**: GCC (C++17)

## 快速开始

```bash
# 运行安装脚本
python3 install.py

# 或手动编译
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
./main
```

## 访问地址

- 首页: http://localhost:18080
- API: http://localhost:18080/api
- 图书列表: http://localhost:18080/books
'''
    with open(os.path.join(BASE_DIR, "README.md"), "w") as f:
        f.write(readme_content)

    # 编译
    print("\\n[BUILD] 编译项目...")
    os.makedirs(BUILD_DIR, exist_ok=True)
    run("cmake .. -DCMAKE_BUILD_TYPE=Release", cwd=BUILD_DIR)
    run("make -j$(nproc)", cwd=BUILD_DIR)
    run("chmod +x main", cwd=BUILD_DIR)

    print("\\n" + "=" * 60)
    print("  安装完成！")
    print("=" * 60)
    print(f"""
项目结构:
  {BASE_DIR}/
  ├── lib/              # 库文件目录
  │   ├── include/      # Crow + Asio + SQLiteCpp 头文件
  │   ├── Crow/             # Crow 源码
  │   ├── asio/             # Asio 源码
  │   ├── SQLiteCpp/        # SQLiteCpp 源码
  │   └── lib/          # 静态库
  ├── templates/        # Mustache 模板
  ├── main.cpp          # 示例代码
  ├── CMakeLists.txt    # CMake 配置
  ├── README.md         # 项目说明
  └── build/            # 构建目录
      └── main          # 可执行文件

运行:
  cd {BASE_DIR}/build
  ./main

  访问 http://localhost:18080
  API http://localhost:18080/api
  数据库 http://localhost:18080/db
""")
    yml="""
autoOpen: false
apps:
  - name: crow-web
    description: Crow C++ Web 服务器
    root: ./web/
    run: |
      pkill -f "./main" 2>/dev/null; sleep 1;
      mkdir -p build && cd build &&
      cmake -DCMAKE_BUILD_TYPE=Release .. &&
      cmake --build . --config Release &&
      chmod +x ./main &&
      ./main
    port: 18080
    autoOpen: true
  """
    with open(f"/workspace/.vscode/preview.yml", "w") as f:
      f.write(yml)


if __name__ == "__main__":
    main()
