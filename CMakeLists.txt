cmake_minimum_required(VERSION 3.13.4)

project(LabelNameGenerator)

find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

add_subdirectory(LabelNameGenerator)
