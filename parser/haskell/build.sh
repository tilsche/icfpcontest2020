#!/bin/bash
# sudo apt-get install haskell-platform

cabal install JuicyPixels JuicyPixels-util errors extra groupBy
ghc parser.hs --make
