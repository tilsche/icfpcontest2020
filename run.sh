#!/bin/sh

cd build
cat dummy-submodule/dummy.txt
./main "$@" || echo "run error code: $?"
