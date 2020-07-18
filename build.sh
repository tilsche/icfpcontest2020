#!/bin/sh

pip install --no-index --find-links ./wheels zebv
echo "HI!"
pwd
ls -lha
echo $PATH
