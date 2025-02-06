import os
import requests

# Opções de fontes disponíveis
sources = {
    "Production": "https://dados.gov.pt/api/1/site/catalog.xml",
    "Preprod": "https://preprod.dados.gov.pt/api/1/site/catalog.xml",
    "Test": "https://10.55.37.38/api/1/site/catalog.xml",
    "Development": "https://172.31.204.12/api/1/site/catalog.xml"
}

# Solicita ao usuário que escolha a fonte
print("Escolha a fonte para criar o catálogo:")
for key in sources:
    print(f"- {key}")

while True:
    source_choice = input("Digite o nome da fonte desejada: ")
    if source_choice in sources:
        BASE_URL = sources[source_choice]
        break
    print("Opção inválida. Tente novamente.")

# Pergunta se deseja adicionar uma tag
add_tag = input("Deseja adicionar uma tag à consulta? (s/n): ").strip().lower()
tag_param = ""
if add_tag == "s":
    tag = input("Digite a tag desejada: ").strip()
    tag_param = f"&tag={tag}"

# Pergunta pelo formato do arquivo de saída
output_format = input("Digite o formato do arquivo de saída (ex: xml, json, txt): ").strip()
output_file = os.path.join(os.getcwd(), f"catalog.{output_format}")

# Inicializa o contador de páginas
page = 1

# Abre o arquivo para escrita
with open(output_file, "w", encoding="utf-8") as file:
    while True:
        try:
            # Monta a URL da requisição
            url = f"{BASE_URL}?page={page}{tag_param}"
            print(f"Fetching: {url}")
            
            # Faz a requisição HTTP
            response = requests.get(url, verify=False)
            
            # Verifica se a resposta indica o fim das páginas
            if response.status_code == 404:
                print("Recebido status 404. Nenhuma página adicional disponível. Parando.")
                break

            if response.status_code != 200:
                print(f"Página {page} retornou {response.status_code}. Pulando.")
                page += 1
                continue
            
            # Escreve o conteúdo da página no arquivo
            file.write(response.text)
            
            # Incrementa o contador de páginas
            page += 1
        
        except requests.RequestException as e:
            print(f"Ocorreu um erro: {e}")
            break

print(f"Processo concluído. Resultados salvos em {output_file}.")
