# Mapa de Campos: CKAN PT para uData Database

Este documento mapeia os campos obtidos do harvester `CkanPTBackend` (CKAN API v3) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**API CKAN**: Plataforma CKAN (Comprehensive Knowledge Archive Network)
- Protocolo: CKAN API v3 (REST JSON)
- Endpoints principais:
  - `package_list` - Lista de datasets
  - `package_show` - Detalhes de um dataset
  - `package_search` - Pesquisa com filtros
- Biblioteca: Requests HTTP (implementação customizada)

## Resumo do Mapeamento

| Campo Fonte (CKAN API) | Propriedade JSON | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `id` | `data['id']` | `remote_id` (HarvestItem) | UUID do dataset no CKAN. |
| `name` | `data['name']` | `slug` | Nome técnico/slug do dataset. |
| `title` | `data['title']` | `title` | Título do dataset. |
| `notes` | `data['notes']` | `description` | Descrição (HTML parseado). |
| `license_id` | `data['license_id']` | `license` | Identificador da licença. |
| `license_title` | `data['license_title']` | `license` | Título da licença (fallback). |
| `tags[].name` | `data['tags']` | `tags` | Lista de tags. |
| - | - | `tags` | Adiciona hostname da fonte. |
| `metadata_created` | `data['metadata_created']` | `created_at_internal` | Data de criação. |
| `metadata_modified` | `data['metadata_modified']` | `last_modified_internal` | Data de modificação. |
| `organization.name` | `data['organization']['name']` | `organization.acronym` | Acrónimo da organização. |
| `organization.title` | `data['organization']['title']` | `organization.name` | Nome da organização. |
| `organization.description` | `data['organization']['description']` | `organization.description` | Descrição da organização. |
| `url` | `data['url']` | `extras['remote_url']` | URL remota do dataset. |
| - | - | `extras['ckan:name']` | Nome CKAN original. |
| - | - | `extras['harvest:name']` | Nome da fonte de harvest. |
| - | - | `frequency` | Fixo: `'unknown'`. |
| **Extras** | `data['extras']` | | Campos adicionais CKAN. |
| `spatial` | `extra['value']` (GeoJSON) | `spatial.geom` | Cobertura espacial (desativado). |
| `temporal_start` | `extra['value']` | `temporal_coverage.start` | Início da cobertura temporal. |
| `temporal_end` | `extra['value']` | `temporal_coverage.end` | Fim da cobertura temporal. |
| `frequency` | `extra['value']` | - | Não mapeado (apenas log). |
| Outros extras | `extra['key']` / `extra['value']` | `extras[key]` | Copiados para extras. |
| **Resource** | `data['resources']` | **Resource** | |
| `id` | `res['id']` | `id` | UUID do recurso. |
| `name` | `res['name']` | `title` | Título do recurso. |
| `description` | `res['description']` | `description` | Descrição (HTML parseado). |
| `url` | `res['url']` | `url` | URL do recurso (normalizada). |
| `format` | `res['format']` | `format` | Formato do ficheiro. |
| `mimetype` | `res['mimetype']` | `mime` | MIME type. |
| `hash` | `res['hash']` | `hash` | Hash do ficheiro. |
| `created` | `res['created']` | `created` | Data de criação. |
| `last_modified` | `res['last_modified']` | `modified` | Data de modificação. |
| - | - | `filetype` | Fixo: `'remote'`. |
| `resource_type` | `res['resource_type']` | - | Filtro (apenas tipos permitidos). |

## Detalhes Específicos

### 1. Identificador do Dataset
O harvester usa inicialmente o `name` (slug) para identificar o dataset, mas depois atualiza para o `id` (UUID):
```python
item.remote_id = data['id']
```

### 2. Organização
O harvester **cria automaticamente** organizações se não existirem:
```python
organization_acronym = data['organization']['name']
orgObj = Organization.objects(acronym=organization_acronym).first()
if orgObj:
    dataset.organization = orgObj
else:
    orgObj = Organization()
    orgObj.acronym = organization_acronym
    orgObj.name = data['organization']['title']
    orgObj.description = data['organization']['description']
    orgObj.save()
    dataset.organization = orgObj
```

### 3. Licença
A licença é determinada por heurística, com fallback configurável:
```python
default_license = self.harvest_config.get('license', License.default())
dataset.license = License.guess(
    data['license_id'],
    data['license_title'],
    default=default_license
)
```

### 4. Tags
As tags incluem:
- Tags originais do CKAN: `data['tags']`
- Hostname da fonte: `urlparse(self.source.url).hostname`

```python
dataset.tags = [t['name'] for t in data['tags'] if t['name']]
dataset.tags.append(urlparse(self.source.url).hostname)
```

### 5. Cobertura Espacial
A cobertura espacial pode ser definida de duas formas:

#### 5.1 Por Configuração (Geozones)
Se configurado no `harvest_config`, usa zonas geográficas predefinidas:
```python
if self.harvest_config.get('geozones', False):
    dataset.spatial = SpatialCoverage()
    dataset.spatial.zones = []
    for zone in self.harvest_config.get('geozones'):
        geo_zone = GeoZone.objects.get(id=zone)
        dataset.spatial.zones.append(geo_zone)
```

#### 5.2 Por GeoJSON (Desativado)
O código para processar GeoJSON do extra `spatial` está comentado.

### 6. Cobertura Temporal
Extraída dos extras `temporal_start` e `temporal_end`:
```python
if temporal_start and temporal_end:
    dataset.temporal_coverage = db.DateRange(
        start=temporal_start,
        end=temporal_end,
    )
```

### 7. Recursos (Resources)

#### 7.1 Filtro de Tipos
Apenas recursos com tipos permitidos são processados:
```python
ALLOWED_RESOURCE_TYPES = ('dkan', 'file', 'file.upload', 'api', 'metadata')

if res['resource_type'] not in ALLOWED_RESOURCE_TYPES:
    continue
```

#### 7.2 Validação de URL
URLs inválidas são ignoradas:
```python
try:
    url = uris.validate(res['url'])
except uris.ValidationError:
    continue
```

#### 7.3 Preservação de ID
Os recursos mantêm o UUID original do CKAN:
```python
resource = Resource(id=res['id'])
```

#### 7.4 Limpeza de Recursos Removidos
Recursos que já não existem na fonte são removidos:
```python
for resource_id in current_resources:
    if resource_id not in fetched_resources:
        dataset.resources.remove(resource)
```

### 8. Extras CKAN
Todos os extras do CKAN são copiados para `dataset.extras`, exceto:
- `spatial` (processado separadamente)
- `spatial-text` (ignorado)
- `spatial-uri` (ignorado)
- `temporal_start` (processado separadamente)
- `temporal_end` (processado separadamente)
- `frequency` (apenas logged, não mapeado)

### 9. Filtros de Harvest
O harvester suporta filtros configuráveis:
- **Organization**: Filtra por organização CKAN
- **Tag**: Filtra por tag

Exemplo de query com filtros:
```python
q = "organization:my-org AND tags:environment"
```

### 10. Validação de Schema
O harvester valida os dados recebidos contra um schema Voluptuous:
```python
data = self.validate(response['result'], self.schema)
```

## Exemplo de Mapeamento

### Resposta CKAN API (simplificado)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "dados-ambientais",
  "title": "Dados Ambientais de Portugal",
  "notes": "<p>Descrição dos dados ambientais</p>",
  "license_id": "cc-by",
  "license_title": "Creative Commons Attribution",
  "metadata_created": "2023-01-15T10:30:00",
  "metadata_modified": "2024-01-20T14:45:00",
  "organization": {
    "name": "apa",
    "title": "Agência Portuguesa do Ambiente",
    "description": "Entidade responsável..."
  },
  "tags": [
    {"name": "ambiente"},
    {"name": "qualidade-ar"}
  ],
  "extras": [
    {"key": "temporal_start", "value": "2020-01-01"},
    {"key": "temporal_end", "value": "2023-12-31"}
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
```

### Dataset uData resultante
```python
dataset.slug = "dados-ambientais"
dataset.title = "Dados Ambientais de Portugal"
dataset.description = "Descrição dos dados ambientais"
dataset.license = License('cc-by')
dataset.tags = ["ambiente", "qualidade-ar", "example.pt"]
dataset.created_at_internal = datetime(2023, 1, 15, 10, 30, 0)
dataset.last_modified_internal = datetime(2024, 1, 20, 14, 45, 0)
dataset.organization = Organization(acronym="apa", name="Agência Portuguesa do Ambiente")
dataset.temporal_coverage = DateRange(start=date(2020, 1, 1), end=date(2023, 12, 31))
dataset.extras = {
    'ckan:name': 'dados-ambientais',
    'harvest:name': 'Nome da Fonte',
    'remote_url': 'https://ckan.example.pt/dataset/dados-ambientais'
}
dataset.resources = [
    Resource(
        id="abc-123",
        title="Dados CSV",
        url="https://example.pt/data.csv",
        format="CSV",
        mime="text/csv",
        filetype="remote",
        created=datetime(2023, 1, 15, 10, 30, 0),
        modified=datetime(2024, 1, 20, 14, 45, 0)
    )
]
```
