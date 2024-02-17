cmake_minimum_required(VERSION 3.6)

include(RezBuild)

file(GLOB_RECURSE py_files "src/python/*.py")

rez_install_files(
    FILES ${py_files}
    RELATIVE src/python
    DESTINATION python
)

# Handle installing houdini/ files.
file(GLOB_RECURSE houdini_files RELATIVE "${CMAKE_SOURCE_DIR}" "src/houdini/*")

rez_install_files(
    ${houdini_files}
    RELATIVE src/houdini
    DESTINATION houdini
)
