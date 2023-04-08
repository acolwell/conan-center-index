cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(OpenImageIO REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)

message("WOOT ${fmt_FOUND} - ${fmt_INCLUDE_DIRS} - ${fmt_VERSION_STRING}")

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} OpenImageIO::OpenImageIO )
#TODO: Replace ${fmt_PACKAGE_FOLDER_RELEASE}/include with ${fmt_INCLUDE_DIRS} once conan generates it properly.
target_include_directories(${PROJECT_NAME} PUBLIC ${fmt_PACKAGE_FOLDER_RELEASE}/include)
