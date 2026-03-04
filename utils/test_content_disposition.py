import os
import sys
import json
import urllib.request
import urllib.error

# Obter o BASE_URL das variáveis de ambiente ou usar o valor por defeito do ambiente local
BASE_URL = os.environ.get("SITE_URL", "http://dev.local:7000")


def check_content_disposition(url):
    """
    Testa um URL específico para verificar se inclui o header 'Content-Disposition' com 'attachment'.
    Isso assegura que o ficheiro vai ser descarregado (download) em vez de ser renderizado
    inline na página.
    """
    print(f"A testar URL: {url}")
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                print(f"  [ ERRO ] O pedido retornou o status HTTP {response.status}\n")
                return False

            disposition = response.headers.get("Content-Disposition", "")
            content_type = response.headers.get("Content-Type", "")

            print(f"  - Content-Type: {content_type}")
            print(f"  - Content-Disposition: '{disposition}'")

            if not disposition:
                print(
                    "  [ FALHA ] Header 'Content-Disposition' nulo/ausente. O ficheiro pode abrir na página em vez de descarregar.\n"
                )
                return False

            if "attachment" in disposition.lower():
                print(
                    "  [ SUCESSO ] O ficheiro inclui 'attachment'. Será feito o download automaticamente.\n"
                )
                return True
            else:
                print(
                    "  [ FALHA ] O ficheiro não inclui 'attachment' no Content-Disposition. Pode abrir na página!\n"
                )
                return False

    except urllib.error.URLError as e:
        print(f"  [ ERRO ] Falha na conexão ao URL: {e.reason}\n")
        return False
    except Exception as e:
        print(f"  [ ERRO ] Ocorreu um erro: {e}\n")
        return False


def run_automated_tests():
    """
    Obtém uma lista de ficheiros (resources) do servidor local e testa o comportamento do seu download.
    """
    api_url = f"{BASE_URL}/api/1/datasets/67c5a3b3b50fe67ba7aa1905/"
    print(f"A procurar resources (ficheiros) do dataset específico em {api_url}...\n")

    try:
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            dataset = json.loads(response.read().decode("utf-8"))

        test_urls = []
        # Percorrer os resources do dataset específico
        for resource in dataset.get("resources", []):
            # O udata costuma disponibilizar o download do resource pelo link:
            download_url = resource.get("url") or resource.get("download_url")
            if download_url:
                test_urls.append(download_url)

            if len(test_urls) >= 5:  # Vamos testar apenas os primeiros 5 ficheiros
                break

        if not test_urls:
            print(
                "⚠️ Não foram encontrados datasets com resources válidos no servidor local para testar."
            )
            print(
                f"Podes testar manualmente passando o URL como argumento:\n  python {os.path.basename(__file__)} <URL>\n"
            )
            return

        print(f"Foram encontrados {len(test_urls)} ficheiros. A iniciar testes...\n")
        print("-" * 60)

        passed = 0
        for url in test_urls:
            if check_content_disposition(url):
                passed += 1

        print("-" * 60)
        if passed == len(test_urls):
            print(
                f"✅ CONCLUÍDO: Todos os testes ({passed}/{len(test_urls)}) passaram!"
            )
            print(
                "Resultado: Todos os ficheiros serão descarregados corretamente e não abertos na página."
            )
        else:
            print(
                f"❌ ATENÇÃO: {len(test_urls) - passed} de {len(test_urls)} ficheiros falharam no teste."
            )
            print(
                "Resultado: Alguns ficheiros não possuem o cabeçalho 'Content-Disposition: attachment'..."
            )

    except urllib.error.URLError as e:
        print(
            f"❌ Não foi possível contactar o servidor local ({BASE_URL}). Verifica se o docker-compose / udata está em execução e se acessas ao link corretamente. (Erro: {e.reason})"
        )
    except Exception as e:
        print(f"❌ Ocorreu um erro ao obter datasets: {e}")


if __name__ == "__main__":
    # Permite passar um URL pela command-line para testar ficheiros específicos pontualmente
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"\nIniciando teste manual para: {test_url}\n")
        check_content_disposition(test_url)
    else:
        run_automated_tests()
