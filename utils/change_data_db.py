from pymongo import MongoClient
from bson import ObjectId
from tqdm import tqdm  # Biblioteca para exibir a barra de progresso

# Configuração do MongoDB
MONGO_URI = "mongodb://10.53.37.52:27017" # PPR
DATABASE_NAME = "udata"

# Conectar ao MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
dataset_collection = db["dataset"]
organization_collection = db["organization"]

# Definição dos ObjectIds (com nomes mais claros)
origin_organization_id = ObjectId("616a16170781900668c0637a")  # ID da organização de origem
target_organization_id = ObjectId("5ae97fa2c8d8c915d5faa3c0")  # ID da organização de destino

# Verificar se as organizações existem
origin_org = organization_collection.find_one({"_id": origin_organization_id})
target_org = organization_collection.find_one({"_id": target_organization_id})

if not origin_org:
    print(f"ERRO: Organização de origem com ID {origin_organization_id} não encontrada.")
    client.close()
    exit(1)

if not target_org:
    print(f"ERRO: Organização de destino com ID {target_organization_id} não encontrada.")
    client.close()
    exit(1)

print(f"Organizações encontradas:")
print(f"Origem: {origin_org.get('name', 'Nome não disponível')} ({origin_organization_id})")
print(f"Destino: {target_org.get('name', 'Nome não disponível')} ({target_organization_id})")

# Perguntar ao usuário se deseja continuar
confirmation = input("Deseja continuar com a migração? (s/n): ")
if confirmation.lower() != 's':
    print("Operação cancelada pelo usuário.")
    client.close()
    exit(0)

# Buscar todos os documentos da organização de origem
documents = list(dataset_collection.find({"organization": origin_organization_id}))
print(f"Encontrados {len(documents)} datasets para migrar.")

# Inserir novos documentos com novos IDs e evitar duplicação de slug
new_documents = []
print("Copiando documentos...")
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
else:
    print("Nenhum documento encontrado para copiar.")

try:
    result = dataset_collection.delete_many({"organization": origin_organization_id})
    print(f"{result.deleted_count} datasets da organização de origem foram removidos.")
    result = organization_collection.delete_one({"_id": origin_organization_id})
    if result.deleted_count > 0:
        print(f"Organização {origin_organization_id} foi removida com sucesso.")
    else:
        print(f"Não foi possível remover a organização {origin_organization_id}.")
except Exception as e:
    print(f"Erro ao remover documentos: {e}")

# Fechar conexão
client.close()
print("Operação concluída. Conexão com o MongoDB fechada.")