#!/bin/bash

# Configurações de cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

# Função para verificar a existência do arquivo no GitHub
check_file_exists() {
    url=$1
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" "$url")
    if [ "$status_code" -eq 200 ]; then
        return 0 # Arquivo existe
    else
        return 1 # Arquivo não existe
    fi
}

# Passo 1: Clonar o repositório
echo -e "${BLUE}Enter the udata version (e.g., 2.5.1):${NC}"
read version
source_repo="https://github.com/opendatateam/udata"
target_repo="https://github.com/gpsilv4/udata-front-pt.git"
clone_dir="udata-v$version"

echo -e "${GREEN}Cloning the udata repository version $version...${NC}"
git clone $source_repo "$clone_dir" || { echo -e "${RED}Error cloning the repository.${NC}"; exit 1; }

# Step 2: Copy the form.vue file
form_vue_path="./form.vue" # Update path if necessary
destination_path="$clone_dir/js/components/organization/form.vue"

if [ -f "$form_vue_path" ]; then
    echo -e "${GREEN}Replacing the form.vue file...${NC}"
    cp "$form_vue_path" "$destination_path" || { echo -e "${RED}Error replacing the form.vue file.${NC}"; exit 1; }
else
    echo -e "${RED}form.vue file not found in the current directory.${NC}"
    exit 1
fi

# Exit to the parent directory and activate the virtual environment
echo -e "${GREEN}Activating the virtual environment...${NC}"
cd ..
if [ -d "venv" ]; then
    source venv/bin/activate || { echo -e "${RED}Error activating the virtual environment.${NC}"; exit 1; }
else
    echo -e "${RED}Virtual environment (venv) not found. Please create it first.${NC}"
    exit 1
fi
cd - > /dev/null # Return to the script directory

# Step 3: Run necessary commands
echo -e "${GREEN}Running the necessary commands...${NC}"
cd "$clone_dir" || { echo -e "${RED}Error accessing the $clone_dir directory.${NC}"; exit 1; }

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

nvm install || { echo -e "${RED}Error installing Node.js.${NC}"; exit 1; }
nvm use || { echo -e "${RED}Error using the Node.js version.${NC}"; exit 1; }

npm install || { echo -e "${RED}Error installing dependencies.${NC}"; exit 1; }
inv assets-build || { echo -e "${RED}Error building assets.${NC}"; exit 1; }
inv widgets-build || { echo -e "${RED}Error building widgets.${NC}"; exit 1; }

npm prune --production || { echo -e "${RED}Error removing development dependencies.${NC}"; exit 1; }

Return to the parent directory
cd ..

# Step 4: Compress the udata directory
archive_name="$clone_dir.zip"
echo -e "${GREEN}Compressing the $clone_dir directory into $archive_name...${NC}"
zip -r "$archive_name" "$clone_dir" || { echo -e "${RED}Error compressing the directory.${NC}"; exit 1; }

# Remover o diretório compactado para liberar espaço
echo -e "${GREEN}Removing the directory $clone_dir...${NC}"
rm -rf "$clone_dir" || { echo -e "${RED}Error removing the directory $clone_dir.${NC}"; exit 1; }

# Add the .zip file to Git
echo -e "${GREEN}Adding the $archive_name to Git...${NC}"
git add "$archive_name" || { echo -e "${RED}Error adding the zip file to git.${NC}"; exit 1; }

# echo -e "${GREEN}Adding files to Git...${NC}"
# git add . || { echo -e "${RED}Error adding files.${NC}"; exit 1; }

# Step 5: Update the requirements.pip file
requirements_file="../requirements.pip"
if [ -f "$requirements_file" ]; then
    echo -e "${GREEN}Updating the version link in the $requirements_file file...${NC}"
    sed -i "s|https://github.com/gpsilv4/udata-front-pt/tree/$clone_dir/udata-update/udata-v.*.zip?raw=true|https://github.com/gpsilv4/udata-front-pt/tree/$clone_dir/udata-update/udata-v$version.zip?raw=true|g" "$requirements_file" || { echo -e "${RED}Error updating the requirements.pip file.${NC}"; exit 1; }
else
    echo -e "${RED}requirements.pip file not found in $requirements_file.${NC}"
    exit 1
fi

# Check if the file already exists on GitHub
file_url="https://github.com/gpsilv4/udata-front-pt/tree/$clone_dir/udata-update/udata-v$version.zip"
if check_file_exists "$file_url"; then
    echo -e "${YELLOW}File $file_url already exists on the remote repository. Skipping Git configuration step.${NC}"
else
    # Configure the remote repository and create a new branch
    echo -e "${GREEN}Changing remote repository to $target_repo...${NC}"
    git remote set-url origin "$target_repo" || { echo -e "${RED}Error configuring the remote repository.${NC}"; exit 1; }

    echo -e "${GREEN}Creating a new branch: $clone_dir...${NC}"
    git checkout -b "$clone_dir" || { echo -e "${RED}Error creating the branch.${NC}"; exit 1; }

    # Commit and Push the changes
    echo -e "${GREEN}Committing changes to Git...${NC}"
    git commit -m "Update to version $version of udata" || { echo -e "${YELLOW}No changes to commit.${NC}"; }
    git push --set-upstream origin "$clone_dir" || { echo -e "${RED}Error performing the push.${NC}"; exit 1; }

fi

# Install udata locally
echo -e "${GREEN}Installing udata locally...${NC}"
pip install "$requirements_file" || { echo -e "${RED}Error installing udata locally.${NC}"; exit 1; }

echo -e "${GREEN}Process completed successfully!${NC}"
