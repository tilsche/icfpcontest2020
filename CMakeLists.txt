cmake_minimum_required(VERSION 3.11)
project(icfp VERSION 20.2.0)

# configure Nitro submodule
add_subdirectory(lib/nitro)
add_subdirectory(lib/wxWidgets)

# find external dependencies
#find_package(Boost REQUIRED COMPONENTS system program_options filesystem)
set(THREADS_PREFER_PTHREAD_FLAG true)
find_package(Threads REQUIRED)

set(SOURCE_FILES
    app/main.cpp
)

add_executable(solver ${SOURCE_FILES})

target_link_libraries(solver
    PRIVATE
        Nitro::log
        Nitro::env
        Threads::Threads
)

target_include_directories(solver PRIVATE
    app
)

# define list of C++ features needed for compilation
target_compile_features(solver
    PRIVATE
        cxx_std_20
)

add_executable(pow2 app/pow2.cpp)

target_link_libraries(pow2
    PRIVATE
        Nitro::core
)

target_compile_features(pow2
    PRIVATE
        cxx_std_20
)


#find_package(wxWidgets REQUIRED COMPONENTS core base)

add_executable(galaxy app/galaxy.cpp)

target_link_libraries(galaxy
    PRIVATE
        Nitro::core
        wx::net
        wx::core
        wx::base
        wx::aui
)

target_compile_features(galaxy
    PRIVATE
        cxx_std_20
)

# define feature test macro
# target_compile_definitions(solver PRIVATE _GNU_SOURCE)

# build Debug with -Werror
target_compile_options(solver PRIVATE -Wall -pedantic -Wextra)


install(TARGETS solver RUNTIME DESTINATION bin)
