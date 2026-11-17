"""
    Arquivo: Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores.
    Data: 10/11/2026
    Autor: Leonardo Scotti
    Versão: 1.0.11.2026
"""
import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import LIMITE_MEDIA, confianca

CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "sessao", "nota_facilidade"]

MSG_DADO_PESSOAL = "Atenção: não digite CPF, telefone ou e-mail. Reescreva."


def tem_dado_pessoal(texto):
    digitos = 0
    for c in texto:
        if c.isdigit():
            digitos += 1
    return digitos >= 8 or "@" in texto


def tem_letra(texto):
    for c in texto:
        if c.isalpha():
            return True
    return False


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historico = []
        self._carregar_historico()

    # ========== entrada de dados =========
    def _ler_opcao(self, minimo, maximo):
        while True:
            texto = input("Escolha uma opção: ").strip()
            if not texto.isdigit():
                print("Opção inválida. Digite apenas o número.")
                continue
            numero = int(texto)
            if numero < minimo or numero > maximo:
                print(f"Opção inválida. Escolha entre {minimo} e {maximo}.")
                continue
            return numero

    def _pedir_sn(self, pergunta):
        while True:
            resposta = input(f"\n{pergunta} (s/n): ").strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Resposta inválida. Digite s para sim ou n para não.")

    # ========== histórico ==========
    def _carregar_historico(self):
        if not os.path.exists(self.caminho_historico):
            return
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, list):
                raise ValueError("histórico não é uma lista")
            self.historico = [d for d in dados if isinstance(d, dict)]
        except (json.JSONDecodeError, ValueError, OSError):
            print("[Aviso] Histórico ilegível. Um novo histórico será iniciado.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".bak")
            except OSError:
                pass
            self.historico = []

    def _salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"[Aviso] Não foi possível salvar o histórico: {erro}")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):

        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "sessao": self.sessao,
            "nota_facilidade": None,
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    # =========== atendimento por pergunta ==========
    def perguntar(self):
        while self._atender_pergunta():
            pass

    def _atender_pergunta(self):

        inicio = time.time()
        tentativas = 0
        encontrou = False
        id_orientacao = None
        ultima = ""
        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                if tentativas > 0:
                    self.registrar("pergunta", ultima, id_orientacao, encontrou,
                                   False, tentativas, round(time.time() - inicio, 1))
                return False
            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if tem_dado_pessoal(texto):
                print(MSG_DADO_PESSOAL)
                continue
            if not tem_letra(texto):
                print("Escreva sua dúvida com palavras, por favor.")
                continue

            tentativas += 1
            ultima = texto
            resultados = self.base.buscar(texto)

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                encontrou, id_orientacao = False, None
                self._mostrar_nao_encontrei()
                continue

            encontrou = True
            pontos, melhor = resultados[0]
            id_orientacao = melhor.id
            print(f"\nConfiança da resposta: {confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()
            alternativas = [(p, o) for p, o in resultados[1:3] if p >= LIMITE_MEDIA]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} [{o.categoria}] ({p} pontos)")

            if self._pedir_sn("Essa orientação respondeu sua dúvida?"):
                self.registrar("pergunta", texto, melhor.id, True, True,
                               tentativas, round(time.time() - inicio, 1))
                return True
            print("Que pena. Tente escrever de outro jeito ou use a navegação por categorias.")

    def _mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente usar outras palavras, por exemplo: bilhete único, metrô, trem,")
        print("ônibus gratuito, passagem entre estados. Ou use as categorias:")
        for c in self.base.categorias():
            print(f"  - {c}")

    # ========== navegação por categorias ==========
    def navegar(self):
        categorias = self.base.categorias()
        while True:
            print("\n=== Categorias ===")
            for i, categoria in enumerate(categorias, start=1):
                print(f"  {i}. {categoria}")
            print("  0. Voltar")
            opcao = self._ler_opcao(0, len(categorias))
            if opcao == 0:
                return
            self._navegar_categoria(categorias[opcao - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n=== {categoria} ===")
            for i, o in enumerate(orientacoes, start=1):
                print(f"  {i}. {o.titulo}")
            print("  0. Voltar")
            inicio = time.time()
            opcao = self._ler_opcao(0, len(orientacoes))
            if opcao == 0:
                return
            escolhida = orientacoes[opcao - 1]
            escolhida.exibir()
            ajudou = self._pedir_sn("Essa orientação respondeu sua dúvida?")
            self.registrar("categoria", f"{categoria} > {escolhida.titulo}",
                           escolhida.id, True, ajudou, 1,
                           round(time.time() - inicio, 1))

    # ========== indicadores ==========
    def indicadores(self):

        total = len(self.historico)
        if total == 0:
            return {"total": 0}
        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo_segundos", 0) for a in encontrados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]

        notas = {}
        for a in self.historico:
            if a.get("nota_facilidade") is not None:
                notas[a.get("sessao")] = a["nota_facilidade"]

        sem_solucao = []
        for a in self.historico:
            if not a.get("ajudou") and a.get("pergunta") not in sem_solucao:
                sem_solucao.append(a.get("pergunta"))

        return {
            "total": total,
            "encontrada_pct": round(len(encontrados) / total * 100, 1),
            "acerto_pct": round(len(ajudaram) / total * 100, 1),
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else 0,
            "tentativas_media": round(sum(tentativas) / total, 1),
            "facilidade": round(sum(notas.values()) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        ind = self.indicadores()
        print("\n=== Indicadores ===")
        if ind["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return
        print(f"Atendimentos registrados:      {ind['total']}")
        print(f"Resposta encontrada (%):       {ind['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%):    {ind['acerto_pct']}")
        print(f"Tempo médio para encontrar:    {ind['tempo_medio']} s")
        print(f"Tentativas por atendimento:    {ind['tentativas_media']}")
        facilidade = ind["facilidade"] if ind["facilidade"] is not None else "sem notas ainda"
        print(f"Facilidade de uso (1 a 5):     {facilidade}")
        print("Dúvidas sem solução:")
        if ind["sem_solucao"]:
            for d in ind["sem_solucao"]:
                print(f"  - {d}")
        else:
            print("  (nenhuma)")

    # ========== exportação ==========
    def exportar_csv(self):

        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore", restval="")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"Atendimentos exportados para {self.caminho_csv}")
            return True
        except OSError as erro:
            print(f"[Aviso] Não foi possível exportar o CSV: {erro}")
            return False

    # ========== encerramento ==========
    def encerrar(self):

        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if da_sessao:
            print("\nQuanto foi fácil usar este assistente? 1 = muito difícil, 5 = muito fácil.")
            nota = self._ler_opcao(1, 5)
            for a in da_sessao:
                a["nota_facilidade"] = nota
            self._salvar_historico()
        self.exportar_csv()
        self.mostrar_indicadores()
        print("\nObrigado por usar o Citizen Assist AI. Até logo!")
