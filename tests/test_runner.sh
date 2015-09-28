#!/bin/sh

# Run all python tests in subdirectories
for file in $(find . -name "*.py")
do
    nosetests --rednose "$file"
done

