#!/bin/sh

cd build
ls -lhaR
cat dummy-submodule/dummy.txt
./main "$@" || echo "run error code: $?"
