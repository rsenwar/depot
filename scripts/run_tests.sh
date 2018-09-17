#!/usr/bin/env bash


echo "Linting code before commit..."
flake8 depot > .error.log

# Check if the error file is empty
if [ -s .error.log ]
then
  # not empty, contains errors
  echo "flake8 Errors in the .error.log file"
  cat .error.log
  echo "Commit failed."
  exit 1
else
  # no errors, remove the file
  rm .error.log
fi

echo "pydoc linting check."
pydocstyle depot > .error.log
if [ -s .error.log ]
then
  # contains errors
  echo "pydoc error in the .error.log"
  cat .error.log
  echo "Commit failed."
  exit 1
else
  # no errors, remove the file
  rm .error.log
fi

echo "pylint check."
cd depot; pylint depot > .pylint.log
cat .pylint.log | awk /.*Module.*/{p=1}p > .error.log
if [ -s .error.log ]
then
  # contains errors
  echo "pylint errors in .error.log"
  cat .error.log
  echo "Commit failed."
  exit 1
else
  # no errors, remove the file
  rm .error.log
  cat .pylint.log
  rm .pylint.log
fi


echo "running tests before commit..."
cd ..
py.test -mxv depot > .pytest.log
cat .pytest.log | awk /.*FAILURE.*/{p=1}p > .error.log

# Check if the error file is empty
if [ -s .error.log ]
then
  # not empty, contains errors
  echo "Errors in the .error.log file"
  echo "Commit failed."
  exit 1
else
  # no errors, remove the file
  rm .error.log
  cat .pytest.log
  rm .pytest.log
  exit 0
fi

