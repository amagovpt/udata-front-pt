# Extrator de Estrutura MongoDB

Este script extrai **APENAS a estrutura** de uma base de dados MongoDB (nomes de coleções e campos), sem trazer dados.

Gera um ficheiro Excel com:
- Lista de todas as coleções
- Todos os campos de cada coleção com seus tipos
- Referências entre coleções (campos que terminam em _id ou Id)

**IMPORTANTE: Não extrai dados, apenas nomes de coleções e campos.**

## Requisitos

### Python 3 com os seguintes pacotes:
```bash
pip install pymongo openpyxl --break-system-packages
```

### MongoDB a correr num container Docker

## Configuração do Container Docker

### Opção 1: Container existente com porto mapeado
Se o seu container MongoDB já está a correr com o porto mapeado:
```bash
docker ps | grep mongo
```

### Opção 2: Executar o script dentro do container
```bash
# Copiar o script para dentro do container
docker cp mongodb_schema_extractor.py <container_name>:/tmp/

# Entrar no container
docker exec -it <container_name> bash

# Instalar dependências dentro do container
pip install pymongo openpyxl

# Executar o script
python /tmp/mongodb_schema_extractor.py
```

### Opção 3: Executar com acesso à rede Docker
```bash
# Descobrir a rede do container
docker inspect <container_name> | grep NetworkMode

# Executar o script na mesma rede
docker run --network=<network_name> -v $(pwd):/work -it python:3.11 bash
cd /work
pip install pymongo openpyxl
python mongodb_schema_extractor.py
```

## Configuração do Script

Edite as seguintes variáveis no início da função `main()`:

```python
DATABASE_NAME = 'udata'        # Nome da base de dados
CONTAINER_NAME = 'mongodb'     # Nome do container Docker
PORT = 27017                   # Porto do MongoDB
SAMPLE_SIZE = 100              # Número de documentos a analisar por coleção
OUTPUT_FILE = 'mongodb_schema.xlsx'  # Nome do ficheiro de saída
```

## Uso

```bash
python mongodb_schema_extractor.py
```

## Saída

O script gera um ficheiro Excel com 3 folhas:

### 1. Resumo
- Nome de cada coleção
- Número de documentos
- Número de campos

### 2. Campos
- Coleção
- Nome do campo (incluindo campos aninhados)
- Tipo(s) de dados
- Se é uma referência
- Para que coleção referencia

### 3. Referências
- Mapa de todas as referências entre coleções
- Coleção origem → Campo → Coleção destino

## Detecção de Referências

O script identifica automaticamente campos que possam ser referências:
- Campos terminados em `_id` (ex: user_id, product_id)
- Campos terminados em `Id` (ex: userId, productId)

## Exemplo de Estrutura Detectada

Para um documento como:
```json
{
  "_id": "123",
  "name": "João",
  "user_id": "456",
  "address": {
    "street": "Rua X",
    "city": "Lisboa"
  },
  "orders": [
    {"order_id": "789", "total": 100}
  ]
}
```

O script detecta:
- Campo: `name` (tipo: string)
- Campo: `user_id` (tipo: string, **referência para coleção "user"**)
- Campo: `address.street` (tipo: string)
- Campo: `address.city` (tipo: string)
- Campo: `orders.order_id` (tipo: string, **referência para coleção "order"**)
- Campo: `orders.total` (tipo: integer)

## Resolução de Problemas

### Erro de conexão
```
Erro ao conectar ao MongoDB: ...
```
**Solução**: Verifique se:
1. O container está a correr: `docker ps`
2. O porto está mapeado: `docker port <container_name>`
3. O nome do container está correto no script

### Permissões
```
Permission denied
```
**Solução**: Execute o script dentro do container ou ajuste as permissões de rede Docker

### Análise lenta
Se tiver muitos documentos, reduza o `SAMPLE_SIZE` para 50 ou 10.

## Notas

- O script analisa uma amostra de documentos de cada coleção (padrão: 100)
- Campos aninhados são representados com notação de ponto (ex: `address.city`)
- Arrays de objetos são analisados através do primeiro elemento
- A detecção de referências é baseada em convenções de nomenclatura
