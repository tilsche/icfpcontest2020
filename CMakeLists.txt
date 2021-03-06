cmake_minimum_required(VERSION 3.11)
project(icfp VERSION 20.2.0)

# configure Nitro submodule
add_subdirectory(lib/nitro)
add_subdirectory(lib/wxWidgets)

# TODO Maybe revert this with CMP0077 some time in the future
set(FMT_INSTALL ON CACHE BOOL "If you can read this, something is wrong with CMake.")
add_subdirectory(lib/fmt EXCLUDE_FROM_ALL)

# find external dependencies
#find_package(Boost REQUIRED COMPONENTS system program_options filesystem)
set(THREADS_PREFER_PTHREAD_FLAG true)
find_package(Threads REQUIRED)

find_package(OpenSSL REQUIRED)

set(SOURCE_FILES
    app/main.cpp
    app/modem.cpp
)

add_executable(solver ${SOURCE_FILES})

target_link_libraries(solver
    PRIVATE
        Nitro::log
        Nitro::env
        Threads::Threads
        fmt::fmt-header-only
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

add_executable(galaxy app/galaxy.cpp app/modem.cpp)

target_link_libraries(galaxy
    PRIVATE
        Nitro::core
        Nitro::env
        wx::net
        wx::core
        wx::base
        wx::aui
        fmt::fmt-header-only
        OpenSSL::SSL
        OpenSSL::Crypto
)



target_compile_features(galaxy
    PRIVATE
        cxx_std_20
)

# define feature test macro
target_compile_definitions(galaxy PRIVATE CPPHTTPLIB_OPENSSL_SUPPORT)

# build Debug with -Werror
target_compile_options(solver PRIVATE -Wall -pedantic -Wextra)


install(TARGETS solver RUNTIME DESTINATION bin)
