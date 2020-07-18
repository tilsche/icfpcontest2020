#!/bin/sh

pip install --force-reinstall --no-index --find-links ./wheels .
echo "HI!"
pwd
ls -lha
echo $PATH
