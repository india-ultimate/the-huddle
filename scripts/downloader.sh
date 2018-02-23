#!/bin/bash

pushd `dirname $0`/..
wget -m --accept-regex="the-huddle-issue" https://www.usaultimate.org/multimedia/the_huddle/issues.aspx
popd
