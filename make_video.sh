#!/bin/bash

ffmpeg -framerate 30 -i $1/%05d.png -c:v libx264 -r 30 -pix_fmt yuv420p $1/out.mp4
