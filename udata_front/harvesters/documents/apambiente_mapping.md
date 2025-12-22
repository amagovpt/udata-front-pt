# Mapa de Campos: Portal do Ambiente (CSW) para uData Database

Este documento mapeia os campos obtidos do harvester `PortalAmbienteBackend` (CSW - Catalogue Service for the Web) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**Endpoint CSW**: Portal do Ambiente (APA - Agência Portuguesa do Ambiente)
- URL exemplo: `https://sniambgeoportal.apambiente.pt/geoportal/csw`
- Protocolo: CSW (OGC Catalogue Service for the Web)
- Biblioteca: OWSLib (`owslib.csw.CatalogueServiceWeb`)

## Resumo do Mapeamento

| Campo Fonte (CSW Record) | Propriedade OWSLib | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `identifier` | `record.identifier` | `remote_id` (HarvestItem) | Identificador único do registo CSW. |
| `title` | `record.title` | `title` | Título do dataset. |
| `abstract` | `record.abstract` | `description` | Descrição do dataset. |
| - | - | `license` | Fixo: `cc-by` (Creative Commons Attribution). |
| - | - | `tags` | Fixo: `["apambiente.pt"]`. |
| - | `item.get('date')` | `created_at` | Data de criação (se disponível). |
| **Resource** | | | |
| `references[0]['url']` | `record.references[0].get('url')` | `url` | URL do recurso (normalizada). |
| `title` | `record.title` | `title` | Reutiliza o título do dataset. |
| `type` | `record.type` | `format` | Determina o formato do recurso. |
| - | - | `filetype` | Fixo: `remote`. |

## Detalhes Específicos

### 1. Identificador do Dataset
O `identifier` do registo CSW é usado como `remote_id` no `HarvestItem`, permitindo a identificação única do dataset durante a harvest.

### 2. Licença
O harvester atribui automaticamente a licença **CC-BY** (Creative Commons Attribution) a todos os datasets colhidos:
```python
dataset.license = License.guess('cc-by')
```

### 3. Tags
Todos os datasets recebem a tag `"apambiente.pt"` para identificação da fonte:
```python
dataset.tags = ["apambiente.pt"]
```

### 4. Recursos (Resources)

#### 4.1 URL do Recurso
A URL é extraída do primeiro elemento em `record.references` e normalizada:
```python
item["url"] = normalize_url_slashes(record.references[0].get('url'))
```

#### 4.2 Formato do Recurso
O formato é determinado pela propriedade `type` do registo CSW:
- Se `type == "liveData"` → formato = `"wms"` (Web Map Service)
- Caso contrário, extrai a extensão da URL:
  - Se a extensão tiver mais de 3 caracteres → formato = `"wms"`
  - Caso contrário, usa a extensão como formato (ex: `pdf`, `xml`, `zip`)

```python
if item.get('type') == "liveData":
    type = "wms"
else:
    type = url.split('.')[-1].lower()
    if len(type) > 3:
        type = "wms"
```

#### 4.3 Recriação de Recursos
O harvester **força a recriação** de todos os recursos a cada execução:
```python
dataset.resources = []
```
Isto significa que os recursos existentes são substituídos pelos novos dados colhidos.

### 5. Campos Não Mapeados

Os seguintes campos típicos de CSW **não são mapeados** neste harvester:
- `spatial` (cobertura espacial)
- `temporal` (cobertura temporal)
- `keywords` (palavras-chave do CSW)
- `contact` (informação de contacto)
- `modified` (data de modificação)

### 6. Paginação
O harvester processa os registos em lotes de 100:
```python
csw.getrecords2(maxrecords=100, startposition=startposition)
```

## Exemplo de Mapeamento

### Registo CSW (simplificado)
```python
record.identifier = "12345-abcd-6789"
record.title = "Áreas Protegidas de Portugal"
record.abstract = "Delimitação das áreas protegidas..."
record.type = "liveData"
record.references = [{'url': 'https://example.pt/wms?service=WMS'}]
```

### Dataset uData resultante
```python
dataset.title = "Áreas Protegidas de Portugal"
dataset.description = "Delimitação das áreas protegidas..."
dataset.license = License('cc-by')
dataset.tags = ["apambiente.pt"]
dataset.resources = [
    Resource(
        title="Áreas Protegidas de Portugal",
        url="https://example.pt/wms?service=WMS",
        filetype="remote",
        format="wms"
    )
]
```
