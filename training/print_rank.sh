#!/bin/bash

config=${1}

sed -En 's/.*:(\s+((Rank)|([0-9]+)).*:\s+(.*):\s+(.*))/\1/p' ${config}/training.log
