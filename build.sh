#!/bin/sh

pip install --no-index --find-links ./wheels icfpcontest2020
echo "HI!"
pwd
ls -lha
echo $PATH
