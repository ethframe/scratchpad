cmake_minimum_required(VERSION 3.25.1)

project(astutil)

add_executable(example
    example.cc)

set_property(TARGET example PROPERTY CXX_STANDARD 17)

install(TARGETS
    example)
