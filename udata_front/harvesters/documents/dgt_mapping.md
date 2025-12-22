# Mapa de Campos: DGT (SNIG) para uData Database

Este documento mapeia os campos obtidos do harvester `DGTBackend` (Sistema Nacional de Informação Geográfica - SNIG) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**API SNIG**: Direção-Geral do Território (DGT)
- URL exemplo: `https://snig.dgterritorio.gov.pt/rndg/srv/por/q?_content_type=json&fast=index&from=1&resultType=details&sortBy=referenceDateOrd&type=dataset+or+series&dataPolicy=Dados%20abertos&keyword=DGT`
- Protocolo: API JSON customizada (GeoNetwork)
- Formato de resposta: JSON com estrutura específica do GeoNetwork

## Resumo do Mapeamento

| Campo Fonte (SNIG JSON) | Propriedade JSON | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `geonet:info.uuid` | `each['geonet:info']['uuid']` | `remote_id` (HarvestItem) | UUID do registo no GeoNetwork. |
| `defaultTitle` | `each['defaultTitle']` | `title` | Título do dataset. |
| `defaultAbstract` | `each['defaultAbstract']` | `description` | Descrição/resumo do dataset. |
| - | - | `license` | Fixo: `cc-by` (Creative Commons Attribution). |
| - | - | `tags` | Fixo: `["snig.dgterritorio.gov.pt"]`. |
| `keyword` | `each['keyword']` | `tags` | Keywords adicionadas às tags. |
| `publicationDate` | `each['publicationDate']` | `created_at` | Data de publicação (comentado). |
| - | - | `extras['harvest:name']` | Nome da fonte de harvest. |
| **Resource** | `each['link']` | **Resource** | |
| `link` (pipe-separated) | Posição 2 | `url` | URL do recurso (normalizada). |
| `link` (pipe-separated) | Posição 3 | - | Tipo (não usado). |
| `link` (pipe-separated) | Posição 4 | `format` | Formato do recurso. |
| - | - | `title` | Reutiliza o título do dataset. |
| - | - | `filetype` | Fixo: `'remote'`. |

## Detalhes Específicos

### 1. Estrutura da Resposta JSON
A API retorna uma estrutura com metadados que pode ser:
- **Dict único**: Convertido para lista `[metadata]`
- **Lista de dicts**: Processada diretamente
- **String**: Erro (não processável)
- **Vazio**: Erro (sem datasets)

```python
metadata = data.get("metadata")
if isinstance(metadata, dict):
    metadata = [metadata]
elif isinstance(metadata, str):
    raise Exception("metadata é uma string, não um dict")
```

### 2. Identificador do Dataset
O UUID é extraído do objeto aninhado `geonet:info`:
```python
remote_id = each.get("geonet:info", {}).get("uuid")
```

### 3. Licença
Todos os datasets recebem automaticamente a licença **CC-BY**:
```python
dataset.license = License.guess('cc-by')
```

### 4. Tags
As tags incluem:
- Tag fixa de identificação: `"snig.dgterritorio.gov.pt"`
- Keywords do metadata: `each.get('keyword')`

```python
dataset.tags = ["snig.dgterritorio.gov.pt"]
for keyword in item.get('keywords'):
    dataset.tags.append(keyword)
```

### 5. Recursos (Resources)

#### 5.1 Formato Pipe-Separated
Os recursos vêm numa string separada por pipes (`|`):
```
nome|descrição|URL|tipo|formato
```

Exemplo:
```
WMS Service|Serviço WMS|https://example.pt/wms?service=WMS|OGC:WMS|WMS
```

#### 5.2 Parsing de Links
O harvester processa tanto listas quanto strings individuais:

**Lista de recursos:**
```python
if isinstance(resources, list):
    for url in resources:
        url_parts = url.split('|')
        inner_link = {
            'url': url_parts[2],
            'type': url_parts[3],
            'format': url_parts[4]
        }
        links.append(inner_link)
```

**Recurso único:**
```python
elif isinstance(resources, str):
    url_parts = resources.split('|')
    inner_link = {
        'url': url_parts[2],
        'type': url_parts[3],
        'format': url_parts[4]
    }
    links.append(inner_link)
```

#### 5.3 Determinação do Formato
O formato é determinado por duas estratégias:

**1. Extração do parâmetro `service` da query string:**
```python
parsed = urlparse.urlparse(resource['url'])
format = str(urlparse.parse_qs(parsed.query)['service'][0])
```

**2. Fallback para extensão do ficheiro:**
```python
except KeyError:
    format = resource['url'].split('.')[-1]
```

Isto permite identificar serviços OGC (WMS, WFS, etc.) através do parâmetro `service`.

#### 5.4 Recriação de Recursos
O harvester **força a recriação** de todos os recursos:
```python
dataset.resources = []
```

### 6. Data de Publicação (Desativada)
O código para processar a data de publicação está comentado:
```python
# if each.get("publicationDate"):
#     item["date"] = datetime.strptime(each.get("publicationDate"), "%Y-%m-%d")
```

### 7. Validação de Metadados
O harvester valida que os metadados não estão vazios:
```python
if not metadata:
    raise Exception('Erro: Metadados vazios. Nenhum dataset disponível.')
```

## Exemplo de Mapeamento

### Resposta SNIG API (simplificado)
```json
{
  "metadata": {
    "geonet:info": {
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    "defaultTitle": "Carta de Uso e Ocupação do Solo",
    "defaultAbstract": "Carta de uso e ocupação do solo de Portugal Continental",
    "keyword": ["uso do solo", "ocupação", "cartografia"],
    "link": [
      "WMS|Serviço WMS|https://snig.dgterritorio.gov.pt/wms?service=WMS|OGC:WMS|WMS",
      "Download|Ficheiro Shapefile|https://snig.dgterritorio.gov.pt/data/cos.zip|download|ZIP"
    ]
  }
}
```

### Dataset uData resultante
```python
dataset.title = "Carta de Uso e Ocupação do Solo"
dataset.description = "Carta de uso e ocupação do solo de Portugal Continental"
dataset.license = License('cc-by')
dataset.tags = [
    "snig.dgterritorio.gov.pt",
    "uso do solo",
    "ocupação",
    "cartografia"
]
dataset.extras = {
    'harvest:name': 'Nome da Fonte DGT'
}
dataset.resources = [
    Resource(
        title="Carta de Uso e Ocupação do Solo",
        url="https://snig.dgterritorio.gov.pt/wms?service=WMS",
        filetype="remote",
        format="WMS"  # Extraído do parâmetro service
    ),
    Resource(
        title="Carta de Uso e Ocupação do Solo",
        url="https://snig.dgterritorio.gov.pt/data/cos.zip",
        filetype="remote",
        format="zip"  # Extraído da extensão
    )
]
```

## Campos Não Mapeados

Os seguintes campos típicos **não são mapeados** neste harvester:
- `publicationDate` (comentado, não usado)
- `type` do link (extraído mas não usado)
- Cobertura espacial (`spatial`)
- Cobertura temporal (`temporal_coverage`)
- Organização (`organization`)
- Frequência de atualização (`frequency`)

## Particularidades do GeoNetwork

Este harvester é específico para a API do GeoNetwork usada pela DGT:
- Formato de links pipe-separated é específico desta implementação
- Estrutura `geonet:info` é própria do GeoNetwork
- Suporta serviços OGC (WMS, WFS, WCS) através da detecção do parâmetro `service`
