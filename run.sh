#!/bin/sh

pwd
ls -lha
echo $PATH
py-zebra "$@" -v debug || echo "run error code: $?"
