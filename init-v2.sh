echo "Initializing Git Repo."

if [ -d ".git" ]; then
  echo "This directory has already been initialized with git."
  exit 1
else
    git init .
    if (( $? )); then
      echo "Unable to initialize your directory"
      exit 1
    fi
    git add --all
    if (( $? )); then
      echo "Unable to stage files"
      exit 1
    fi
    git commit -m "Initial Commit"
    if (( $? )); then
      echo "Unable to create the initial commit"
      exit 1
    fi
    if [ -z "$1" ]
    then
        echo "No remote branch entered"
    else
        echo "Adding remote git repo"
        git remote add origin $1
        git push -u origin main
    fi
    touch README.md
    touch .gitignore
fi

echo "Creating Python venv"
if [ -d "venv" ]; then
    echo "Python Virtual Environment already created"
    exit 1
else
    python3 -m venv ./venv/
    echo "Virtual Environment created"
fi
echo "Git initalization complete"
