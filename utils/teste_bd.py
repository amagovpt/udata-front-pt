from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime  # <--- 1. Importação necessária

# === CONFIGURAÇÃO ===
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "udata"
COLLECTION_NAME = "dataset"

DATASET_ID = ObjectId("67a6e85478959b30d3127cb5")

NOVO_URL = "https://dados.justica.gov.pt/dataset/ef89faf2-c327-4e4b-bb33-fbfca8e4c8c0/resource/e52dce08-035a-4eb5-bd2a-224f8f11e3a1/download/nomesfeminino.csvcsv"
# https://oeirasinterativa.oeiras.pt/dadosabertos/dataset/dc9a39aa-4ba1-4c32-b892-aaafe7925a8e/resource/34c22d9d-6803-480d-844e-b812bad3f236/download/adesao_redeintermunicipalcooperacaodesenvolvimento.pdf

# === LIGAÇÃO AO MONGO ===
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# === UPDATE ===
result = collection.update_one(
    {"_id": DATASET_ID},
    {
        "$set": {
            "resources.0.url": NOVO_URL,
            # 2. Atualizamos as datas explicitamente aqui:
            "resources.0.last_modified_internal": datetime.now(),
        },
        # 2. $unset: Remove o campo específico dentro do recurso
        # "$unset": {"resources.0.last_modified": ""},
    },
)

# === RESULTADO ===
if result.matched_count == 0:
    print("❌ Dataset não encontrado")
elif result.modified_count == 0:
    print("⚠️ Dataset encontrado, mas o valor já era igual")
else:
    print("✅ URL e Datas atualizadas com sucesso")

client.close()
