#!/bin/bash
##
# Script rápido para verificar se o uData está disponível
# Útil antes de executar os testes completos
##

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

UDATA_URL="${UDATA_URL:-http://preprod.dados.gov.pt}"

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Verificação Rápida - uData Front PT${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""

# 1. Verifica se Docker está a correr
echo -e "${YELLOW}🐳 Verificando Docker...${NC}"
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo -e "   ${GREEN}✅ Docker está ativo${NC}"
        
        # Lista containers udata
        udata_containers=$(docker ps --filter "name=udata" --format "{{.Names}}" 2>/dev/null || echo "")
        if [ -n "$udata_containers" ]; then
            echo -e "   ${GREEN}✅ Containers uData encontrados:${NC}"
            echo "$udata_containers" | while read -r container; do
                status=$(docker ps --filter "name=$container" --format "{{.Status}}" 2>/dev/null)
                echo -e "      → ${container} (${status})"
            done
        else
            echo -e "   ${YELLOW}⚠️  Nenhum container 'udata' em execução${NC}"
        fi
    else
        echo -e "   ${RED}❌ Docker não está acessível${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Docker não encontrado${NC}"
fi

# 2. Verifica porta 7000
echo ""
echo -e "${YELLOW}🔌 Verificando porta 7000...${NC}"
if command -v ss &> /dev/null; then
    if ss -tuln | grep -q ":7000"; then
        echo -e "   ${GREEN}✅ Porta 7000 está em uso (listen)${NC}"
    else
        echo -e "   ${RED}❌ Porta 7000 não está em uso${NC}"
        echo -e "   ${YELLOW}💡 O uData pode não estar a correr${NC}"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln | grep -q ":7000"; then
        echo -e "   ${GREEN}✅ Porta 7000 está em uso (listen)${NC}"
    else
        echo -e "   ${RED}❌ Porta 7000 não está em uso${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Comando ss/netstat não disponível${NC}"
fi

# 3. Teste HTTP
echo ""
echo -e "${YELLOW}🌐 Testando conexão HTTP em ${UDATA_URL}...${NC}"

# Tenta aceder ao endpoint
http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${UDATA_URL}" 2>/dev/null || echo "000")

if [ "$http_code" = "200" ]; then
    echo -e "   ${GREEN}✅ Serviço respondeu com HTTP 200 OK${NC}"
    response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 5 "${UDATA_URL}" 2>/dev/null)
    echo -e "   ${GREEN}⚡ Tempo de resposta: ${response_time}s${NC}"
elif [ "$http_code" = "302" ] || [ "$http_code" = "301" ]; then
    echo -e "   ${GREEN}✅ Serviço respondeu com HTTP ${http_code} (Redirecionamento)${NC}"
elif [ "$http_code" = "404" ]; then
    echo -e "   ${YELLOW}⚠️  HTTP 404 - Endpoint não encontrado${NC}"
    echo -e "   ${YELLOW}💡 Tentando /api/1/me/ ...${NC}"
    api_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "${UDATA_URL}/api/1/me/" 2>/dev/null || echo "000")
    if [ "$api_code" = "200" ] || [ "$api_code" = "401" ]; then
        echo -e "   ${GREEN}✅ API respondeu com HTTP ${api_code}${NC}"
    else
        echo -e "   ${RED}❌ API não respondeu corretamente${NC}"
    fi
elif [ "$http_code" = "502" ]; then
    echo -e "   ${RED}❌ HTTP 502 Bad Gateway${NC}"
    echo -e "   ${YELLOW}💡 Workers do uWSGI podem estar a reiniciar${NC}"
elif [ "$http_code" = "000" ]; then
    echo -e "   ${RED}❌ Sem resposta - Serviço não está disponível${NC}"
    echo -e "   ${YELLOW}💡 Verifique se o uData está a correr${NC}"
else
    echo -e "   ${YELLOW}⚠️  HTTP ${http_code} - Resposta inesperada${NC}"
fi

# 4. Resumo e recomendações
echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"

if [ "$http_code" = "200" ] || [ "$http_code" = "302" ] || [ "$http_code" = "301" ]; then
    echo -e "${GREEN}✅ PRONTO PARA TESTES!${NC}"
    echo ""
    echo -e "O serviço uData está disponível e respondendo."
    echo -e "Execute os testes de performance:"
    echo ""
    echo -e "  ${GREEN}./test_performance.sh 1${NC}   # Teste rápido"
    echo -e "  ${GREEN}./test_performance.sh 2${NC}   # Teste completo"
else
    echo -e "${RED}❌ NÃO PRONTO PARA TESTES${NC}"
    echo ""
    echo -e "${YELLOW}📋 Ações recomendadas:${NC}"
    echo ""
    echo -e "1. Iniciar o uData:"
    echo -e "   ${GREEN}docker-compose up -d${NC}"
    echo ""
    echo -e "2. Verificar logs:"
    echo -e "   ${GREEN}docker-compose logs -f udata${NC}"
    echo ""
    echo -e "3. Verificar status dos containers:"
    echo -e "   ${GREEN}docker ps -a | grep udata${NC}"
    echo ""
    echo -e "4. Restart se necessário:"
    echo -e "   ${GREEN}docker-compose restart udata${NC}"
fi

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""

# Exit code baseado no resultado
if [ "$http_code" = "200" ] || [ "$http_code" = "302" ] || [ "$http_code" = "301" ]; then
    exit 0
else
    exit 1
fi
