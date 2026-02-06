# Documentação dos Comandos uData

---

## udata

**`Usage: udata [OPTIONS] COMMAND [ARGS]...`**
Cliente de gestão udata

**`Options:`**

- --version
- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`api`** - Operações relacionadas com a API
- **`badges`** - Operações relacionadas com distintivos (badges)
- **`cache`** - Operações relacionadas com cache.
- **`collect`** - Recolher ficheiros estáticos
- **`dataset`** - Operações relacionadas com conjuntos de dados (datasets)
- **`db`** - Operações relacionadas com a base de dados
- **`dcat`** - Operações de diagnóstico DCAT
- **`frequency-reminder`** - Enviar um email único por organização aos membros
- **`generate-fixtures-file`** - Criar ficheiro de exemplo (fixture) baseado em datasets...
- **`harvest`** - Operações de colheita (harvesting) de repositórios remotos
- **`images`** - Operações relacionadas com imagens
- **`import-fixtures`** - Criar dados de exemplo (utilizadores, datasets, ...
- **`info`** - Exibir detalhes sobre o ambiente local
- **`init`** - Inicializar a instância udata (índice de pesquisa, ...
- **`job`** - Operações relacionadas com tarefas (jobs)
- **`licenses`** - Carregar licenças a partir de um ficheiro JSON
- **`linkchecker`** - Operações de verificação de links
- **`metrics`** - Operações relacionadas com métricas
- **`organizations`** - Operações relacionadas com organizações
- **`purge`** - Remover permanentemente dados marcados como apagados.
- **`roles`** - Comandos de funções (roles).
- **`search`** - Operações de pesquisa/indexação
- **`serve`** - Executa um servidor de desenvolvimento.
- **`shell`** - Executar uma shell no contexto da aplicação.
- **`sitemap`** - Gerar sitemap estático para a diretoria indicada.
- **`spatial`** - Operações relacionadas com dados geoespaciais
- **`test`** - Alguns comandos para fins de teste
- **`user`** - Operações relacionadas com utilizadores
- **`users`** - Comandos de utilizador.
- **`worker`** - Operações relacionadas com workers

---

## udata api

**`Usage: udata api [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com a API

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`create-oauth-client`** - Cria uma instância OAuth2Client na BD
- **`postman`** - Exportar a API como uma coleção Postman
- **`swagger`** - Exportar as especificações Swagger
- **`validate`** - Validar a especificação Swagger/OpenAPI com...

---

## udata badges

**`Usage: udata badges [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com distintivos (badges)

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`toggle`** - Alternar um `badge_kind` para um dado `path_or_id`

---

## udata cache

**`Usage: udata cache [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com cache.

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`flush`** - Limpar a cache

---

## udata collect

**`Usage: udata collect [OPTIONS] [PATH]`**
Recolher ficheiros estáticos

**`Options:`**

- **`-ni,`** - --no-input Desativar pedidos de input
- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

---

## udata dataset

**`Usage: udata dataset [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com conjuntos de dados (datasets)

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`archive`** - Arquivar múltiplos datasets a partir de uma lista num ficheiro (um id...
- **`archive-one`** - Arquivar um dataset

---

## udata db

**`Usage: udata db [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com a base de dados

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- check-duplicate-resources-ids
- **`check-integrity`** - Verificar a integridade da base de dados a partir de...
- **`info`** - Exibir informações detalhadas sobre uma migração
- **`migrate`** - Executar migrações de base de dados
- **`status`** - Exibir o estado das migrações de base de dados
- **`unrecord`** - Remover um registo de migração de base de dados.

---

## udata dcat

**`Usage: udata dcat [OPTIONS] COMMAND [ARGS]...`**
Operações de diagnóstico DCAT

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`parse-url`** - Processar os datasets em formato DCAT localizados no URL (debug)

---

## udata harvest

**`Usage: udata harvest [OPTIONS] COMMAND [ARGS]...`**
Operações de colheita (harvesting) de repositórios remotos

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`attach`** - Associar datasets existentes ao seu ID remoto de colheita
- **`backends`** - Listar backends disponíveis
- **`clean`** - Apagar todos os datasets ligados a uma fonte de colheita
- **`create`** - Criar uma nova fonte de colheita
- **`delete`** - Apagar uma fonte de colheita
- **`launch`** - Iniciar a colheita de uma fonte nos workers
- **`purge`** - Remover permanentemente fontes de colheita apagadas
- **`run`** - Executar um harvester de forma síncrona
- **`schedule`** - Agendar um job de colheita para execução periódica
- **`sources`** - Listar todas as fontes de colheita
- **`unschedule`** - Cancelar o agendamento periódico de um job de colheita
- **`validate`** - Validar uma fonte dado o seu identificador

---

## udata images

**`Usage: udata images [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com imagens

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`render`** - Forçar a (re)renderização das imagens armazenadas

---

## udata info

**`Usage: udata info [OPTIONS] COMMAND [ARGS]...`**
Exibir alguns detalhes sobre o ambiente local

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`config`** - Exibir alguns detalhes sobre a configuração local
- **`plugins`** - Exibir alguns detalhes sobre os plugins locais

---

## udata init

**`Usage: udata init [OPTIONS]`**
Inicializar a sua instância udata (índice de pesquisa, utilizador, dados de exemplo...)

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

---

## udata job

**`Usage: udata job [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com tarefas (jobs)

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`list`** - Listar todos os jobs disponíveis
- **`run`** - Executar o job <nome>
- **`schedule`** - Agendar o job <nome> para executar periodicamente dado o...
- **`scheduled`** - Listar jobs agendados.
- **`unschedule`** - Cancelar agendamento do job <nome> com os parâmetros dados.

---

## udata licenses

**`Usage: udata licenses [OPTIONS] [SOURCE]`**
Carregar as licenças a partir de um ficheiro JSON

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

---

## udata linkchecker

**`Usage: udata linkchecker [OPTIONS] COMMAND [ARGS]...`**
Operações de verificação de links

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`check`** - Verificar <número> de URLs que não foram verificados (recentemente)

---

## udata metrics

**`Usage: udata metrics [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com métricas

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`update`** - Atualizar todas as métricas para a data atual

---

## udata organizations

**`Usage: udata organizations [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com organizações

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`attach-zone`** - Associar uma zona <geoid> restrita ao nível para uma dada...
- **`detach-zone`** - Desassociar a zona de uma dada <organização>.

---

## udata purge

**`Usage: udata purge [OPTIONS]`**
Remover permanentemente dados marcados como apagados.
Se nenhuma flag de modelo for dada, todos os modelos serão limpos.

**`Options:`**

- **`-d,`** - --datasets
- **`-r,`** - --reuses
- **`-o,`** - --organizations
- --dataservices
- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

---

## udata roles

**`Usage: udata roles [OPTIONS] COMMAND [ARGS]...`**
Comandos de funções (roles).

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`add`** - Adicionar função ao utilizador.
- **`add_permissions`** - Adicionar permissões à função.
- **`create`** - Criar uma função.
- **`remove`** - Remover função do utilizador.
- **`remove_permissions`** - Remover permissões da função.

---

## udata search

**`Usage: udata search [OPTIONS] COMMAND [ARGS]...`**
Operações de pesquisa/indexação

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`index`** - Inicializar ou reconstruir o índice de pesquisa

---

## udata serve

**`Usage: udata serve [OPTIONS]`**
Executa um servidor local de desenvolvimento udata.
Este servidor local é recomendado apenas para desenvolvimento, mas pode
também ser usado para implementações simples em intranet.
Por defeito, não suporta qualquer tipo de concorrência para simplificar
o debugging. Isto pode ser alterado com a opção --with-threads que irá
ativar multithreading básico.
O reloader e debugger estão ativos por defeito se a flag de debug do Flask
estiver ativada, caso contrário estão desativados.

**`Options:`**

- **`-h,`** - --host TEXT A interface de rede para vincular.
- **`-p,`** - --port INTEGER A porta de rede para vincular.
- **`-r,`** - --reload / -nr, --no-reload
- **`Enable`** - ou desativar o reloader. Por defeito
- **`the`** - o reloader está ativo se o debug estiver ativado.
- **`-d,`** - --debugger / -nd, --no-debugger
- **`Enable`** - ou desativar o debugger. Por defeito
- **`the`** - o debugger está ativo se o debug estiver ativado.
- **`--eager-loading`** - / --lazy-loader
- **`Enable`** - ou desativar o eager loading. Por defeito
- **`eager`** - o eager loading está ativado se o reloader estiver
- desativado.
- **`--with-threads`** - / --without-threads
- **`Enable`** - ou desativar multithreading.
- **`-?,`** - --help Mostrar esta mensagem e sair.

---

## udata shell

**`Usage: udata shell [OPTIONS]`**
Executar uma shell Python interativa no contexto de uma aplicação Flask.
A aplicação irá preencher o namespace padrão desta shell de acordo
com a sua configuração.
Isto é útil para executar pequenos trechos de código de gestão sem
ter que configurar manualmente a aplicação.

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

---

## udata sitemap

**`Usage: udata sitemap [OPTIONS]`**
Gerar sitemap estático para a diretoria indicada.

**`Options:`**

- **`-o,`** - --output-directory TEXT Diretoria de saída para os ficheiros do sitemap.
- **`-v,`** - --verbose
- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

---

## udata spatial

**`Usage: udata spatial [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com dados geoespaciais

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`load`** - Carregar um arquivo de geozones a partir de <nomedoficheiro>
- **`migrate`** - Migrar zones de IDs antigos para novos em datasets.

---

## udata test

**`Usage: udata test [OPTIONS] COMMAND [ARGS]...`**
Alguns comandos para fins de teste

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`log`** - Testar logging

---

## udata user

**`Usage: udata user [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com utilizadores

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`activate`** - Ativar um utilizador existente (validar o seu email...
- **`create`** - Criar um novo utilizador
- **`delete`** - Apagar um utilizador existente
- password
- **`rotate-password`** - Pedir ao utilizador rotação de password no próximo login e redefinir...
- **`set-admin`** - Definir um utilizador como administrador

---

## udata users

**`Usage: udata users [OPTIONS] COMMAND [ARGS]...`**
Comandos de utilizador.
Para comandos que requerem um USER - passe qualquer atributo de identidade.

**`Options:`**

- **`-?,`** - -h, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`activate`** - Ativar um utilizador.
- **`change_password`** - Alterar administrativamente a palavra-passe de um utilizador.
- **`create`** - Criar um novo utilizador com um ou mais atributos usando a
- **`syntax:`** - atrb:valor. Se atrb não for definido, assume-se 'email'.
- **`Identity`** - Valores de atributos de identidade serão validados usando o
- **`configured`** - confirm_register_form; contudo, qualquer
- **`attribute:value`** - par atrb:valor ADICIONAL será enviado para datastore.create_user
- **`deactivate`** - Desativar um utilizador.
- **`reset_access`** - Redefinir todas as credenciais de autenticação do utilizador.

---

## udata worker

**`Usage: udata worker [OPTIONS] COMMAND [ARGS]...`**
Operações relacionadas com workers

**`Options:`**

- **`-h,`** - -?, --help Mostrar esta mensagem e sair.

**`Commands:`**

- **`start`** - Iniciar um worker
- **`status`** - Listar tarefas em fila agregadas por nome
- **`tasks`** - Exibir tarefas registadas com a sua fila

---

## Lista de Jobs Schedulables

Lista de jobs obtida via API (`GET /api/1/workers/jobs/schedulables`) ou console (`udata worker tasks`).
Estes jobs podem ser agendados para execução periódica (via Celery Beat).

| Job                                  | Descrição                                                           | Em uso? | Horário/Agendamento |
| :----------------------------------- | :------------------------------------------------------------------ | :-----: | :------------------ |
| **`bind-tabular-dataservice`**       | Vincula recursos tabulares a dataservices para API/Preview.         |   Sim   | Trigger/Sob demanda |
| **`check-integrity`**                | Verifica integridade referencial do banco de dados.                 |   Sim   | Semanal (Padrão)    |
| **`compute-geozones-metrics`**       | Calcula métricas baseadas em zonas geográficas.                     |   Sim   | Diário (Padrão)     |
| **`compute-site-metrics`**           | Calcula métricas globais do portal (números da home).               |   Sim   | Diário (Padrão)     |
| **`count-tags`**                     | Recalcula contadores de uso das tags.                               |   Sim   | Diário (Padrão)     |
| **`delete-inactive-users`**          | Exclui usuários considerados inativos.                              |   Não   | Manual              |
| **`export-csv`**                     | Gera arquivos CSV com metadados do catálogo.                        |   Sim   | Diário (se config)  |
| **`harvest`**                        | Executa a colheita de dados (harvesters) agendados.                 |   Sim   | Varia por fonte     |
| **`notify-inactive-users`**          | Envia notificações para usuários inativos.                          |   Não   | Manual              |
| **`piwik-bulk-track-api`**           | Envia dados de rastreamento pendentes para o Piwik/Matomo.          |   Sim   | Regular (ex: 15min) |
| **`purge-chunks`**                   | Limpa fragmentos de uploads incompletos ou órfãos.                  |   Sim   | Diário              |
| **`purge-datasets`**                 | Exclui fisicamente datasets marcados como deletados (soft-deleted). |   Sim   | Diário              |
| **`purge-harvest-jobs`**             | Limpa histórico de execuções de harvest antigas.                    |   Sim   | Diário              |
| **`purge-harvesters`**               | Exclui fisicamente harvesters marcados como deletados.              |   Sim   | Diário              |
| **`purge-organizations`**            | Exclui fisicamente organizações marcadas como deletadas.            |   Sim   | Diário              |
| **`purge-reuses`**                   | Exclui fisicamente reutilizações marcadas como deletadas.           |   Sim   | Diário              |
| **`send-frequency-reminder`**        | Envia lembretes de periodicidade aos produtores de dados.           |   Sim   | Diário (06:00)      |
| **`test-default-queue`**             | Job de teste para a fila padrão.                                    |   Não   | -                   |
| **`test-error`**                     | Job para testar geração e registro de erros.                        |   Não   | -                   |
| **`test-high-queue`**                | Job de teste para a fila de alta prioridade.                        |   Não   | -                   |
| **`test-log`**                       | Job para testar geração de logs.                                    |   Não   | -                   |
| **`test-low-queue`**                 | Job de teste para a fila de baixa prioridade.                       |   Não   | -                   |
| **`update-datasets-reuses-metrics`** | Atualiza métricas (views, downloads) de datasets e reuses.          |   Sim   | Diário              |
| **`update-metrics`**                 | Atualiza métricas gerais diárias.                                   |   Sim   | Diário              |

> **Nota:** O status "Em uso" e o "Horário" devem ser preenchidos conforme a configuração do ambiente (`udata.cfg` -> `CELERY_BEAT_SCHEDULE`).
