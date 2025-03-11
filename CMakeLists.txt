cmake_minimum_required(VERSION 3.14)
project(Nomad)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE release CACHE STRING "Choose build type (debug or release)" FORCE)
endif()

set(BUILD_DIR ${CMAKE_BINARY_DIR})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BUILD_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${BUILD_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${BUILD_DIR}/lib)

set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O2")

add_executable(Nomad src/cpp/main.cpp)

target_include_directories(Nomad PRIVATE ${CMAKE_SOURCE_DIR}/include)

add_custom_command(TARGET Nomad POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/data/champions.json
        ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/champions.json
)