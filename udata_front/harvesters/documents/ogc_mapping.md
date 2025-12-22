# Mapa de Campos: OGC API - Collections para uData Database

Este documento mapeia os campos obtidos do harvester `OGCBackend` (OGC API - Collections em formato JSON-LD) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**OGC API - Collections**: Open Geospatial Consortium API
- Formato: JSON-LD (Schema.org)
- Protocolo: HTTP GET
- Estrutura: Baseada em Schema.org Dataset
- Exemplo: `https://ogcapi.dgterritorio.gov.pt/collections`

## Resumo do Mapeamento

| Campo Fonte (OGC JSON-LD) | Propriedade JSON | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `@id` | `each['@id']` | `remote_id` (HarvestItem) | Identificador único (URI). |
| `name` | `each['name']` | `title` | Nome do dataset. |
| `description` | `each['description']` | `description` | Descrição do dataset. |
| `keywords` | `each['keywords']` | `tags` | Keywords (lista ou string). |
| (Código) | - | `tags` | Adiciona tag fixa: `'ogcapi.dgterritorio.gov.pt'`. |
| `license` | `each['license']` | `license` | URL da licença (guess). |
| (Código) | - | `license` | Fallback: `'notspecified'` se não encontrar. |
| `temporalCoverage` | `each['temporalCoverage']` | `extras['temporal_coverage']` | Cobertura temporal (não parseada). |
| `provider` | `each['provider']` ou `data['provider']` | `extras['publisher_name']` | Nome do fornecedor. |
| `provider.contactPoint.email` | `provider['contactPoint']['email']` | `extras['publisher_email']` | Email de contacto. |
| (Código) | - | `extras['harvest:name']` | Nome da fonte de harvest. |
| **Distribution** | `each['distribution']` | **Resource** | |
| `contentURL` | `dist['contentURL']` | `url` | URL do recurso (normalizada). |
| `description` | `dist['description']` | `title` | Descrição como título. |
| `name` | `dist['name']` | `title` | Nome (fallback). |
| (Código) | - | `title` | Fallback final: `'Resource'`. |
| `encodingFormat` | `dist['encodingFormat']` | `format` | MIME type convertido para formato. |
| (Código) | - | `filetype` | Fixo: `'remote'`. |

## Detalhes Específicos

### 1. Estrutura JSON-LD
O harvester espera uma estrutura Schema.org com array `dataset`:
```json
{
  "@context": "https://schema.org/",
  "@type": "DataCatalog",
  "dataset": [
    {
      "@id": "https://...",
      "name": "...",
      ...
    }
  ]
}
```

### 2. Validação de Estrutura
Verifica se o campo `dataset` existe:
```python
metadata = data.get("dataset")
if not metadata:
    raise Exception('Could not find "dataset" in OGC response')
```

### 3. Normalização de Metadata
Garante que metadata é sempre uma lista:
```python
if isinstance(metadata, dict):
    metadata = [metadata]
```

### 4. Identificador (@id)
O `@id` é obrigatório. Datasets sem `@id` são ignorados:
```python
remote_id = each.get("@id")
if not remote_id:
    self.logger.warning(f"Skipping OGC dataset without @id")
    continue
```

### 5. Fallbacks de Título e Descrição
```python
title = each.get("name") or "Untitled Dataset"
description = each.get("description") or ""
```

### 6. Tags

#### 6.1 Tag Fixa
Todos os datasets recebem a tag de identificação:
```python
dataset.tags = ["ogcapi.dgterritorio.gov.pt"]
```

#### 6.2 Keywords
Suporta lista ou string única:
```python
keywords = item_data.get('keywords', [])
if isinstance(keywords, list):
    for keyword in keywords:
        if keyword and isinstance(keyword, str):
            dataset.tags.append(keyword)
elif isinstance(keywords, str) and keywords:
    dataset.tags.append(keywords)
```

### 7. Licença

#### 7.1 Tentativa de Guess
Tenta identificar a licença pela URL:
```python
license_url = item_data.get('license')
if license_url:
    dataset.license = License.guess(license_url)
```

#### 7.2 Fallback
Se não conseguir identificar, usa `'notspecified'`:
```python
if not dataset.license:
    dataset.license = License.guess('notspecified')
```

### 8. Recursos (Distributions)

#### 8.1 Validação de URL
Apenas cria recursos com URL válida:
```python
url = dist.get("contentURL", "")
if not url:
    continue
```

#### 8.2 Filtro de Formatos
**Ignora** recursos HTML e PNG:
```python
link_type = dist.get("encodingFormat", "")
if link_type in ('text/html', 'image/png'):
    continue
```

**Razão:** HTML são páginas de visualização, PNG são imagens de pré-visualização, não dados.

#### 8.3 Determinação do Formato
Usa mapeamento de MIME types para formatos:
```python
mime_to_format = {
    'application/json': 'JSON',
    'application/ld+json': 'JSON-LD',
    'application/xml': 'XML',
    'application/xls': 'XLS',
    'application/xlsx': 'XLSX',
    'application/csv': 'CSV',
    'text/csv': 'CSV',
    'text/xml': 'XML',
    'application/geo+json': 'GeoJSON',
    'application/gml+xml': 'GML',
}
```

**Fallback:** Se MIME type não estiver no mapeamento:
```python
# Extrai a parte após '/' e converte para maiúsculas
format = mime_type.split('/')[-1].upper()
```

**Fallback final:** Se não houver `encodingFormat`, extrai da URL:
```python
format_value = url.split('.')[-1] if '.' in url.split('/')[-1] else "unknown"
```

#### 8.4 Título do Recurso
Ordem de prioridade:
1. `description`
2. `name`
3. `"Resource"` (fallback)

```python
resource_title = dist.get("description") or dist.get("name") or "Resource"
```

#### 8.5 Recriação de Recursos
Os recursos são **recriados** a cada execução:
```python
dataset.resources = []
```

### 9. Provider/Publisher
Informação do fornecedor é armazenada em extras:
```python
provider = item_data.get('provider')
if provider and isinstance(provider, dict):
    dataset.extras['publisher_name'] = provider.get('name')
    dataset.extras['publisher_email'] = provider.get('contactPoint', {}).get('email')
```

**Nota:** O provider pode vir do dataset individual ou do catálogo raiz:
```python
"provider": each.get("provider") or data.get("provider")
```

### 10. Cobertura Temporal
Armazenada em extras sem parsing:
```python
temporal = item_data.get('temporal_coverage')
if temporal:
    dataset.extras['temporal_coverage'] = temporal
```

**Nota:** Não é parseada para o campo `temporal_coverage` do modelo Dataset.

## Estrutura JSON-LD Esperada

```json
{
  "@context": "https://schema.org/",
  "@type": "DataCatalog",
  "name": "OGC API Collections",
  "provider": {
    "@type": "Organization",
    "name": "DGT",
    "contactPoint": {
      "@type": "ContactPoint",
      "email": "info@dgterritorio.gov.pt"
    }
  },
  "dataset": [
    {
      "@type": "Dataset",
      "@id": "https://ogcapi.dgterritorio.gov.pt/collections/caop",
      "name": "Carta Administrativa Oficial de Portugal",
      "description": "Limites administrativos de Portugal",
      "keywords": ["administrativo", "limites", "portugal"],
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "temporalCoverage": "2023",
      "distribution": [
        {
          "@type": "DataDownload",
          "contentURL": "https://ogcapi.dgterritorio.gov.pt/collections/caop/items?f=json",
          "encodingFormat": "application/geo+json",
          "description": "GeoJSON export"
        },
        {
          "@type": "DataDownload",
          "contentURL": "https://ogcapi.dgterritorio.gov.pt/collections/caop/items?f=xml",
          "encodingFormat": "application/gml+xml",
          "description": "GML export"
        }
      ]
    }
  ]
}
```

## Exemplo de Mapeamento

### Resposta OGC API (simplificado)
```json
{
  "@context": "https://schema.org/",
  "dataset": [
    {
      "@id": "https://ogcapi.dgterritorio.gov.pt/collections/caop",
      "name": "Carta Administrativa Oficial de Portugal",
      "description": "Limites administrativos de Portugal",
      "keywords": ["administrativo", "limites", "portugal"],
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "temporalCoverage": "2023",
      "provider": {
        "name": "Direção-Geral do Território",
        "contactPoint": {
          "email": "info@dgterritorio.gov.pt"
        }
      },
      "distribution": [
        {
          "contentURL": "https://ogcapi.dgterritorio.gov.pt/collections/caop/items?f=json",
          "encodingFormat": "application/geo+json",
          "description": "GeoJSON export"
        },
        {
          "contentURL": "https://ogcapi.dgterritorio.gov.pt/collections/caop/items?f=html",
          "encodingFormat": "text/html",
          "description": "HTML viewer"
        }
      ]
    }
  ]
}
```

### Dataset uData resultante
```python
dataset.remote_id = "https://ogcapi.dgterritorio.gov.pt/collections/caop"
dataset.title = "Carta Administrativa Oficial de Portugal"
dataset.description = "Limites administrativos de Portugal"
dataset.tags = [
    "ogcapi.dgterritorio.gov.pt",
    "administrativo",
    "limites",
    "portugal"
]
dataset.license = License('cc-by')  # Identificada pela URL

dataset.extras = {
    'harvest:name': 'Nome da Fonte OGC',
    'temporal_coverage': '2023',
    'publisher_name': 'Direção-Geral do Território',
    'publisher_email': 'info@dgterritorio.gov.pt'
}

dataset.resources = [
    Resource(
        title="GeoJSON export",
        url="https://ogcapi.dgterritorio.gov.pt/collections/caop/items?f=json",
        filetype="remote",
        format="GeoJSON"
    )
    # HTML viewer é ignorado (filtrado)
]
```

## Campos Não Mapeados

Os seguintes campos **não são mapeados** para o modelo Dataset:
- `temporalCoverage` - Armazenado em extras, não parseado para `temporal_coverage`
- `spatialCoverage` - Não processado
- `provider` - Armazenado em extras, não mapeado para `organization`
- `@type` - Não usado
- `@context` - Não usado

## Particularidades

1. **Schema.org**: Usa vocabulário Schema.org em vez de DCAT
2. **Filtro de formatos**: Ignora HTML e PNG automaticamente
3. **Identificador URI**: Usa `@id` como identificador (pode ser URL completa)
4. **Licença por URL**: Tenta identificar licença pela URL fornecida
5. **Provider não cria organização**: Informação armazenada apenas em extras
6. **Temporal coverage não parseada**: Armazenada como string em extras
7. **Tag fixa específica**: `'ogcapi.dgterritorio.gov.pt'` (hardcoded)
8. **Mapeamento MIME extensível**: Fácil adicionar novos formatos ao dicionário

## Comparação com Outros Harvesters

| Aspecto | OGC API | DCAT | CKAN |
| :--- | :--- | :--- | :--- |
| **Formato** | JSON-LD (Schema.org) | RDF/XML/JSON-LD (DCAT) | JSON (CKAN API) |
| **Identificador** | `@id` (URI) | `dct:identifier` | `id` (UUID) |
| **Distribuições** | `distribution` | `dcat:distribution` | `resources` |
| **Licença** | URL | `dct:license` | `license_id` |
| **Provider** | `provider` | `dct:publisher` | `organization` |
| **Filtro de formatos** | Sim (HTML, PNG) | Não | Sim (resource_type) |
