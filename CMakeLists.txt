cmake_minimum_required(VERSION 3.18)
project(CrowWeb)

add_executable(main main.cpp)
target_compile_features(main PRIVATE cxx_std_17)

# 头文件路径
include_directories("./lib/include")
include_directories(".")

# 库路径
link_directories("${CMAKE_SOURCE_DIR}/lib/lib")

# pthread
find_package(Threads REQUIRED)
target_link_libraries(main PRIVATE 
    Threads::Threads 
    ${CMAKE_SOURCE_DIR}/lib/lib/libSQLiteCpp.a 
    ${CMAKE_SOURCE_DIR}/lib/lib/libsqlite3.a 
    dl
)
