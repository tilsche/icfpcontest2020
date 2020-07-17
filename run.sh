#!/bin/sh

cd build
./solver "$@" || echo "run error code: $?"
