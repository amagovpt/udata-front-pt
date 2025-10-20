#!/bin/bash
set -e

# ───────────────────────────────
# 🔧 Configurações básicas
# ───────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/build.log"
mkdir -p "$LOG_DIR"

# ───────────────────────────────
# 🔄 Funções auxiliares
# ───────────────────────────────
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
    echo "[INFO] $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[WARN] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    echo "[ERROR] $1" >> "$LOG_FILE"
}

progress_bar() {
    local pid=$1
    local delay=0.15
    local spin='|/-\'
    while ps -p $pid > /dev/null 2>&1; do
        for i in $(seq 0 3); do
            printf "\r${BLUE}Processando... ${spin:$i:1}${NC}"
            sleep $delay
        done
    done
    printf "\r${GREEN}✔ Concluído.${NC}\n"
}

check_file_exists() {
    local url=$1
    local status_code
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" "$url")
    [[ "$status_code" -eq 200 ]]
}

# ───────────────────────────────
# 🧹 Passo 0: Limpeza inicial
# ───────────────────────────────
log "Limpando diretórios antigos e arquivos ZIP..."
rm -f *.zip
rm -rf udata-* udata-metrics
log "Limpeza inicial concluída."

# ───────────────────────────────
# 📦 Passo 1: Entrada de versão
# ───────────────────────────────
read -rp "Enter the udata version (e.g., 2.5.1): " version
archive_name="udata-v$version.zip"
file_url="https://github.com/amagovpt/udata-front-pt/blob/udata-v$version/udata-update/$archive_name"
requirements_file="../requirements.pip"

log "Versão definida: $version"

# ───────────────────────────────
# 🧾 Passo 2: Atualizar requirements.pip
# ───────────────────────────────
if [ -f "$requirements_file" ]; then
    log "Atualizando o ficheiro $requirements_file..."
    sed -i "s|https://github.com/amagovpt/udata-front-pt/blob/udata-v.*/udata-update/udata-v.*.zip|$file_url|g" "$requirements_file"
else
    error "Ficheiro $requirements_file não encontrado."
    exit 1
fi

# ───────────────────────────────
# 🌐 Passo 3: Verificar se o ficheiro existe
# ───────────────────────────────
if check_file_exists "$file_url"; then
    log "Ficheiro $file_url já existe. Instalando diretamente..."
    pip install "$file_url?raw=true" &
    progress_bar $!
    log "Instalação concluída."
    exit 0
else
    log "Ficheiro não encontrado. Procedendo com build completo..."
fi

# ───────────────────────────────
# 🧩 Passo 4: Clonar repositórios
# ───────────────────────────────
source_repo_udata="https://github.com/opendatateam/udata.git"
clone_dir="udata-v$version"

log "Clonando repositórios..."
{
    git clone --branch "v$version" --single-branch "$source_repo_udata" "$clone_dir"
    cd "$clone_dir" && git switch -c "udata-v$version" >/dev/null 2>&1 && cd ..
    git clone https://github.com/opendatateam/udata-metrics.git "udata-metrics"
} & progress_bar $!

# ───────────────────────────────
# ⚙️ Passo 5: Alterações no código
# ───────────────────────────────
log "Aplicando personalizações no código..."

# form.vue
cp "./files/admin/form.vue" "$clone_dir/js/components/organization/form.vue"

# templates metrics
cp "./files/metrics/"*.html "udata-metrics/udata_metrics/templates/"

# account_deleted.html
cp "./files/templates/account_deleted.html" "$clone_dir/udata/templates/mail/account_deleted.html"

# tradução
cp "./files/translations/udata.po" "$clone_dir/udata/translations/pt/LC_MESSAGES/udata.po"

# MAIL_DEFAULT_SENDER
sed -i "s/webmaster@udata/noreply.dados.gov@ama.gov.pt/g" "$clone_dir/udata/settings.py"

# SVG Restrição
api_file="$clone_dir/udata/core/dataset/api.py"
insert_string="        # Adicionar verificação para ficheiros SVG\n        if infos['mime'] == 'image/svg+xml':\n            api.abort(415, 'Unsupported file type: SVG images are not allowed')"
sed -i "/infos = handle_upload(storages.resources, prefix)/a $insert_string" "$api_file"

# Traduções EU_HVD_CATEGORIES
rdf_file="$clone_dir/udata/rdf.py"
declare -A translations=(
    ["Météorologiques"]="Meteorológicas"
    ["Entreprises et propriété d'entreprises"]="Empresas e propriedade de empresas"
    ["Géospatiales"]="Geoespaciais"
    ["Mobilité"]="Mobilidade"
    ["Observation de la terre et environnement"]="Observação da Terra e do ambiente"
    ["Statistiques"]="Estatísticas"
)
for k in "${!translations[@]}"; do
    sed -i "s|\"$k\"|\"${translations[$k]}\"|g" "$rdf_file"
done

# Tradução de Emblemas (Badges)
badge_file="$clone_dir/udata/core/organization/models.py"
declare -A badges=(
    ["Public Service"]="Serviço Público"
    ["Certified"]="Certificado"
    ["Association"]="Associação"
    ["Company"]="Empresa"
    ["Local authority"]="Autoridade Local"
)
for k in "${!badges[@]}"; do
    sed -i "s|\"$k\"|\"${badges[$k]}\"|g" "$badge_file"
done

log "Personalizações aplicadas com sucesso."

# ───────────────────────────────
# 🧠 Passo 6: Ambiente virtual
# ───────────────────────────────
log "Ativando ambiente virtual..."
if [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    error "Ambiente virtual (venv) não encontrado. Crie-o antes de continuar."
    exit 1
fi

# ───────────────────────────────
# 🏗️ Passo 7: Build de assets
# ───────────────────────────────
log "Iniciando build de assets..."
cd "$clone_dir"
{
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install
    nvm use
    npm install
    inv assets-build
    inv widgets-build
    npm prune --production
} & progress_bar $!
cd ..

# ───────────────────────────────
# 📦 Passo 8: Compactação
# ───────────────────────────────
log "Compactando diretórios..."
{
    zip -r "$archive_name" "$clone_dir"
    zip -r custom-udata-metrics "udata-metrics"
} & progress_bar $!

# ───────────────────────────────
# 🧽 Passo 9: Limpeza
# ───────────────────────────────
log "Removendo diretórios temporários..."
rm -rf "$clone_dir" "udata-metrics"

# ───────────────────────────────
# 🚀 Passo 10: Push para o GitHub
# ───────────────────────────────
target_repo="https://github.com/amagovpt/udata-front-pt.git"
log "Alterando repositório remoto para $target_repo..."
git remote set-url origin "$target_repo"

git checkout -b "udata-v$version" >/dev/null 2>&1 || true
git add -A
git commit -m "Update to version $version of udata" || warn "Nenhuma modificação a commitar."
git push --set-upstream origin "udata-v$version"

# ───────────────────────────────
# 🏁 Finalização
# ───────────────────────────────
echo -e "\n${GREEN}✅ Processo concluído com sucesso!${NC}"
echo -e "${BLUE}Log completo disponível em:${NC} ${YELLOW}$LOG_FILE${NC}"
