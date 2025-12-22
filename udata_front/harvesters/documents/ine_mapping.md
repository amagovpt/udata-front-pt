# Mapa de Campos: INE (XML Indicators) para uData Database

Este documento mapeia os campos obtidos do harvester `INEBackend` (XML de Indicadores do INE) para os campos da tabela/coleção `datasets` na base de dados do uData (modelo `Dataset`).

## Fonte de Dados

**API INE**: Instituto Nacional de Estatística - XML de Indicadores
- URLs suportadas:
  - `https://www.ine.pt/ine/xml_indic.jsp?opc=2` (endpoint padrão)
  - `https://www.ine.pt/ine/xml_indic_hvd.jsp?opc=3` (endpoint HVD)
- Protocolo: XML via HTTP GET
- Formato de resposta: XML com estrutura de indicadores
- Parâmetros:
  - `varcd` - ID do indicador/dataset
  - `lang` - Idioma (padrão: PT)
  - `opc` - Opção de operação

## Resumo do Mapeamento

| Campo Fonte (INE XML) | Elemento XML | Campo Destino (uData `Dataset`) | Notas / Lógica |
| :--- | :--- | :--- | :--- |
| **Catalog** | | | |
| `language` | `<language>` | `extras['ine:language']` | Idioma do catálogo (ex: PT). |
| `extraction_date` | `<extraction_date>` | `extras['ine:extraction_date']` | Data de extração do XML. |
| **Dataset** | | | |
| `id` | `<indicator id="...">` | `remote_id` (HarvestItem) | ID do indicador. |
| `varcd` | `<varcd>` | `extras['ine:varcd']` | Código interno do indicador. |
| `title` | `<title>` | `title` | Título do indicador. |
| `description` | `<description>` | `description` | Descrição do indicador. |
| - | - | `license` | Fixo: `cc-by` (Creative Commons Attribution). |
| `periodicity` | `<periodicity>` | `frequency` | Mapeado via `PERIODICITY_MAP`. |
| `last_update` | `<last_update>` | `modified` | Parseado como data (`%d-%m-%Y`). |
| - | - | `tags` | Adiciona tag fixa: `'ine.pt'`. |
| `keywords` | `<keywords>` | `tags` | Texto parseado e dividido. |
| `theme` | `<theme>` | `tags` | Adicionado às tags (múltiplos). |
| `subtheme` | `<subtheme>` | `tags` | Adicionado às tags (múltiplos). |
| `source` | `<source>` | `tags` | Adicionado às tags. |
| `geo_lastlevel` | `<geo_lastlevel>` | `tags` | Adicionado às tags. |
| `last_period` | `<last_period_available>` | `extras['ine:last_period_available']` | Extra metadata. |
| `update_type` | `<update_type>` | `extras['ine:update_type']` | Extra metadata. |
| **Resources** | | | |
| `bdd_url` | `<html/bdd_url>` | `Resource` | Tipo: `documentation`, Filetype: `remote`, Formato: `html`, Título: `Página do indicador (HTML)`. |
| `metainfo_url` | `<html/metainfo_url>` | `Resource` | Tipo: `documentation`, Filetype: `remote`, Formato: `html`, Título: `Metainformação (HTML)`. |
| `json_dataset` | `<json/json_dataset>` | `Resource` | Tipo: `main`, Filetype: `remote`, Formato: `json`, Título: `Dados do indicador (JSON)`. |
| `json_metainfo` | `<json/json_metainfo>` | `Resource` | Tipo: `documentation`, Filetype: `remote`, Formato: `json`, Título: `Metainformação (JSON)`. |

## Detalhes Específicos

### 1. Tratamento da Fonte (XML)

O harvester inclui uma lógica robusta para processar a resposta da fonte:
- **Limpeza de Texto**: Remove automaticamente textos introdutórios que não façam parte do XML (comum em visualizações de browsers).
- **Encoding**: Tenta decodificar como UTF-8, recuando para Latin-1 se necessário.
- **Parsing**: Utiliza `minidom` após a limpeza do conteúdo.

### 2. Harvest Otimizado (Cache)

O harvester foi otimizado para lidar com a lentidão da infraestrutura do INE:

#### Fase 1: Descoberta e Cache
O harvester obtém o catálogo completo uma única vez e armazena todos os indicadores em memória:
```python
# Pre-popula o cache para evitar novos downloads
self._indicator_cache = {}
for propNode in doc.getElementsByTagName('indicator'):
    currentId = propNode.getAttribute('id')
    self._indicator_cache[str(currentId)] = propNode
    datasetIds.add(currentId)
```

#### Fase 2: Processamento Instantâneo
Ao processar cada dataset, o harvester consulta o cache. Se os dados estiverem lá, o processamento é local (sem rede):
```python
if str(item.remote_id) in self._indicator_cache:
    target = self._indicator_cache[str(item.remote_id)]
    # ... processa localmente ...
```
Isso reduz o tempo de harvest de horas para apenas alguns minutos.

### 3. Construção da URL de Metadados

A URL é construída dinamicamente preservando a estrutura da URL base:
```python
parsed = urlparse(base_url)
qs = parse_qs(parsed.query)

# Garante idioma PT
if 'lang' not in qs or not qs['lang']:
    qs['lang'] = ['PT']

# Adiciona ID do dataset
qs['varcd'] = [str(item.remote_id)]

# Reconstrói a URL
new_query = urlencode({k: v[0] for k, v in qs.items()})
final_url = urlunparse(parsed._replace(query=new_query))
```

**Exemplo:**
- Base: `https://www.ine.pt/ine/xml_indic.jsp?opc=2`
- ID: `0011234`
- Final: `https://www.ine.pt/ine/xml_indic.jsp?opc=2&lang=PT&varcd=0011234`

### 4. Localização do Indicador Correto

O XML pode conter múltiplos indicadores. O harvester procura o indicador específico:
```python
target = None
for propNode in properties:
    if propNode.hasAttribute('id') and str(propNode.getAttribute('id')) == str(item.remote_id):
        target = propNode
        break

if not target:
    # Fallback: usa o primeiro indicador
    target = properties[0] if properties else None
```

### 5. Mapeamento de Frequência (Periodicidade)

O campo `<periodicity>` é mapeado para valores padrão do uData:

| INE periodicity | uData frequency |
| :--- | :--- |
| Anual | `annual` |
| Semestral | `semiannual` |
| Trimestral | `quarterly` |
| Mensal | `monthly` |
| Decenal | `unknown` |
| Quinzenal | `biweekly` |
| Semenal | `weekly` |
| Diário | `daily` |
| Contínuo | `continuous` |
| Irregular | `irregular` |
| Pontual | `punctual` |
| Quinquenal | `quinquennial` |
| Bienal | `biennial` |
| Trienal | `triennial` |
| Não periódica | `irregular` |

**Nota sobre Validação**: Se o valor vindo do INE não estiver no mapeamento acima ou não for suportado pelo uData, o harvester preenche automaticamente como `unknown` para garantir a integridade do banco de dados.

### 6. Extração de Keywords e Tags

#### 6.1 Parsing do Elemento `<keywords>`
As keywords são extraídas do elemento XML e divididas por múltiplos separadores:
```python
for kn in target.getElementsByTagName('keywords'):
    text = self._get_text(kn)
    if text:
        # Divide por: ; , / ou padrões como " - " ou " | "
        parts = re.split(r'[;,/]|\s+-\s+|\s+\|\s+', text)
        for p in parts:
            p = p.strip().strip(',')
            if p:
                keywordSet.add(p.lower())
```

#### 6.2 Adição de Theme, Subtheme, Source e Geo level
Os elementos `<theme>`, `<subtheme>`, `<source>` e `<geo_lastlevel>` também são adicionados como tags:
```python
for tagname in ('theme', 'subtheme', 'source', 'geo_lastlevel'):
    for tn in target.getElementsByTagName(tagname):
        val = self._get_text(tn)
        if val:
            keywordSet.add(val.lower())
```

### 7. Tags Finais
As tags são ordenadas alfabeticamente e a tag `'ine.pt'` é garantida:
```python
dataset.tags = sorted(keywordSet)
if 'ine.pt' not in dataset.tags:
    dataset.tags.append('ine.pt')
```

### 8. Recursos

O harvester extrai quatro tipos de recursos se disponíveis no XML:

1.  **Página do indicador (HTML)**: URL direta para a página do indicador no site do INE (`bdd_url`).
2.  **Metainformação (HTML)**: URL para a página de metainformação (`metainfo_url`).
3.  **Dados do indicador (JSON)**: Endpoint da API para os dados em JSON (`json_dataset`).
4.  **Metainformação (JSON)**: Endpoint da API para os metadados em JSON (`json_metainfo`).

### 9. Extras

Informações específicas do INE e do catálogo são armazenadas no campo `extras`:
- `ine:language`: Idioma do arquivo de origem.
- `ine:extraction_date`: Data em que os dados foram extraídos.
- `ine:varcd`: Identificador de variável oficial do INE.
- `ine:last_period_available`: Último período com dados disponíveis.
- `ine:update_type`: Tipo de atualização.

## Estrutura XML Esperada

```xml
<catalog>
  <extraction_date><![CDATA[ Friday, 19 December 2025 ]]></extraction_date>
  <language>PT</language>
  <indicator id="0001461">
    <theme><![CDATA[ Agricultura, floresta e pescas ]]></theme>
    <subtheme><![CDATA[ Produção vegetal ]]></subtheme>
    <keywords>INE, Árvores, fruto, oliveiras</keywords>
    <title><![CDATA[ Árvores de fruto e oliveiras vendidas (N.º) pelos viveiros ]]></title>
    <description><![CDATA[ Árvores de fruto e oliveiras vendidas (N.º) pelos viveiros por Local de origem... ]]></description>
    <geo_lastlevel><![CDATA[ NUTS II ]]></geo_lastlevel>
    <source><![CDATA[ INE, Inquérito à venda de árvores de fruto e oliveiras ]]></source>
    <dates>
      <last_update><![CDATA[ 28-10-2025 ]]></last_update>
    </dates>
    <periodicity><![CDATA[ Anual ]]></periodicity>
    <html>
      <bdd_url><![CDATA[ https://www.ine.pt/xurl/indx/0001461/PT ]]></bdd_url>
    </html>
    <json>
      <json_dataset><![CDATA[ https://www.ine.pt/ine/json_indicador/... ]]></json_dataset>
    </json>
  </indicator>
</catalog>
```


## Campos Não Mapeados
1. 
Os seguintes campos do XML **não são mapeados**:
- `date_published` - Não encontrado no exemplo base mas presente em algumas variantes.

**Nota:** Este harvester foi refatorado para capturar a totalidade dos campos relevantes presentes no XML do INE, tornando-o funcional para a criação de datasets completos com recursos e metadados detalhados.

