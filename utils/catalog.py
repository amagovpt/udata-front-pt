import os
import requests
import xml.etree.ElementTree as ET
import csv
import time

sources = {
    "1": {"name": "Production", "url": "https://dados.gov.pt/api/1/site/catalog.xml"},
    "2": {"name": "Preprod", "url": "https://preprod.dados.gov.pt/api/1/site/catalog.xml"},
    "3": {"name": "Test", "url": "https://10.55.37.38/api/1/site/catalog.xml"},
    "4": {"name": "Development", "url": "https://172.31.204.12/api/1/site/catalog.xml"},
    "5": {"name": "Local", "url": "http://localhost:7000/api/1/site/catalog.xml"}
}

print("Escolha a fonte para criar o catálogo:")
for key, value in sources.items():
    print(f"{key} - {value['name']}")

while True:
    source_choice = input("Digite o número da fonte desejada: ")
    if source_choice in sources:
        BASE_URL = sources[source_choice]["url"]
        break
    print("Opção inválida. Tente novamente.")

add_tag = input("Deseja adicionar uma tag à consulta? (s/n): ").strip().lower()
tag_param = ""
if add_tag == "s":
    tag = input("Digite a tag desejada: ").strip()
    tag_param = f"&tag={tag}"

output_format = input("Digite o formato do arquivo de saída (ex: xml, txt, csv): ").strip()
output_file = os.path.join(os.getcwd(), f"catalog.{output_format}")

page = 1
all_records = []
max_retries = 3

def xml_to_csv(xml_content, csv_file):
    root = ET.fromstring(xml_content)
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:  # Corrigido para 'csvfile'
        csvwriter = csv.writer(csvfile)  # Corrigido para 'csvfile'
        headers = [elem.tag for elem in root[0]]
        csvwriter.writerow(headers)
        for record in root:
            csvwriter.writerow([record.find(header).text if record.find(header) is not None else '' for header in headers])

while True:
    try:
        retry_count = 0
        success = False
        while retry_count < max_retries:
            url = f"{BASE_URL}?page={page}{tag_param}" if "?" not in BASE_URL else f"{BASE_URL}&page={page}{tag_param}"
            print(f"Fetching: {url} (Tentativa {retry_count + 1})")

            try:
                response = requests.get(url, verify=False)
            except requests.RequestException as e:
                print(f"Erro de conexão: {e}. Tentando novamente...")
                retry_count += 1
                time.sleep(1)
                continue

            if response.status_code == 404 or not response.text.strip():
                print(f"Fim do processo, página {page}: {response.status_code}. Nenhum dado restante. Parando.")
                success = True
                break

            if response.status_code != 200:
                print(f"Erro na página {page}: {response.status_code}. Tentativa {retry_count + 1} de {max_retries}.")
                retry_count += 1
                time.sleep(1)
                continue

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as e:
                print(f"Erro ao processar XML da página {page}: {e}. Tentando novamente...")
                retry_count += 1
                time.sleep(1)
                continue

            if len(root) == 0:
                print(f"Página {page} não contém mais registros. Parando.")
                success = True
                break

            all_records.extend(root)
            page += 1
            success = True
            break

        if not success:
            print(f"Falha após {max_retries} tentativas na página {page}. Pulando para a próxima página.")
            page += 1
        else:
            if response.status_code == 404 or not response.text.strip() or len(root) == 0:
                break

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        break

if all_records:
    root_element = ET.Element("catalog")
    root_element.extend(all_records)
    full_xml_content = ET.tostring(root_element, encoding="utf-8").decode("utf-8")

    if output_format == "csv":
        xml_to_csv(full_xml_content, output_file)
    else:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(full_xml_content)

    print(f"Processo concluído. Resultados salvos em {output_file}.")
else:
    print("Nenhum dado foi coletado. Nenhum arquivo foi gerado.")