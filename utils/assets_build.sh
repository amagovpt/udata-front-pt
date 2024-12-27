#!/bin/bash

# Cores para as mensagens
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Sem cor

# Localiza a raiz do projeto (pasta udata-front-pt)
BASE_DIR=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)/../..")

# Caminho padrão para a pasta de imagens
IMG_DIR="${BASE_DIR}/udata_front/theme/gouvfr/static/img"

# Executa o comando inv assets-build
echo -e "${CYAN}Executando 'inv assets-build'...${NC}"
inv assets-build || { echo -e "${RED}Erro ao executar 'inv assets-build'${NC}"; exit 1; }

# Define os ficheiros específicos para ignorar alterações
files_to_ignore=(
    "favicon.png"
    "cc.png"
    "eidas.png"
    "logo-social.png"
)

echo -e "${CYAN}Ignorando alterações em ficheiros específicos...${NC}"
for file in "${files_to_ignore[@]}"; do
    full_path="${IMG_DIR}/${file}"
    git update-index --assume-unchanged "$full_path"
    echo -e "${GREEN}Ignorado:${NC} $full_path"
done

# Ignorar alterações em todos os ficheiros da pasta 'topics'
echo -e "${CYAN}Ignorando alterações nos ficheiros de imagem da pasta 'topics'...${NC}"
topics_files=$(git ls-files "${IMG_DIR}/topics/")
if [[ -n "$topics_files" ]]; then
    git update-index --assume-unchanged $topics_files
    echo -e "${GREEN}Ficheiros da pasta 'topics' ignorados com sucesso.${NC}"
else
    echo -e "${YELLOW}Nenhum ficheiro rastreado encontrado na pasta 'topics'.${NC}"
fi

echo -e "${CYAN}Script concluído.${NC}"
