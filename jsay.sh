i#!/bin/sh
TMP=/tmp/jsay.wav
echo "$1" | open_jtalk \
-m /usr/share/hts-voice/mei/mei_normal.htsvoice \
-x /var/lib/mecab/dic/open-jtalk/naist-jdic \
-ow $TMP && \
aplay --quiet $TMP
rm -f $TMP
