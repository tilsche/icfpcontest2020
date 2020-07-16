#!/bin/sh

pwd
ls -lha
echo $PATH
py-zebra "$@" || echo "run error code: $?"
