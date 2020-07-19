#!/bin/sh

pwd
ls -lha
echo $PATH
py-zebra "$@" -v || echo "run error code: $?"
