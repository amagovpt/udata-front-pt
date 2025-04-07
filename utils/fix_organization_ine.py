import sys
import subprocess
import os

# Verificar e instalar pacotes necessários
def install_requirements():
    required_packages = ['pymongo', 'tqdm']
    
    print("Verificando e instalando pacotes necessários...")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} já está instalado")
        except ImportError:
            print(f"Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} instalado com sucesso")
    
    print("Todos os pacotes necessários estão instalados.\n")

# Instalar pacotes necessários
install_requirements()

# Agora importamos os pacotes
from pymongo import MongoClient
from bson import ObjectId
from tqdm import tqdm

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def select_environment():
    """Exibe o menu para seleção do ambiente."""
    clear_screen()
    print("=" * 50)
    print("SISTEMA DE MIGRAÇÃO DE DATASETS, FIX ORGANIZAÇÃO INE")
    print("=" * 50)
    print("\nSelecione o ambiente para executar o script:")
    print("1. Produção (10.51.37.51)")
    print("2. Pré-produção (10.53.37.52)")
    print("3. IP Personalizado")
    print("0. Sair")
    
    choice = input("\nEscolha uma opção (0-3): ")
    
    if choice == '1':
        return "10.51.37.51"
    elif choice == '2':
        return "10.53.37.52"
    elif choice == '3':
        custom_ip = input("Digite o IP do servidor MongoDB: ")
        return custom_ip
    elif choice == '0':
        print("Saindo do programa.")
        sys.exit(0)
    else:
        print("Opção inválida. Tente novamente.")
        input("Pressione Enter para continuar...")
        return select_environment()

def migrate_datasets(mongo_ip):
    """Executa a migração de datasets entre organizações."""
    # Configuração do MongoDB
    MONGO_URI = f"mongodb://{mongo_ip}:27017"
    DATABASE_NAME = "udata"
    
    print(f"\nConectando ao MongoDB em {MONGO_URI}...")
    
    try:
        # Conectar ao MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Verificar conexão
        client.server_info()
        print("Conexão estabelecida com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        input("Pressione Enter para voltar ao menu principal...")
        return False
    
    db = client[DATABASE_NAME]
    dataset_collection = db["dataset"]
    organization_collection = db["organization"]
    
    # Solicitar IDs das organizações
    try:
        origin_id_str = "616a16170781900668c0637a"
        target_id_str = "5ae97fa2c8d8c915d5faa3c0"
        
        origin_organization_id = ObjectId(origin_id_str)
        target_organization_id = ObjectId(target_id_str)
    except Exception as e:
        print(f"Erro ao converter ID: {e}")
        print("Certifique-se de inserir IDs válidos no formato hexadecimal.")
        client.close()
        input("Pressione Enter para voltar ao menu principal...")
        return False
    
    # Verificar se as organizações existem
    origin_org = organization_collection.find_one({"_id": origin_organization_id})
    target_org = organization_collection.find_one({"_id": target_organization_id})
    
    if not origin_org:
        print(f"ERRO: Organização de origem com ID {origin_organization_id} não encontrada.")
        client.close()
        input("Pressione Enter para voltar ao menu principal...")
        return False
    
    if not target_org:
        print(f"ERRO: Organização de destino com ID {target_organization_id} não encontrada.")
        client.close()
        input("Pressione Enter para voltar ao menu principal...")
        return False
    
    print(f"\nOrganizações encontradas:")
    print(f"Origem: {origin_org.get('name', 'Nome não disponível')} ({origin_organization_id})")
    print(f"Destino: {target_org.get('name', 'Nome não disponível')} ({target_organization_id})")
    
    # Perguntar ao usuário se deseja continuar
    confirmation = input("\nDeseja continuar com a migração? (s/n): ")
    if confirmation.lower() != 's':
        print("Operação cancelada pelo usuário.")
        client.close()
        return False
    
    # Buscar todos os documentos da organização de origem
    documents = list(dataset_collection.find({"organization": origin_organization_id}))
    print(f"Encontrados {len(documents)} datasets para migrar.")
    
    if len(documents) == 0:
        print("Nenhum dataset encontrado para migrar.")
        client.close()
        input("Pressione Enter para voltar ao menu principal...")
        return False
    
    # Inserir novos documentos com novos IDs e evitar duplicação de slug
    new_documents = []
    print("\nCopiando documentos...")
    for doc in tqdm(documents, desc="Progresso", unit="doc"):
        # Criar uma cópia do documento para não modificar o original
        new_doc = doc.copy()
        
        # Gerar novo ID e atualizar a organização
        new_doc["_id"] = ObjectId()
        new_doc["organization"] = target_organization_id
    
        # Verificar se o slug já existe e modificar se necessário
        original_slug = new_doc.get("slug", "")
        new_slug = original_slug
        counter = 1
        
        while dataset_collection.find_one({"slug": new_slug, "_id": {"$ne": new_doc["_id"]}}):
            new_slug = f"{original_slug}-{counter}"
            counter += 1
        
        new_doc["slug"] = new_slug
        new_documents.append(new_doc)
    
    # Inserir os documentos modificados
    if new_documents:
        try:
            dataset_collection.insert_many(new_documents)
            print(f"{len(new_documents)} documentos foram copiados com sucesso.")
        except Exception as e:
            print(f"Erro ao inserir documentos: {e}")
            client.close()
            input("Pressione Enter para voltar ao menu principal...")
            return False
    
    # Perguntar se o usuário quer remover os datasets e a organização de origem
    delete_confirmation = input("\nDeseja remover os datasets da organização de origem? (s/n): ")
    if delete_confirmation.lower() == 's':
        try:
            result = dataset_collection.delete_many({"organization": origin_organization_id})
            print(f"{result.deleted_count} datasets da organização de origem foram removidos.")
            
            delete_org_confirmation = input("Deseja remover a organização de origem também? (s/n): ")
            if delete_org_confirmation.lower() == 's':
                result = organization_collection.delete_one({"_id": origin_organization_id})
                if result.deleted_count > 0:
                    print(f"Organização {origin_organization_id} foi removida com sucesso.")
                else:
                    print(f"Não foi possível remover a organização {origin_organization_id}.")
        except Exception as e:
            print(f"Erro ao remover documentos: {e}")
    
    # Fechar conexão
    client.close()
    print("\nOperação concluída. Conexão com o MongoDB fechada.")
    input("\nPressione Enter para voltar ao menu principal...")
    return True

# Função principal
def main():
    while True:
        mongo_ip = select_environment()
        if mongo_ip:
            migrate_datasets(mongo_ip)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
        sys.exit(0)