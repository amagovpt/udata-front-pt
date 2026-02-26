# Testes E2E — Playwright

Este documento contém a lista completa de todos os testes _End-to-End_ (E2E) realizados pelo Playwright no projeto **udata-front-pt**.

Estes testes encontram-se definidos em: `tests/smoke/smoke-post-deploy.spec.ts`.

## 1. Home Page — Disponibilidade

- **Home Page responde com HTTP 200**: Verifica se a página inicial está acessível.
- **Título contém 'dados.gov' ou 'uData'**: Valida se o título da página está correto de acordo com a configuração.
- **Elemento `<h1>` é visível na Home Page**: Garante que o cabeçalho principal é renderizado.
- **Página contém atributo lang='pt' no HTML**: Verifica a internacionalização básica da página.

## 2. Pesquisa — Resultados da Base de Dados

- **Barra de pesquisa está visível e funcional**: Confirma a presença do componente de pesquisa.
- **Pesquisar 'dados' retorna resultados da API**: Valida a integração entre a interface de pesquisa e os serviços de Elasticsearch/MongoDB.

## 3. Download de Recurso de Dataset

- **Página de dataset contém link de download acessível**: Verifica se é possível navegar até um dataset e se os links de download de recursos estão presentes e funcionais (teste de integridade via HEAD request).

## 4. Integridade de Assets — Imagens & CSS

- **Home Page não tem imagens partidas**: Deteta erros técnicos ou caminhos incorretos em imagens da página inicial.
- **Páginas carregam folhas de estilo CSS corretamente**: Garante que não existem erros 404/500 no carregamento de estilos.
- **Página /datasets não tem imagens partidas**: Valida a integridade visual na listagem de datasets (logos e thumbnails).
- **Assets estáticos do volume FS são servidos (/s/)**: Verifica se ficheiros servidos a partir do volume de armazenamento (prefixo `/s/`) estão acessíveis.

## 5. Redefinição de Palavra-passe

- **Abordagem POST via formulário**: Simula a submissão do formulário de reset de password (bypass reCAPTCHA) e valida a resposta 2xx/3xx do servidor.
- **Abordagem POST direto**: Valida a segurança do fluxo via extração de CSRF e submissão direta à API do Flask-Security.

## 6. Organizações

- **Página de organizações carrega e contém cards**: Verifica se a listagem de organizações está a renderizar corretamente e se contém dados reais da BD.

## 7. Reutilizações

- **Página de reutilizações carrega e contém cards**: Semelhante às organizações, valida a listagem de reutilizações e a presença de indicadores visuais.

## 8. API REST — Endpoints

- **Raiz da API (/api/1/) responde com HTTP < 400**: Verifica a saúde básica da API.
- **Endpoint Datasets responde com JSON**: Valida funcionalidade e formato de saída para dados de datasets.
- **Endpoint Organizações responde com JSON**: Valida funcionalidade e formato de saída para dados de organizações.
- **Endpoint Reutilizações responde com JSON**: Valida funcionalidade e formato de saída para dados de reutilizações.

## 9. Navegação e Links Internos

- **Links principais da navegação estão acessíveis**: Testa os links de topo (datasets, services, reuses, organizations).
- **Links do footer estão acessíveis**: Valida links de rodapé, incluindo FAQs, Termos, Acessibilidade e Dashboard.

## 10. Dashboard — Estatísticas

- **Página de dashboard carrega com indicadores**: Confirma que a página de estatísticas está ONLINE e apresenta dados numéricos (contagem de datasets, recursos, etc).

## 11. Páginas Estáticas

- **Páginas legais e informativas respondem com HTTP < 400**: Valida a disponibilidade de páginas como "Sobre nós", "Licenças", "Acessibilidade", etc.

## 12. Formulário de Contacto

- **Página de contacto carrega com formulário**: Verifica a presença de um formulário de contacto funcional e os respetivos campos obrigatórios.
