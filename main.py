import hashlib
import os
import shutil
import sys
from datetime import datetime, timedelta

# Console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray


def calcular_hash(arquivo, algoritmo="MD5"):
    hash_alg = hashlib.new(algoritmo)

    with open(arquivo, "rb") as f:
        while True:
            bloco = f.read(4096)
            if not bloco:
                break
            hash_alg.update(bloco)

    return hash_alg.hexdigest()


def contar_arquivos(diretorio):
    total_arquivos = 0

    print('Verificando quantidade de arquivos ...')
    # Percorre o diretório e seus subdiretórios
    for _, _, arquivos in os.walk(diretorio):
        total_arquivos += len(arquivos)  # Conta a quantidade de arquivos
        print(f'\r{total_arquivos} arquivos encontrados ...', end='')
    print(f'\r{total_arquivos} arquivos encontrados ... [ {G}OK{W} ]')

    return total_arquivos


def replica_diretorios(origem, destino):
    # Verifica se o diretório existe
    if not os.path.isdir(origem):
        print(f"{R}Erro{W}: O diretório '{origem}' não existe.")
        return

    total_arquivos = contar_arquivos(origem)
    arquivo = 0

    for raiz, diretorios, arquivos in os.walk(origem):
        for nome_arquivo in arquivos:
            arquivo += 1
            print(f'\rCopiando arquivo {arquivo} de {total_arquivos} ...', end='')
            sulfixo = raiz.split(origem)[1]
            caminho_final = f'{destino}{sulfixo}'
            os.makedirs(caminho_final, exist_ok=True)
            origem_arquivo = os.path.join(raiz, nome_arquivo)
            destino_arquivo = os.path.join(caminho_final, nome_arquivo)
            shutil.copy(origem_arquivo, destino_arquivo)

    print(f'\rCopiados {arquivo} de {total_arquivos} arquivos ... [ {G}OK{W} ]')


def tempo_do_arquivo_maior_que(caminho_arquivo, dias=2):
    # Obtém o tempo de modificação do arquivo
    tempo_modificacao = os.path.getmtime(caminho_arquivo)
    # Converte o tempo de modificação
    data_modificacao = datetime.fromtimestamp(tempo_modificacao)
    # Pega a data de X dias atrás
    dois_dias_atras = datetime.now() - timedelta(days=dias)

    # Verifica se o arquivo foi modificado há mais de X dias
    return data_modificacao < dois_dias_atras


def limpa_arquivos_copiados(origem, destino):
    for raiz, diretorios, arquivos in os.walk(origem):
        for nome_arquivo in arquivos:
            sulfixo = raiz.split(origem)[1]
            caminho_final = f'{destino}{sulfixo}'

            origem_arquivo = os.path.join(raiz, nome_arquivo)
            destino_arquivo = os.path.join(caminho_final, nome_arquivo)

            print(f'\rVerificando integridade {nome_arquivo} ...', end='')

            hash_o = calcular_hash(origem_arquivo)
            hash_d = calcular_hash(destino_arquivo)

            integridade = hash_o == hash_d

            if integridade:
                print(f'\rVerificando integridade {nome_arquivo} ... [ {G}OK{W} ]')
            else:
                print(f'\rVerificando integridade {nome_arquivo} ... [ {R}ERROR{W} ]')

            if integridade and tempo_do_arquivo_maior_que(origem_arquivo):
                print(f'Removendo arquivo antigo: {R}{nome_arquivo}{W}')
                os.remove(origem_arquivo)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Faltam parâmetros! Certifique-se de passar os diretórios de origem e destino!')
        print(f'{R}ABORTANDO ...{W}')
        exit(-1)

    origem = sys.argv[1]
    destino = sys.argv[2]

    replica_diretorios(origem, destino)
    limpa_arquivos_copiados(origem, destino)

    print(f'{G}============ Programa finalizado ============{W}')
