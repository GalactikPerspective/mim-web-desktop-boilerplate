#!/usr/bin/env bash

# Initialize variables
target=""
env_file=""

# Parse command line arguments using getopts
while getopts ":e:" opt; do
  case $opt in
    e)
      env_file="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Shift to the next argument (the mandatory "target" argument)
shift $((OPTIND - 1))

# Check if the mandatory "target" argument is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 -e <env-file> <target>"
  exit 1
fi

target="$1"

# Load environment variables from the file specified by --env-file (if provided)
if [ -n "$env_file" ] && [ -f "$env_file" ]; then
  source "$env_file"
fi

# Set variables

# MIM_VAR_TITLE
if [ -n "$MIM_VAR_TITLE" ]; then
  ESCAPED_MIM_VAR_TITLE=$(echo $MIM_VAR_TITLE | sed 's/[\/&]/\\&/g')
  echo "Replacing MIM_VAR_TITLE: $ESCAPED_MIM_VAR_TITLE"
  sed -i -e "s/%MIM_VAR_TITLE%/$ESCAPED_MIM_VAR_TITLE/g" $target
fi

# MIM_VAR_TITLE
if [ -n "$MIM_VAR_DESCRIPTION" ]; then
  ESCAPED_MIM_VAR_DESCRIPTION=$(echo $MIM_VAR_DESCRIPTION | sed 's/[\/&]/\\&/g')
  echo "Replacing MIM_VAR_DESCRIPTION: $ESCAPED_MIM_VAR_DESCRIPTION"
  sed -i -e "s/%MIM_VAR_DESCRIPTION%/$ESCAPED_MIM_VAR_DESCRIPTION/g" $target
fi

# MIM_VAR_OG_FILE
if [ -n "$BASEDOMAIN" ] && [ -n "$MIM_VAR_OG_FILE" ]; then
  ESCAPED_MIM_VAR_OG_FILE=$(echo $BASEDOMAIN/$MIM_VAR_OG_FILE | sed 's/[\/&]/\\&/g')
  echo "Replacing MIM_VAR_OG_FILE: $ESCAPED_MIM_VAR_OG_FILE"
  sed -i -e "s/%MIM_VAR_OG_FILE%/$ESCAPED_MIM_VAR_OG_FILE/g" $target
fi

echo "Finished replacing vars in $target."
