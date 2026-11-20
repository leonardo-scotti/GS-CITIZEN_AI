import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c", "ü": "u"}

PESO_PALAVRA_CHAVE = 3
PESO_TITULO = 1
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

IGNORAR = ["como", "para", "onde", "qual", "quais", "quem", "pode", "preciso",
           "quero", "tenho", "fazer", "faco", "esse", "essa", "isso", "minha"]


def normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/%\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def confianca(pontos: int) -> str:
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return "BAIXA"


def registro_valido(o: Orientacao) -> bool:
    if not isinstance(o.id, int):
        return False
    for campo in [o.categoria, o.titulo, o.resposta, o.onde, o.fonte, o.verificado_em]:
        if not isinstance(campo, str) or campo.strip() == "":
            return False
    for lista in [o.palavras_chave, o.documentos]:
        if not isinstance(lista, list):
            return False
        for item in lista:
            if not isinstance(item, str):
                return False
    return len(o.palavras_chave) > 0


def pontos_da_tupla(tupla):
    return tupla[0]


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self) -> bool:
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"[Erro] Arquivo da base de conhecimento não encontrado: {self.caminho}")
            return False
        except json.JSONDecodeError:
            print(f"[Erro] O arquivo {self.caminho} está corrompido (JSON inválido).")
            return False

        if not isinstance(dados, list):
            print("[Erro] A base de conhecimento deve ser uma lista de orientações.")
            return False

        ignoradas = 0
        for item in dados:
            try:
                orientacao = Orientacao(**item)
            except TypeError:
                ignoradas += 1
                continue
            if registro_valido(orientacao):
                self.orientacoes.append(orientacao)
            else:
                ignoradas += 1

        if ignoradas > 0:
            print(f"[Aviso] {ignoradas} registro(s) inválido(s) foram ignorados.")
        if not self.orientacoes:
            print("[Erro] Nenhuma orientação válida foi carregada.")
            return False
        return True

    def categorias(self) -> list:
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria: str) -> list:
        lista = []
        for o in self.orientacoes:
            if o.categoria == categoria:
                lista.append(o)
        return lista

    def pontuar(self, pergunta: str, orientacao: Orientacao) -> int:
        texto = normalizar(pergunta)
        pontos = 0
        for chave in orientacao.palavras_chave:
            if normalizar(chave) in texto:
                pontos += PESO_PALAVRA_CHAVE

        titulo = normalizar(orientacao.titulo)
        ja_contadas = []
        for palavra in texto.split():
            if len(palavra) >= 4 and palavra not in IGNORAR and palavra not in ja_contadas:
                ja_contadas.append(palavra)
                if " " + palavra + " " in titulo:
                    pontos += PESO_TITULO
        return pontos

    def buscar(self, pergunta: str) -> list:
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, o))
        resultados.sort(key=pontos_da_tupla, reverse=True)
        return resultados
