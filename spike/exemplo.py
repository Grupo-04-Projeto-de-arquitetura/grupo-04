'''
O QUE ENTREGAR

    Um programa em Python que prova que a decisão mais arriscada do projeto funciona. O README diz qual ADR ele prova.
    Entre 100 e 300 linhas, só biblioteca padrão do Python 3.12, roda com python3 exemplo.py e imprime resultado determinístico, registrado em saida-esperada.txt.
    Simula o que for externo (rede, banco, sistema legado) com o mínimo necessário para o mecanismo aparecer.
    README de meia página: o que prova, como rodar, o que aconteceria se a decisão estivesse errada.
    
    ADR provada: "0002 -  Utilização de arquitetura baseada em cédulas."
    
    fonte do codigo: seção 4 do capitulo de arquitetura baseada em cedulas(so pra n esquecer de colocar dps)
    
    Alterações a serem feitas: Simular rede, banco de dados e sistema legado com o mínimo necessário para o mecanismo aparecer.

'''
from pathlib import Path
import hashlib
import random
from itertools import combinations

file1 = open("saida-esperada.txt", "w")

PACIENTES = [f"cliente-{i:02d}" for i in range(1, 25)]
def impressao(chave: str) -> int:
    """Hash estavel entre execucoes (hash() embutido usa semente aleatoria por
    processo)."""
    return int.from_bytes(hashlib.blake2b(chave.encode("utf-8"),
    digest_size=8).digest(), "big")
    
class Celula:
    """Instancia completa e isolada do sistema: aplicacao mais os proprios
    dados."""

    def __init__(self, nome: str) -> None:
        self.nome = nome
        self.registros_locais = Local()
        self.saudavel = True
        self.pendentes = []
    def processar(self, cliente: str, valor: int) -> int:
        if not self.saudavel:
            self.pendentes.append((cliente, valor))
            raise RuntimeError(f"celula {self.nome} indisponivel")
        dados_atuais_celula = self.registros_locais.ler(cliente)
        novos_dados = dados_atuais_celula + valor
        self.registros_locais.armazenar(cliente, novos_dados)
        return novos_dados
    def sync(self, sistema_legado: "Legado") -> None:
        '''Sincroniza os dados locais da celula com o sistema legado.'''
        while self.pendentes:
            cliente, valor = self.pendentes.pop(0)
            try:
                resultado = sistema_legado.sync(cliente, valor)
                print(f" {resultado}")
            except RuntimeError:
                self.pendentes.insert(0, (cliente, valor))
                break
        

class Local:
    """Simula o banco de dados local da celula, que nao e compartilhado com
    outras celulas."""
    
    def __init__(self):
        self.registros = {}
        
    def armazenar(self, chave: str, valor: int) -> None:
        self.registros[chave] = valor
        
    def ler(self, chave: str) -> int:
        return self.registros.get(chave, 0)

class Roteador:
    """Camada mais fina possivel: escolhe a celula pela chave de particao e
    nada mais."""
    
    def __init__(self, celulas: list[Celula]) -> None:
        self.celulas = celulas
        
    def celula_de(self, cliente: str) -> Celula:
        return self.celulas[impressao(cliente) % len(self.celulas)]

    def enviar(self, cliente: str, evento: int) -> tuple[str, str]: #retorna tupla com status e nome da celula
        celula = self.celula_de(cliente)
        try:
            celula.processar(cliente, evento) #evento pode ser registro, atendimento, etc
            return ("ok", celula.nome)
        except RuntimeError:
            return ("falha", celula.nome)

class Rede: 
    '''Simula a rede, podendo apresentar falhas.'''
    def __init__(self):
        self.disponivel = True
    
    def perder_conexao(self):
        self.disponivel = False
        
    def reconectar(self):
        self.disponivel = True

class Legado:
    '''Simula um sistema legado, podendo apresentar falhas.'''
    def __init__(self):
        self.disponivel = True
        self.dados = []
    
    def falhar(self):
        self.disponivel = False
        
    def recuperar(self):
        self.disponivel = True
        
    def sync(self, cliente: str, valor: int) -> str:
        if not self.disponivel:
            raise RuntimeError("sistema legado fora do ar")
        self.dados.append((cliente, valor))
        return f"sincronizado {cliente} com valor {valor}"
    
def parte_1() -> None:
    '''
    parte 1:
    1. distribui os pacientes pelas celulas
    2. simula a falha de uma celula, mostrando o impacto na base de pacientes
    '''
    celulas = [Celula(nome) for nome in ("A", "B", "C", "D")]
    roteador = Roteador(celulas)
    rede = Rede()
    sistema_legado = Legado()
    
    
    print("Parte 1: distribuicao inicial dos pacientes pelas celulas")
    file1.write("Parte 1: distribuicao inicial dos pacientes pelas celulas.\n")
    for posicao, cliente in enumerate(PACIENTES, start=1):
        roteador.enviar(cliente, random.randint(1, 100) + posicao)
    
    for celula in celulas:
        print(f" celula {celula.nome}: {len(celula.registros_locais.registros):2d} pacientes, "
              f"total {sum(celula.registros_locais.registros.values())}")

    rede.perder_conexao()
    print("\nFalha declarada na rede. Operacao local das celulas.")
    file1.write("\nFalha declarada na rede. Operacao local das celulas.\n")
    celulas[1].saudavel = False  # simula falha da celula B
    print(f"\n celula {celulas[1].nome}: fora do ar; raio de impacto isolado.")
    file1.write(f"\n celula {celulas[1].nome}: fora do ar; raio de impacto isolado.\n")

    for cliente in PACIENTES[:5]:
        status, nome_celula = roteador.enviar(cliente, random.randint(1, 100))
        file1.write(f" cliente {cliente}; status {status}; celula {nome_celula}\n")
        print(f" cliente {cliente}; status {status}; celula {nome_celula}")

    print("\nDados locais ficam pendentes enquanto a rede nao volta.")
    file1.write("\nDados locais ficam pendentes enquanto a rede nao volta.\n")
    for celula in celulas:
        if not celula.saudavel:
            print(f" celula {celula.nome} acumulou {len(celula.pendentes)} eventos pendentes")
            file1.write(f" celula {celula.nome} acumulou {len(celula.pendentes)} eventos pendentes\n")
    
    rede.reconectar()
    print("\nRede reconectada. Sincronizando com sistema legado.")
    file1.write("\nRede reconectada. Sincronizando com sistema legado.\n")
    sistema_legado.recuperar()
    
    celulas[1].saudavel = True  # simula recuperacao da celula B
    for celula in celulas:
        if celula.saudavel:
            celula.sync(sistema_legado)
            celula.pendentes.clear()  # limpa pendentes apos sincronizacao bem-sucedida
    
    
    for celula in celulas:
        print(f" celula {celula.nome}: {len(celula.registros_locais.registros):2d} pacientes, "
              f"total {sum(celula.registros_locais.registros.values())}")
        print(f" celula {celula.nome}: {len(celula.pendentes)} eventos pendentes apos sincronizacao")
        file1.write(f" celula {celula.nome}: {len(celula.registros_locais.registros):2d} pacientes, "
           f"total {sum(celula.registros_locais.registros.values())}\n")
        file1.write(f" celula {celula.nome}: {len(celula.pendentes)} eventos pendentes apos sincronizacao\n")
    print("\nSincronizacao finalizada.")
    file1.write("\nSincronizacao finalizada.\n")
        
if __name__ == "__main__":
    parte_1()