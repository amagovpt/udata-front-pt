# Mapa de Campos: DCAT para uData Database

Este documento mapeia os campos obtidos do harvester `DcatBackend` (e seus derivados como `evian.json`) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**DCAT / RDF**: Data Catalog Vocabulary
- Formatos suportados: RDF/XML, Turtle, JSON-LD, etc.
- O harvester processa o grafo RDF e extrai as entidades `dcat:Dataset`, `dcat:Distribution` (Resource) e `dcat:DataService`.

## Resumo do Mapeamento

| Campo Fonte (DCAT/RDF) | Propriedade JSON (Ex: `evian.json`) | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | `dataset` | | Entidade `dcat:Dataset` |
| `dct:identifier` | `identifier` | `harvest.dct_identifier` | Identificador único no catálogo de origem. Também usado para `harvest.uri`. |
| `dct:title` | `title` | `title` | Título do dataset. |
| `dct:description` | `description` | `description` | Descrição (HTML sanitizado). Fallback para `dct:abstract`. |
| `dcat:keyword` | `keyword` | `tags` | Lista de palavras-chave. |
| `dct:issued` | `issued` | `harvest.issued_at` | Data de publicação original. |
| `dct:created` | `created` | `harvest.created_at` | Data de criação original. |
| `dct:modified` | `modified` | `harvest.modified_at` | Data de modificação. Datas futuras são ignoradas. |
| `dct:spatial` | `spatial` | `spatial.geom` | Cobertura espacial. Suporta GeoJSON, WKT ou String BBox ("w,s,e,n"). |
| `dct:temporal` | `temporal` | `temporal_coverage` | Cobertura temporal (`dct:PeriodOfTime`). |
| `dct:accrualPeriodicity` | `accrualPeriodicity` | `frequency` | Frequência de atualização (mapeada de URIs `freq:` ou `eufreq:`). |
| `dct:publisher` | `publisher` | `contact_points` | Organização publicadora (mapeada para role `publisher`). |
| `vcard:Contact` | `contactPoint` | `contact_points` | Pontos de contacto (mapeados para role `contact`). |
| `dcat:landingPage` | `landingPage` | `harvest.remote_url` | URL da página do dataset na fonte. |
| `dct:license` | `license` | `license` | Licença. Tenta `License.guess` usando `dct:license` e `dct:rights`. |
| `dct:rights` | `rights` | `extras['dcat']['rights']` | Direitos de uso / Acesso. |
| `dct:accessRights` | `accessLevel`* | `extras['dcat']['accessRights']` | Nível de acesso (se mapeado corretamente no Contexto JSON-LD). |
| `dct:provenance` | `provenance` | `extras['dcat']['provenance']` | Informação de proveniência. |
| **Distribution** | `distribution` | **Resource** | Entidade `dcat:Distribution` |
| `dct:identifier` | `identifier` | `harvest.dct_identifier` | Identificador da distribuição. |
| `dct:title` | `title` | `title` | Título do recurso. Fallback para nome do ficheiro ou formato. |
| `dct:description` | `description` | `description` | Descrição do recurso. |
| `dcat:accessURL` | `accessURL` | `url` | URL de acesso (usado se `downloadURL` não existir). |
| `dcat:downloadURL` | `downloadURL` | `url` | URL de download direto (prioritário). |
| `dct:format` | `format` | `format` | Formato do ficheiro. |
| `dcat:mediaType` | `mediaType` | `mime` | MIME type (IANA). |
| `dcat:byteSize` | `byteSize` | `filesize` | Tamanho do ficheiro em bytes. |
| `spdx:checksum` | `checksum` | `checksum` | Checksum e algoritmo (MD5, SHA1, etc.). |
| `dct:issued` | `issued` | `harvest.issued_at` | Data de publicação do recurso. |
| `dct:modified` | `modified` | `harvest.modified_at` | Data de modificação do recurso. |
| `dct:license` | `license` | `extras['dcat']['license']` | Licença específica do recurso. |
| `ostros` | - | - | Recursos OGC (`dcat:accessService`) podem gerar recursos do tipo `api`. |

*Nota sobre `accessLevel`: Em `evian.json`, o campo `accessLevel` é comummente usado, mas o uData procura especificamente `dct:accessRights`. A menos que o `@context` faça esse mapeamento, o campo pode ser ignorado.

## Referências e Dependências

A lógica de extração reside principalmente em `udata.core.dataset.rdf`:

1.  **Dataset**:
    *   Criado/Atualizado em `dataset_from_rdf`.
    *   `dataset.license` é inferido de `dct:license` e `dct:rights` tanto do Dataset como das Distributions.
    *   `dataset.extras['dcat']` armazena metadados RDF originais que não têm campo direto no modelo (ex: `provenance`, `accessRights`).

2.  **Resource**:
    *   Criado em `resource_from_rdf`.
    *   `filetype` é fixado como `"remote"`.
    *   Deteta automaticamente serviços OGC e define `resource.type = "api"`.

3.  **Spatial**:
    *   `spatial_from_rdf` lida com múltiplos formatos:
        *   Literal BBox: `"6.5735,46.3912,6.6069,46.4028"` (Visto em `evian.json`) -> Convertido para MultiPolygon.
        *   GeoJSON Literal.
        *   WKT Literal.

4.  **Temporal**:
    *   `temporal_from_rdf` suporta:
        *   Literais ISO 8601 (ano, mês, intervalo "start/end").
        *   Recursos `dct:PeriodOfTime` com `dcat:startDate`/`endDate`.

## Exemplo Prático (`evian.json`)

### Fonte (JSON-LD Parcial)
```json
{
  "@type": "dcat:Dataset",
  "identifier": "https://www.arcgis.com/home/item.html?id=f656...",
  "title": "stationnement velos",
  "description": "<DIV>...</DIV>",
  "keyword": ["mobilite"],
  "spatial": "6.5735,46.3912,6.6069,46.4028",
  "distribution": [
    {
      "@type": "dcat:Distribution",
      "title": "CSV",
      "format": "CSV",
      "mediaType": "text/csv",
      "accessURL": "https://.../csv?layers=5"
    }
  ]
}
```

### Destino (uData Dataset)
```python
dataset.title = "stationnement velos"
dataset.description = "Emplacement et description..." # HTML limpo
dataset.tags = ["mobilite"]
dataset.spatial = {
    "geom": {
        "type": "MultiPolygon",
        "coordinates": [[[[6.5735, 46.3912], ...]]]
    }
}
dataset.harvest.dct_identifier = "https://www.arcgis.com/home/item.html?id=f656..."
dataset.resources = [
    Resource(
        title="CSV",
        format="csv",
        mime="text/csv",
        url="https://.../csv?layers=5",
        filetype="remote"
    )
]
```
