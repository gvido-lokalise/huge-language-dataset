#!/bin/sh
# Usage: ./format_pypit.sh

sed -ie "s/'.*IS AN INVALID TARGET LANGUAGE.*/''/gm;/USING 2 LETTER ISO/d;/MAY HAVE NO CONTENT'/d" *.yml
