#!/bin/sh

ls -lhaR
cat dummy-submodule/dummy.txt
cd build
./main "$@" || echo "run error code: $?"
