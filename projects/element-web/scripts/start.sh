#!/bin/sh

#
# This script is used by deployment to replace variables in the index.html
# file. This needs to be replaced in the actual file due to them replacing
# some META tags that need to be in the actual file.
# Afterwards, starts the nginx server.
#

sh /scripts/replace_vars.sh /app/index.html


# Also write the version to a file
if [ -n "$VERSION" ]; then
  echo "$VERSION" > /usr/share/nginx/html/version
fi
