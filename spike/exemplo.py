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
Path("saida-esperada.txt").write_text("Resultado deterministico da simulacao de decisao arriscada.\n")


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
    for posicao, cliente in enumerate(PACIENTES, start=1):
        roteador.enviar(cliente, random.randint(1, 100) + posicao)    
    print("Parte 1: distribuicao dos pacientes pelas celulas")
    for celula in celulas:
        print(f" celula {celula.nome}: {len(celula.local.dados):2d} pacientes, "
              f"total {sum(celula.local.dados.values())}")

    rede.perder_conexao()
    print("\nFalha declarada na rede. Operacao local das celulas.")
    celulas[1].saudavel = False  # simula falha da celula B
    print("\nFalha declarada nas celulas indisponiveis. Reenvio de um pedido por cliente:")

    for celula in celulas:
        if not celula.saudavel:
            print(f" celula {celula.nome}: fora do ar; pacientes desta celula nao serao atendidos")

    for cliente in PACIENTES[:5]:
        status, nome_celula = roteador.enviar(cliente, random.randint(1, 100))
        print(f" cliente {cliente}; status {status}; celula {nome_celula}")
    
    rede.reconectar()
    print("\nRede reconectada. Sincronizando com sistema legado.")
    celulas[1].saudavel = True  # simula recuperacao da celula B
    for celula in celulas:
        if celula.saudavel:
            for cliente, valor in celula.pendentes:
                try:
                    resultado = sistema_legado.sync(cliente, valor)
                    print(f" {resultado}")
                except RuntimeError as e:
                    print(f" falha ao sincronizar {cliente}: {e}")
# Parte 2: uma unica celula. Os oito nos abaixo pertencem a celula A e nao sao
# compartilhados com outras celulas: shuffle sharding vale dentro da celula.
CONTAS_DA_CELULA_A = [f"conta-{i:02d}" for i in range(1, 25)]
NOS_DA_CELULA_A = list(range(8))
PARES_EMBARALHADOS = list(combinations(NOS_DA_CELULA_A, 2))
PARES_FIXOS = [(0, 1), (2, 3), (4, 5), (6, 7)]
def sorteio_embaralhado(conta: str) -> tuple[int, int]:
    """Shuffle sharding: cada conta recebe um dos 28 pares possiveis de nos da
    celula."""
    return PARES_EMBARALHADOS[impressao(conta) % len(PARES_EMBARALHADOS)]

def sorteio_fixo(conta: str) -> tuple[int, int]:
    """Particao classica: quatro grupos fixos de dois nos."""
    return PARES_FIXOS[impressao(conta) % len(PARES_FIXOS)]

def derrubados(sorteio, caidos: set[int]) -> list[str]:
    """Contas sem nenhum no: '<=' testa se o par atribuido esta contido nos nos
    caidos."""
    return [c for c in CONTAS_DA_CELULA_A if set(sorteio(c)) <= caidos]

def cenario(caidos: set[int]) -> None:
    print(f" nos fora do ar: {sorted(caidos)}")
    for rotulo, sorteio in (("particao fixa ", sorteio_fixo), ("shuffle sharding ", sorteio_embaralhado)):
        perdidos = derrubados(sorteio, caidos)
        parciais = [c for c in CONTAS_DA_CELULA_A if set(sorteio(c)) & caidos and c not in perdidos]
        print(f" {rotulo}: {len(perdidos)} conta(s) sem nenhum no, " 
              f"{len(parciais)} com capacidade reduzida")
        
def parte_2() -> None:
    print("\nParte 2: shuffle sharding dentro da celula A, 8 nos e 2 nos por conta")
    print(f" combinacoes possiveis: {len(PARES_EMBARALHADOS)} pares (particao fixa oferece "f"{len(PARES_FIXOS)})")
    print("cenario 1, pior caso da particao fixa: os dois nos caidos formam um grupo fixo")
    cenario({0, 1})
    print(" cenario 2: os dois nos caidos estao em grupos fixos diferentes")
    cenario({0, 2})
    print(" amostra de atribuicao embaralhada:")
    for conta in CONTAS_DA_CELULA_A[:4]:
        print(f" {conta}: nos {list(sorteio_embaralhado(conta))}")
        
if __name__ == "__main__":
    parte_1()
    parte_2()