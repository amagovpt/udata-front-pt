#!/bin/bash

# Configurações de cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

# Função para verificar a existência do ficheiro no GitHub
check_file_exists() {
    url=$1
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" "$url")
    if [ "$status_code" -eq 200 ]; then
        return 0 # ficheiro existe
    else
        return 1 # ficheiro não existe
    fi
}

# Passo 0: Remover todos os ficheiros ZIP da pasta atual
rm -f *.zip

# Passo 1: Obter a versão e construir a URL
echo -e "${BLUE}Enter the udata version (e.g., 2.5.1):${NC}"
read version
archive_name="udata-v$version.zip"
echo -e "${GREEN}Version: v$version, Archive Name: $archive_name${NC}"
file_url="https://github.com/amagovpt/udata-front-pt/blob/udata-v$version/udata-update/$archive_name"

# Atualizar o ficheiro requirements.pip
requirements_file="../requirements.pip"
if [ -f "$requirements_file" ]; then
    echo -e "${GREEN}Updating the version link in the $requirements_file file...${NC}"
    sed -i "s|https://github.com/amagovpt/udata-front-pt/blob/udata-v.*/udata-update/udata-v.*.zip|$file_url|g" "$requirements_file" || {
        echo -e "${RED}Error updating the requirements.pip file.${NC}"
        exit 1
    }
    echo -e "${GREEN}File updated successfully.${NC}"
else
    echo -e "${RED}requirements.pip file not found in $requirements_file.${NC}"
    exit 1
fi


# Passo 2: Verificar se o ficheiro já existe no repositório
if check_file_exists "$file_url"; then
    echo -e "${GREEN}File $file_url already exists. Skipping all Git and setup steps...${NC}"

    # Instalar o ficheiro diretamente
    echo -e "${GREEN}Installing udata locally from $file_url...${NC}"
    pip install "$file_url?raw=true" || {
        
        echo -e "${RED}Error installing udata locally.${NC}"
        exit 1
    }
    echo -e "${GREEN}Process completed successfully!${NC}"
    exit 0
else
    echo -e "${GREEN}File $file_url does not exist. Proceeding with full setup...${NC}"
fi


# Passo 3: Clonar o repositório udata e prosseguir se o ficheiro não existir
source_repo="https://github.com/opendatateam/udata.git --branch v$version"
clone_dir="udata-v$version"

echo -e "${GREEN}Cloning the udata repository version $version...${NC}"
git clone $source_repo "$clone_dir" || { echo -e "${RED}Error cloning the repository.${NC}"; exit 1; }

# Passo 3.1: Clonar o repositório udata-metrics e prosseguir se o ficheiro não existir
source_repo="https://github.com/opendatateam/udata-metrics.git"
clone_dir_metrics="udata-metrics"

echo -e "${GREEN}Cloning the udata-metrics repository version $version...${NC}"
git clone $source_repo "$clone_dir_metrics" || { echo -e "${RED}Error cloning the repository.${NC}"; exit 1; }

# Passo 4: Alterações ficheiros udata backend
# 4.1: Substituir o ficheiro form.vue
form_vue_path="./files/admin/form.vue"
destination_path="$clone_dir/js/components/organization/form.vue"

if [ -f "$form_vue_path" ]; then
    echo -e "${GREEN}Replacing the form.vue file...${NC}"
    cp "$form_vue_path" "$destination_path" || { echo -e "${RED}Error replacing the form.vue file.${NC}"; exit 1; }
else
    echo -e "${RED}form.vue file not found in the current directory.${NC}"
    exit 1
fi

# 4.2: Substituir o ficheiro metrics HTML
copy_dataset_path="./files/metrics/dataset-metrics.html"
copy_organization_path="./files/metrics/organization-metrics.html"
copy_reuse_path="./files/metrics/reuse-metrics.html"
copy_site_path="./files/metrics/site-metrics.html"

destination_dataset_path="$clone_dir_metrics/udata_metrics/templates/dataset-metrics.html"
destination_organization_path="$clone_dir_metrics/udata_metrics/templates/organization-metrics.html"
destination_reuse_path="$clone_dir_metrics/udata_metrics/templates/reuse-metrics.html"
destination_site_path="$clone_dir_metrics/udata_metrics/templates/site-metrics.html"

# Dataset metrics
if [ -f "$copy_dataset_path" ]; then
    echo -e "${GREEN}Replacing the dataset-metrics.html file...${NC}"
    cp "$copy_dataset_path" "$destination_dataset_path" || { echo -e "${RED}Error replacing the dataset-metrics.html file.${NC}"; exit 1; }
else
    echo -e "${RED}dataset-metrics.html file not found in the expected directory.${NC}"
    exit 1
fi

# Organization metrics
if [ -f "$copy_organization_path" ]; then
    echo -e "${GREEN}Replacing the organization-metrics.html file...${NC}"
    cp "$copy_organization_path" "$destination_organization_path" || { echo -e "${RED}Error replacing the organization-metrics.html file.${NC}"; exit 1; }
else
    echo -e "${RED}organization-metrics.html file not found in the expected directory.${NC}"
    exit 1
fi

# Reuse metrics
if [ -f "$copy_reuse_path" ]; then
    echo -e "${GREEN}Replacing the reuse-metrics.html file...${NC}"
    cp "$copy_reuse_path" "$destination_reuse_path" || { echo -e "${RED}Error replacing the reuse-metrics.html file.${NC}"; exit 1; }
else
    echo -e "${RED}reuse-metrics.html file not found in the expected directory.${NC}"
    exit 1
fi

# Site metrics
if [ -f "$copy_site_path" ]; then
    echo -e "${GREEN}Replacing the site-metrics.html file...${NC}"
    cp "$copy_site_path" "$destination_site_path" || { echo -e "${RED}Error replacing the site-metrics.html file.${NC}"; exit 1; }
else
    echo -e "${RED}site-metrics.html file not found in the expected directory.${NC}"
    exit 1
fi

# 4.3: Alterar variável MAIL_DEFAULT_SENDER
settings_file="$clone_dir/udata/settings.py"
search_string="webmaster@udata"
replace_string="noreply.dados.gov@ama.gov.pt"

if [ -f "$settings_file" ]; then
    sed -i "s/$search_string/$replace_string/g" "$settings_file"
    echo "Substituição de e-mail concluída com sucesso."
else
    echo "O ficheiro $settings_file não foi encontrado."
fi

# 4.4: Adicionar verificação para ficheiros SVG
api_file="$clone_dir/udata/core/dataset/api.py"
search_string="infos = handle_upload(storages.resources, prefix)"
insert_string="        # Adicionar verificação para ficheiros SVG\n        if infos['mime'] == 'image/svg+xml':\n            api.abort(415, 'Unsupported file type: SVG images are not allowed')"

if [ -f "$api_file" ]; then
    sed -i "/$search_string/a $insert_string" "$api_file"
    echo "Código SVG inserido com sucesso."
else
    echo "O arquivo $api_file não foi encontrado."
fi

# Passo 4.5: Substituir keywords (EU_HVD_CATEGORIES) francesas por portuguesas
#Definir o caminho do arquivo
rdf_file="$clone_dir/udata/rdf.py"

#Verificar se o arquivo existe antes de aplicar as substituições
if [ -f "$rdf_file" ]; then
    echo "Substituindo termos franceses por português no arquivo $rdf_file..."

    #Substituições usando sed
    sed -i "s|\"Météorologiques\"|\"Meteorológicas\"|g" "$rdf_file"
    sed -i "s|\"Entreprises et propriété d'entreprises\"|\"Empresas e propriedade de empresas\"|g" "$rdf_file"
    sed -i "s|\"Géospatiales\"|\"Geoespaciais\"|g" "$rdf_file"
    sed -i "s|\"Mobilité\"|\"Mobilidade\"|g" "$rdf_file"
    sed -i "s|\"Observation de la terre et environnement\"|\"Observação da Terra e do ambiente\"|g" "$rdf_file"
    sed -i "s|\"Statistiques\"|\"Estatísticas\"|g" "$rdf_file"

    echo "Substituição EU_HVD_CATEGORIES concluída com sucesso."
else
    echo "O arquivo $rdf_file não foi encontrado."
fi

# Passo 5: Configurar o ambiente virtual
echo -e "${GREEN}Activating the virtual environment...${NC}"
cd ..
if [ -d "venv" ]; then
    source venv/bin/activate || { echo -e "${RED}Error activating the virtual environment.${NC}"; exit 1; }
else
    echo -e "${RED}Virtual environment (venv) not found. Please create it first.${NC}"
    exit 1
fi
cd - > /dev/null

# Passo 6: Executar os comandos necessários para construir o pacote
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

cd ..

# Passo 7: Compactar o diretório
# Passo 7.1: zip udata
echo -e "${GREEN}Compressing the $clone_dir directory into $archive_name...${NC}"
zip -r "$archive_name" "$clone_dir" || { echo -e "${RED}Error compressing the directory.${NC}"; exit 1; }

# Passo 7.2: zip udata-metrics
echo -e "${GREEN}Compressing the $clone_dir_metrics directory into custom-udata-metrics...${NC}"
zip -r custom-udata-metrics "$clone_dir_metrics" || { echo -e "${RED}Error compressing the directory.${NC}"; exit 1; }

# Passo 8: Remover o diretório compactado
# Passo 8.1: Remove udata
echo -e "${GREEN}Removing the directory $clone_dir...${NC}"
rm -rf "$clone_dir" || { echo -e "${RED}Error removing the directory $clone_dir.${NC}"; exit 1; }

# Passo 8.2: Remove udata-metrics
echo -e "${GREEN}Removing the directory $clone_dir_metrics...${NC}"
rm -rf "$clone_dir_metrics" || { echo -e "${RED}Error removing the directory $clone_dir_metrics.${NC}"; exit 1; }

# Passo 9: Adicionar o ficheiro ao Git e atualizar
target_repo="https://github.com/amagovpt/udata-front-pt.git"
echo -e "${GREEN}Changing remote repository to $target_repo...${NC}"
git remote set-url origin "$target_repo" || { echo -e "${RED}Error configuring the remote repository.${NC}"; exit 1; }

echo -e "${GREEN}Creating a new branch: $clone_dir...${NC}"
git checkout -b "$clone_dir" || { echo -e "${RED}Error creating the branch.${NC}"; exit 1; }

git commit -m "Update to version $version of udata" || { echo -e "${YELLOW}No changes to commit.${NC}"; }
git add -A || { echo -e "${RED}Error adding the zip file to git.${NC}"; exit 1; }
git push --set-upstream origin "$clone_dir" || { echo -e "${RED}Error performing the push.${NC}"; exit 1; }

echo -e "${BLUE}Do you want to create a new release? (yes/no)${NC}"
read create_release

if [[ "$create_release" == "yes" || "$create_release" == "y" ]]; then
    echo -e "${BLUE}Enter the release version (e.g., 2.5.1):${NC}"
    read release_version

    echo -e "${GREEN}Creating a new branch: $release_version...${NC}"
    git checkout -b release-"$release_version" || { echo -e "${RED}Error creating the branch.${NC}"; exit 1; }

    rm -f *.zip

    # Instalar o ficheiro compactado
    echo -e "${GREEN}Installing udata locally...${NC}"
    cd .. || { echo -e "${RED}Erro ao mudar de diretorio.${NC}"; exit 1; }
    pip install -r requirements.pip || { echo -e "${RED}Error installing udata locally.${NC}"; exit 1; }
    pip install -e . -r requirements/test.pip -r requirements/develop.pip || { echo -e "${RED}Error installing udata locally.${NC}"; exit 1; }

    # Atualizar javascript (comando a definir se necessário)

    git push --set-upstream origin release-"$release_version" || { echo -e "${RED}Error performing the push.${NC}"; exit 1; }

else
    echo -e "${GREEN}Skipping release creation. Cleaning up...${NC}"
fi

git checkout main || { echo -e "${RED}Error creating the branch.${NC}"; exit 1; }

rm -f *.zip


echo -e "${GREEN}Process completed successfully!${NC}"
