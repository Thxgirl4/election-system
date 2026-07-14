import hashlib


def gerar_hash_id(voto_id):
    hash_obj = hashlib.sha256(voto_id.encode('utf-8'))
    return hash_obj.hexdigest()[:100] 