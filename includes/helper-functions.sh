#!/bin/sh

# Define the global bundler version.
bundler_version="aries";

################################################################################
# Global Variables
################################################################################
__data="$HOME/Library/Application Support/Alfred 2/Workflow Data/alfred.bundler-$bundler_version"
__cache="$HOME/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/alfred.bundler-$bundler_version"


################################################################################
# Functions
################################################################################

# Make a directory if it doesn't exist
function dir {
  if [ ! -d "$1" ]; then
    mkdir "$1"
  fi
}

# Just grabs something via cURL
function get {
  curl -sL "$1" > "$2"
}

function cleanUp {
  rm -fR "$cache/$now"
}