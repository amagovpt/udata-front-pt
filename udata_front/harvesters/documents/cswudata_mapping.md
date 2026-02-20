# Mapa de Campos: CSW para uData Database

Este documento mapeia os campos obtidos do harvester `CSWUdataBackend` (OGC CSW 2.0.2) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**OGC CSW (Catalogue Service for the Web)**: Norma para descoberta de recursos geoespaciais.

- Versão: 2.0.2
- Biblioteca: `OWSLib.csw`
- Ações principais:
  - `getrecords2` - Pesquisa e obtém registos de metadados (esn='full').

## Resumo do Mapeamento

| Campo Fonte (CSW / OWSLib) | Propriedade                         | Campo Destino (uData `Dataset`) | Notas / Lógica                                             |
| :------------------------- | :---------------------------------- | :------------------------------ | :--------------------------------------------------------- |
| **Dataset**                |                                     |                                 |                                                            |
| `identifier`               | `record.identifier`                 | `remote_id` (HarvestItem)       | Identificador único do registo no CSW.                     |
| `title`                    | `record.title`                      | `title`                         | Título do dataset.                                         |
| `abstract`                 | `record.abstract`                   | `description`                   | Descrição detalhada (abstract).                            |
| `subjects`                 | `record.subjects`                   | `tags`                          | Lista de palavras-chave.                                   |
| `created`                  | `record.created`                    | `created_at`                    | Data de criação (armazenada também em `extras`).           |
| `modified`                 | `record.modified`                   | `last_modified_internal`        | Data de modificação (armazenada também em `extras`).       |
| `identifier`               | `record.identifier`                 | `extras['dct_identifier']`      | Mantido como identificador Dublin Core.                    |
| **Recursos**               | `record.uris` / `record.references` | **Resource**                    |                                                            |
| `url`                      | `uri['url']`                        | `url`                           | URL do recurso ou serviço.                                 |
| `name`                     | `uri['name']`                       | `title`                         | Nome do recurso (fallback para título do dataset).         |
| `protocol`                 | `uri['protocol']`                   | `format`                        | Mapeia protocolos (WMS, WFS) ou MIME types para o formato. |
| (Código)                   | -                                   | `filetype`                      | Fixo: `'remote'`.                                          |
| **Spatial**                | `record.bbox`                       | `spatial.geom`                  | Bounding Box convertido para MultiPolygon.                 |

## Detalhes Específicos

### 1. Resolução de URL

O harvester tenta resolver a URL base para seguir redirecionamentos (comum em GeoNetwork):

```python
response = requests.get(base_url, timeout=30, allow_redirects=True, stream=True)
base_url = response.url
```

### 2. Forçar HTTPS

Se a URL de origem for HTTPS, o harvester força o uso de HTTPS para todas as operações, ignorando anúncios incorretos do servidor (GetCapabilities):

```python
if base_url.startswith("https://"):
    for op in getattr(csw, "operations", []):
        for method in op.methods:
            if method.get("url", "").startswith("http://"):
                method["url"] = method["url"].replace("http://", "https://", 1)
```

### 3. Processamento de Tags

- Adiciona sempre uma tag padrão configurada em `default_tag` (ou `'csw'` por omissão).
- Normaliza todas as palavras-chave do campo `subjects`.

### 4. Datas (Created / Modified)

Tenta converter strings ISO8601 para objetos `datetime`.

- `created` -> `dataset.created_at`
- `modified` -> `dataset.last_modified_internal`

Os valores originais são preservados em `extras['created_at']` e `extras['modified_at']`.

### 5. Cobertura Espacial (Spatial Coverage)

Converte o `bbox` do OWSLib para `MultiPolygon` (exigido pelo uData):

- Se for um **ponto** (minx=maxx e miny=maxy), cria um pequeno polígono de ~11m em redor para satisfazer o tipo `MultiPolygon`.
- Se for uma **área**, cria um polígono retangular seguindo a ordem horária/anti-horária correta.

### 6. Recursos (Resources)

O harvester percorre `record.uris` e, se vazio, tenta `record.references`.

#### 6.1 Detecção de Formato

- **WMS/WFS**: Identificados através do campo `protocol`.
- **MIME Types**: Extrai o subtipo de strings como `image/jpeg`.
- **Fallback**: Usa a extensão da URL ou o valor `'remote'`.

#### 6.2 Remote URL do Dataset

Tenta identificar uma "página de detalhes" web procurando por protocolos que contenham `html` ou `link`. Se encontrado, define `extras['remote_url']`.

## Exemplo de Mapeamento

### Registo CSW (Representação interna)

```python
# record extraído via OWSLib
record.identifier = "3196ec2b-581d-4f7f-856d-e4d5885f8e5b"
record.title = "Rede Natura 2000 - Zonas Especiais de Conservação"
record.abstract = "Cartografia dos limites das Zonas Especiais de Conservação..."
record.subjects = ["ambiente", "biodiversidade", "áreas protegidas"]
record.created = "2015-05-12T10:00:00"
record.modified = "2024-02-18T11:00:00"
record.bbox = <bbox minx=-9.5 miny=37.0 maxx=-6.2 maxy=42.1>
record.uris = [
    {
        "url": "https://geoservices.example.pt/wms",
        "protocol": "OGC:WMS",
        "name": "WMS Natura 2000"
    },
    {
        "url": "https://example.pt/manual.pdf",
        "protocol": "application/pdf",
        "name": "Manual de Apoio"
    }
]
```

### Dataset uData resultante

```python
dataset.remote_id = "3196ec2b-581d-4f7f-856d-e4d5885f8e5b"
dataset.title = "Rede Natura 2000 - Zonas Especiais de Conservação"
dataset.description = "Cartografia dos limites das Zonas Especiais de Conservação..."
dataset.tags = ["csw", "ambiente", "biodiversidade", "areas-protegidas"]
dataset.created_at = datetime(2015, 5, 12, 10, 0, 0)
dataset.last_modified_internal = datetime(2024, 2, 18, 11, 0, 0)

dataset.spatial.geom = {
    "type": "MultiPolygon",
    "coordinates": [[ [[-9.5, 37.0], [-6.2, 37.0], [-6.2, 42.1], [-9.5, 42.1], [-9.5, 37.0]] ]]
}

dataset.resources = [
    Resource(
        title="WMS Natura 2000",
        url="https://geoservices.example.pt/wms",
        format="wms",
        filetype="remote"
    ),
    Resource(
        title="Manual de Apoio",
        url="https://example.pt/manual.pdf",
        format="pdf",
        filetype="remote"
    )
]

dataset.extras = {
    "dct_identifier": "3196ec2b-581d-4f7f-856d-e4d5885f8e5b",
    "created_at": "2015-05-12T10:00:00",
    "modified_at": "2024-02-18T11:00:00"
}
```
