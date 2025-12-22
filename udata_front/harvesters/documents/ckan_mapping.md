# Mapa de Campos: CKAN para uData Database

Este documento mapeia os campos obtidos do harvester `CkanBackend` (CKAN API v3) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**API CKAN**: Comprehensive Knowledge Archive Network
- Endpoint: `{source_url}/api/3/action/`
- Protocolo: REST API JSON
- Versão: API v3 (suporta CKAN \u003e= 1.8)
- Ações principais:
  - `package_list` - Lista de nomes de datasets
  - `package_search` - Pesquisa com filtros
  - `package_show` - Detalhes de um dataset

## Resumo do Mapeamento

| Campo Fonte (CKAN API) | Propriedade JSON | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `id` | `data['id']` | `remote_id` (HarvestItem) | UUID do dataset (substitui `name`). |
| `name` | `data['name']` | `slug` | Nome técnico/slug do dataset. |
| `title` | `data['title']` | `title` | Título do dataset. |
| `notes` | `data['notes']` | `description` | Descrição (HTML parseado). |
| `license_id` | `data['license_id']` | `license` | Identificador da licença. |
| `license_title` | `data['license_title']` | `license` | Título da licença (fallback). |
| `tags[].name` | `data['tags']` | `tags` | Lista de tags. |
| `metadata_created` | `data['metadata_created']` | `harvest.created_at` | Data de criação. |
| `metadata_modified` | `data['metadata_modified']` | `harvest.modified_at` | Data de modificação. |
| `name` | `data['name']` | `harvest.ckan_name` | Nome CKAN original. |
| `url` | `data['url']` | `harvest.remote_url` | URL remota (se válida). |
| (Código) | - | `harvest.remote_url` | URL do dataset no CKAN (fallback). |
| (URL inválida) | `data['url']` | `harvest.ckan_source` | URL original se inválida. |
| **Extras** | `data['extras']` | | Campos adicionais CKAN. |
| `spatial` | `extra['value']` (GeoJSON) | `spatial.geom` | Cobertura espacial (GeoJSON). |
| `spatial-text` | `extra['value']` | `spatial.zones` ou `extras['ckan:spatial-text']` | Zona geográfica (texto). |
| `spatial-uri` | `extra['value']` | `extras['ckan:spatial-uri']` | URI da zona geográfica. |
| `frequency` | `extra['value']` | `frequency` | Frequência de atualização. |
| `temporal_start` | `extra['value']` | `temporal_coverage.start` | Início da cobertura temporal. |
| `temporal_end` | `extra['value']` | `temporal_coverage.end` | Fim da cobertura temporal. |
| Outros extras | `extra['key']` / `extra['value']` | `extras[key]` | Copiados para extras. |
| **Resource** | `data['resources']` | **Resource** | |
| `id` | `res['id']` | `id` | UUID do recurso (preservado). |
| `name` | `res['name']` | `title` | Título do recurso. |
| `description` | `res['description']` | `description` | Descrição (HTML parseado). |
| `url` | `res['url']` | `url` | URL do recurso. |
| `format` | `res['format']` | `format` | Formato do ficheiro. |
| `mimetype` | `res['mimetype']` | `mime` | MIME type. |
| `hash` | `res['hash']` | `hash` | Hash do ficheiro. |
| `created` | `res['created']` | `harvest.issued_at` | Data de criação. |
| `last_modified` | `res['last_modified']` | `harvest.modified_at` | Data de modificação. |
| (Código) | - | `filetype` | Fixo: `'remote'`. |
| `resource_type` | `res['resource_type']` | - | Filtro (apenas tipos permitidos). |

## Detalhes Específicos

### 1. Autenticação
Suporta API key para acesso a datasets privados:
```python
headers = {
    'content-type': 'application/json',
    'Authorization': self.config.get('apikey')
}
```

### 2. Filtros de Harvest
Suporta filtros configuráveis:
- **Organization**: Filtra por organização CKAN
- **Tag**: Filtra por tag

```python
filters = [
    {'key': 'organization', 'value': 'my-org'},
    {'key': 'tags', 'value': 'environment', 'type': 'exclude'}
]
```

**Query construída:**
```
organization:my-org AND -tags:environment
```

**Limite:** 1000 datasets por pesquisa (limite da API CKAN)

### 3. Identificador do Dataset
O harvester usa inicialmente o `name` mas depois atualiza para o `id`:
```python
# Fase 1: Usa name
self.process_dataset(name)

# Fase 2: Substitui por id
if result.get('id'):
    item.remote_id = result['id']
```

### 4. Compatibilidade DKAN
Suporta DKAN (fork do CKAN) que retorna lista em vez de objeto:
```python
result = response['result']
if type(result) is list:
    result = result[0]
```

### 5. Validação de Schema
Valida os dados contra schema Voluptuous:
```python
data = self.validate(result, self.schema)
```

**Campos validados:**
- Tipos de dados corretos
- Normalização de strings
- Conversão de datas
- Validação de emails
- Normalização de tags

### 6. Skip se Sem Recursos
Datasets sem recursos são ignorados:
```python
if not len(data.get('resources', [])):
    raise HarvestSkipException(f"Dataset {data['name']} has no record")
```

### 7. Licença
Usa heurística para identificar licença:
```python
default_license = dataset.license or License.default()
dataset.license = License.guess(
    data['license_id'],
    data['license_title'],
    default=default_license
)
```

### 8. Extras CKAN

#### 8.1 Spatial (GeoJSON)
Converte GeoJSON para MultiPolygon:
```python
spatial_geom = json.loads(extra['value'])

if spatial_geom['type'] == 'Polygon':
    coordinates = [spatial_geom['coordinates']]
elif spatial_geom['type'] == 'MultiPolygon':
    coordinates = spatial_geom['coordinates']
else:
    raise HarvestException('Unsupported spatial geometry')

dataset.spatial.geom = {
    'type': 'MultiPolygon',
    'coordinates': coordinates
}
```

#### 8.2 Spatial-Text
Tenta encontrar zona geográfica no uData:
```python
qs = GeoZone.objects(db.Q(name=value) | db.Q(slug=value))
if qs.count() == 1:
    spatial_zone = qs.first()
    dataset.spatial.zones = [spatial_zone]
else:
    dataset.extras['ckan:spatial-text'] = value
```

#### 8.3 Frequency
Tenta converter para UpdateFrequency:
```python
# Tenta RDF frequency
if freq := frequency_from_rdf(value):
    dataset.frequency = freq
else:
    # Tenta valor direto
    try:
        dataset.frequency = UpdateFrequency(value)
    except ValueError:
        dataset.extras['ckan:frequency'] = value
```

#### 8.4 Temporal Coverage
```python
temporal_start = daterange_start(extra['value'])
temporal_end = daterange_end(extra['value'])

if temporal_start and temporal_end:
    dataset.temporal_coverage = db.DateRange(
        start=temporal_start,
        end=temporal_end
    )
```

#### 8.5 Outros Extras
Extras não reconhecidos são copiados:
```python
dataset.extras[extra['key']] = value
```

**Nota:** Extras vazios são ignorados.

### 9. Remote URL
Ordem de prioridade:
1. Campo `url` do dataset (se válido)
2. URL do dataset no CKAN: `{source_url}/dataset/{name}`

```python
dataset.harvest.remote_url = self.dataset_url(data['name'])
if data.get('url'):
    try:
        url = uris.validate(data['url'])
        dataset.harvest.remote_url = url
    except uris.ValidationError:
        dataset.harvest.ckan_source = data['url']
```

### 10. Recursos (Resources)

#### 10.1 Tipos Permitidos
```python
ALLOWED_RESOURCE_TYPES = ('dkan', 'file', 'file.upload', 'api', 'metadata')

if res['resource_type'] not in ALLOWED_RESOURCE_TYPES:
    continue
```

#### 10.2 Preservação de UUID
Os recursos mantêm o UUID original do CKAN:
```python
try:
    resource = get_by(dataset.resources, 'id', UUID(res['id']))
except Exception:
    log.error('Unable to parse resource ID %s', res['id'])
    continue

if not resource:
    resource = Resource(id=res['id'])
    dataset.resources.append(resource)
```

#### 10.3 Metadados de Harvest
Cada recurso tem metadados de harvest:
```python
if not resource.harvest:
    resource.harvest = HarvestResourceMetadata()

resource.harvest.issued_at = res['created']
resource.harvest.modified_at = res['last_modified']
```

### 11. Tratamento de Erros CKAN
CKAN pode retornar 200 mesmo em erro:
```python
data = response.json()
if data.get('success', False):
    return data
else:
    error = data.get('error')
    if isinstance(error, dict):
        msg = error.get('message', 'Unknown error')
        if '__type' in error:
            msg = ': '.join((error['__type'], msg))
    else:
        msg = error
    raise HarvestException(msg)
```

## Schema de Validação

### Resource Schema
```python
resource = {
    'id': str,
    'position': int,
    'name': All(DefaultTo(''), str),
    'description': All(str, normalize_string),
    'format': All(str, Lower),
    'mimetype': Any(All(str, Lower), None),
    'size': Any(Coerce(int), None),
    'hash': Any(All(str, hash), None),
    'created': All(str, to_date),
    'last_modified': Any(All(str, to_date), None),
    'url': All(str),
    'resource_type': All(empty_none, DefaultTo('file'), str, Any(*RESOURCE_TYPES)),
}
```

### Tag Schema
```python
tag = {
    'id': str,
    Optional('vocabulary_id'): Any(str, None),
    Optional('display_name'): str,
    'name': All(str, normalize_tag),
    Optional('state'): str,
}
```

### Organization Schema
```python
organization = {
    'id': str,
    'description': str,
    'created': All(str, to_date),
    'title': str,
    'name': All(str, slug),
    'revision_timestamp': All(str, to_date),
    'is_organization': boolean,
    'state': str,
    'image_url': str,
    'revision_id': str,
    'type': 'organization',
    'approval_status': 'approved'
}
```

## Exemplo de Mapeamento

### Resposta CKAN API (simplificado)
```json
{
  "success": true,
  "result": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "dados-ambientais",
    "title": "Dados Ambientais de Portugal",
    "notes": "<p>Descrição dos dados ambientais</p>",
    "license_id": "cc-by",
    "license_title": "Creative Commons Attribution",
    "metadata_created": "2023-01-15T10:30:00",
    "metadata_modified": "2024-01-20T14:45:00",
    "url": "https://example.pt/dados-ambientais",
    "tags": [
      {"name": "ambiente"},
      {"name": "qualidade-ar"}
    ],
    "extras": [
      {"key": "spatial", "value": "{\"type\":\"Polygon\",\"coordinates\":[...]}"},
      {"key": "temporal_start", "value": "2020-01-01"},
      {"key": "temporal_end", "value": "2023-12-31"},
      {"key": "frequency", "value": "http://purl.org/cld/freq/monthly"}
    ],
    "resources": [
      {
        "id": "abc-123",
        "name": "Dados CSV",
        "url": "https://example.pt/data.csv",
        "format": "CSV",
        "mimetype": "text/csv",
        "resource_type": "file",
        "created": "2023-01-15T10:30:00",
        "last_modified": "2024-01-20T14:45:00"
      }
    ]
  }
}
```

### Dataset uData resultante
```python
dataset.remote_id = "123e4567-e89b-12d3-a456-426614174000"
dataset.slug = "dados-ambientais"
dataset.title = "Dados Ambientais de Portugal"
dataset.description = "Descrição dos dados ambientais"
dataset.license = License('cc-by')
dataset.tags = ["ambiente", "qualidade-ar"]
dataset.frequency = UpdateFrequency.MONTHLY

dataset.harvest = HarvestDatasetMetadata(
    created_at=datetime(2023, 1, 15, 10, 30, 0),
    modified_at=datetime(2024, 1, 20, 14, 45, 0),
    ckan_name='dados-ambientais',
    remote_url='https://example.pt/dados-ambientais'
)

dataset.spatial = SpatialCoverage(
    geom={'type': 'MultiPolygon', 'coordinates': [...]}
)

dataset.temporal_coverage = DateRange(
    start=date(2020, 1, 1),
    end=date(2023, 12, 31)
)

dataset.resources = [
    Resource(
        id="abc-123",
        title="Dados CSV",
        url="https://example.pt/data.csv",
        format="csv",
        mime="text/csv",
        filetype="remote",
        harvest=HarvestResourceMetadata(
            issued_at=datetime(2023, 1, 15, 10, 30, 0),
            modified_at=datetime(2024, 1, 20, 14, 45, 0)
        )
    )
]
```

