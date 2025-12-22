# Mapa de Campos: evian.json para uData Database

Este documento mapeia os campos do arquivo fonte `udata/harvest/tests/dcat/evian.json` (formato DCAT-AP JSON-LD) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Resumo do Mapeamento

| Campo Fonte (`evian.json`) | Caminho RDF | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Dataset** | | | |
| `title` | `dct:title` | `title` | |
| `description` | `dct:description` | `description` | Sanitizado (HTML permitido mas limpo). Se ausente, usa `dct:abstract`. |
| `identifier` | `dct:identifier` | `harvest.dct_identifier` | O identificador remoto é armazenado nos metadados de harvest. |
| `landingPage` | `dcat:landingPage` | `harvest.remote_url` | |
| `keyword` | `dcat:keyword` | `tags` | |
| `theme` | `dcat:theme` | `tags` | Os temas são misturados com as keywords nas `tags`. |
| `issued` | `dct:issued` | `harvest.issued_at` | Armazenado em `dataset.harvest`. A data de criação do dataset (`created_at`) pode assumir este valor se for criação. |
| `modified` | `dct:modified` | `harvest.modified_at` | Armazenado em `dataset.harvest`. |
| `spatial` | `dct:spatial` | `spatial` | Convertido para GeoJSON (MultiPolygon). |
| `license` | `dct:license` | `license` | Tenta corresponder a uma licença existente via URL ou título. Também armazenado em `extras.dcat.license`. |
| `publisher.name` | `dct:publisher` | `organization` (Contextual) | O mapeamento para a `organization` do uData geralmente depende da configuração do harvester ou contexto, não é automático apenas pelo nome no JSON. Se mapeado, o dataset pertence a essa organização. |
| `contactPoint` | `dcat:contactPoint` | `contact_points` | Cria objetos `ContactPoint`. |
| &nbsp;&nbsp;`fn` | `vcard:fn` | `ContactPoint.name` | Role: "contact". |
| &nbsp;&nbsp;`hasEmail` | `vcard:hasEmail` | `ContactPoint.email` | |
| **Distribution** | `dcat:distribution` | **Resource** | Item na lista `resources` do Dataset. |
| `title` | `dct:title` | `title` | |
| `description` | `dct:description` | `description` | |
| `accessURL` | `dcat:accessURL` | `url` | URL principal do recurso. |
| `downloadURL` | `dcat:downloadURL` | `url` | Se `accessURL` não existir. |
| `format` | `dct:format` | `format` | Normalizado (ex: 'csv', 'json'). |
| `mediaType` | `dcat:mediaType` | `mime` | Ex: 'text/csv'. |
| `byteSize` | `dcat:byteSize` | `filesize` | |
| `checksum` | `spdx:checksum` | `checksum` | Objeto com `type` e `value`. |
| `issued` | `dct:issued` | `harvest.issued_at` | No recurso. |
| `modified` | `dct:modified` | `harvest.modified_at` | No recurso. |

## Detalhes Específicos

### 1. Datas (`issued`, `modified`)
No uData, as datas de harvest não sobrescrevem diretamente `dataset.created_at_internal` ou `dataset.last_modified_internal` (que são datas de sistema), mas são armazenadas na estrutura `harvest`:
- `dataset.harvest.issued_at`
- `dataset.harvest.modified_at`

### 2. Identificadores
O `identifier` do DCAT ("https://www.arcgis.com/...") é armazenado em `dataset.harvest.dct_identifier`.
A URL de origem (`landingPage`) vai para `dataset.harvest.remote_url`.

### 3. Organização (`publisher`)
O campo `publisher` no JSON:
```json
"publisher": {
    "name": "Ville d'Evian-les-Bains"
}
```
Não garante a atribuição automática à organização "Ville d'Evian-les-Bains" a menos que o backend de harvest (DcatBackend) consiga resolver este nome para uma organização existente na base do uData, ou se a harvest for executada especificamente para essa organização. O código de parsing RDF (`dataset_from_rdf`) usa o publisher para criar um `ContactPoint` com role="publisher".

### 4. Distribuições (`distribution`)
Cada item em `distribution` se torna um `Resource`.
- O `accessURL` é preferido como a URL do recurso.
- Metadados como `format` e `mediaType` são preenchidos.
