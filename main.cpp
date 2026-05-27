#include "crow.h"
#include "SQLiteCpp/SQLiteCpp.h"
#include <iostream>

int main()
{
    std::string current_dir = getcwd(NULL, 0);
    std::string templates_dir = current_dir.substr(0, current_dir.find_last_of("/")) + "/templates/";
    crow::mustache::set_global_base(templates_dir);
    std::cout << "=== SQLite 测试 ===" << std::endl;
    try {
        SQLite::Database db("../test.db", SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE);
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
            SQLite::Database db("../test.db", SQLite::OPEN_READONLY);
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
