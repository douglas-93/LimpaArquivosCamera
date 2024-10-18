import hashlib
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Console colors
class Colors:
    W = '\033[0m'  # white (normal)
    R = '\033[31m'  # red
    G = '\033[32m'  # green
    O = '\033[33m'  # orange
    B = '\033[34m'  # blue
    P = '\033[35m'  # purple
    C = '\033[36m'  # cyan
    GR = '\033[37m'  # gray


def calcular_hash(arquivo: Path, algoritmo="MD5") -> str:
    """Calcula o hash do arquivo dado utilizando o algoritmo especificado."""
    hash_alg = hashlib.new(algoritmo)

    with arquivo.open("rb") as f:
        for bloco in iter(lambda: f.read(4096), b""):
            hash_alg.update(bloco)

    return hash_alg.hexdigest()


def contar_arquivos(diretorio: Path) -> int:
    """Conta quantos arquivos existem dentro de um diretório, incluindo subdiretórios."""
    total_arquivos = 0
    print('Verificando quantidade de arquivos ...')

    for arquivos in diretorio.rglob('*'):
        if arquivos.is_file():
            total_arquivos += 1
            print(f'\r{total_arquivos} arquivos encontrados ...', end='')

    print(f'\r{total_arquivos} arquivos encontrados ... [ {Colors.G}OK{Colors.W} ]')
    return total_arquivos


def replica_diretorios(origem: Path, destino: Path):
    """Replica arquivos de um diretório origem para o diretório destino, mantendo a estrutura de diretórios."""
    if not origem.is_dir():
        print(f"{Colors.R}Erro{Colors.W}: O diretório '{origem}' não existe.")
        return

    total_arquivos = contar_arquivos(origem)
    arquivo = 0

    for arquivo_origem in origem.rglob('*'):
        if arquivo_origem.is_file():
            arquivo += 1
            print(f'\rCopiando arquivo {arquivo} de {total_arquivos} ...', end='')
            destino_final = destino / arquivo_origem.relative_to(origem)
            destino_final.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(arquivo_origem, destino_final)

    print(f'\rCopiados {arquivo} de {total_arquivos} arquivos ... [ {Colors.G}OK{Colors.W} ]')


def tempo_do_arquivo_maior_que(arquivo: Path, dias: int = 2) -> bool:
    """Verifica se o tempo de modificação de um arquivo é maior que X dias."""
    data_modificacao = datetime.fromtimestamp(arquivo.stat().st_mtime)
    return data_modificacao < (datetime.now() - timedelta(days=dias))


def limpa_arquivos_copiados(origem: Path, destino: Path):
    """Verifica a integridade dos arquivos copiados e remove os arquivos antigos do diretório de origem."""
    for arquivo_origem in origem.rglob('*'):
        if arquivo_origem.is_file():
            destino_arquivo = destino / arquivo_origem.relative_to(origem)

            print(f'\rVerificando integridade {arquivo_origem.name} ...', end='')

            if destino_arquivo.exists():
                hash_o = calcular_hash(arquivo_origem)
                hash_d = calcular_hash(destino_arquivo)
                integridade = hash_o == hash_d

                if integridade:
                    print(f'\rVerificando integridade {arquivo_origem.name} ... [ {Colors.G}OK{Colors.W} ]')
                    if tempo_do_arquivo_maior_que(arquivo_origem):
                        print(f'Removendo arquivo antigo: {Colors.R}{arquivo_origem.name}{Colors.W}')
                        arquivo_origem.unlink()
                else:
                    print(f'\rVerificando integridade {arquivo_origem.name} ... [ {Colors.R}ERROR{Colors.W} ]')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Faltam parâmetros! Certifique-se de passar os diretórios de origem e destino!')
        print(f'{Colors.R}ABORTANDO ...{Colors.W}')
        sys.exit(-1)

    origem = Path(sys.argv[1])
    destino = Path(sys.argv[2])

    replica_diretorios(origem, destino)
    limpa_arquivos_copiados(origem, destino)

    print(f'{Colors.G}============ Programa finalizado ============{Colors.W}')
