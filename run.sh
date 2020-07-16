#!/bin/sh

pwd
ls -lha
echo $PATH
app "$@" || echo "run error code: $?"
