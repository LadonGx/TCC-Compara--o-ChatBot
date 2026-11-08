#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
 DIA 1 - COLETA DO CHATBOT A (SEM SEGURANCA)
 TCC 2026 - UNISAL Americana
===========================================================================

POR QUE UM DIA POR CHATBOT
    Rodar todas as chamadas do mesmo chatbot em sequencia mantem o prefixo
    do prompt identico de uma chamada para a outra, o que maximiza o
    acerto do cache de prompt da Groq. Tokens em cache nao contam para os
    limites de taxa, e o prompt de sistema do Chatbot A sozinho tem cerca
    de 3.000 tokens. Intercalar os dois chatbots, como no teste anterior,
    trocava o prefixo a cada chamada e desperdicava o cache.

    O cache NAO altera a resposta: ele reaproveita o processamento do
    prefixo, nao o conteudo de conversas anteriores. Nao ha risco de
    contaminacao entre testes - esse papel cabe ao sessionId, que o
    script ja renova a cada chamada.

ANTES DE RODAR
    - Base reduzida aos 100 registros, igual nos dois chatbots
    - Nome, sobrenome e e-mail sincronizados entre o prompt e a BaseRH
    - Flowise no ar na porta 3000

USO
    pip install requests
    python rodar_chatbot_a.py --ping         # so testa a conexao
    python rodar_chatbot_a.py                # coleta (retoma sozinho)
    python rodar_chatbot_a.py --orcamento 120000
===========================================================================
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experimento_core as core

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CHATFLOW_ID = "fdc388b6-8089-4a4b-b5a2-37cfc170821a"
NOME = "A_sem_seguranca"
ARQ_SAIDA = "resultados_chatbot_A.csv"
ARQ_LOG = "log_chatbot_A.txt"

# O prompt de sistema do Chatbot A carrega os 100 registros em texto.
TOKENS_SISTEMA = 3100


def ping():
    print("=" * 76)
    print(" CONECTIVIDADE - CHATBOT A")
    print("=" * 76)
    print(f" Host     : {core.HOST}")
    print(f" Chatflow : {CHATFLOW_ID}")
    try:
        import requests
        r = requests.get(core.HOST, timeout=15)
        print(f" [+] Flowise respondeu (HTTP {r.status_code})")
    except Exception as e:
        print(f" [X] Flowise inacessivel: {type(e).__name__}")
        return False
    try:
        d = core.consultar(CHATFLOW_ID,
                           "Quantos funcionários estão com status Active?")
    except core.LimiteDiarioAtingido as e:
        print(f" [X] {e}")
        return False
    if d["erro"]:
        print(f" [X] {d['erro']}")
        return False
    bate = any(abs(n - 44) < 0.5 for n in core.numeros(d["resposta"]))
    print(f" [{'+' if bate else '!'}] {d['latencia_s']}s | campo "
          f"'{d['campo_resposta']}' | gabarito 44 "
          f"{'confere' if bate else 'NAO CONFERE'}")
    print(f"     {d['resposta'][:180]}")
    if not bate:
        print("     >>> A base pode nao estar reduzida aos 100 registros.")
    print()
    return True


def main():
    ap = argparse.ArgumentParser(description="Coleta do Chatbot A (dia 1)")
    ap.add_argument("--ping", action="store_true")
    ap.add_argument("--orcamento", type=int, default=core.ORCAMENTO_PADRAO,
                    help="teto de tokens para esta sessao")
    ap.add_argument("--recomecar", action="store_true",
                    help="ignora o que ja foi coletado")
    a = ap.parse_args()

    if a.ping:
        ping()
        return
    if not ping():
        print("[X] Corrija a conexao antes de prosseguir.")
        return

    ex = core.Execucao(NOME, CHATFLOW_ID, ARQ_SAIDA, ARQ_LOG,
                       TOKENS_SISTEMA, a.orcamento)
    ex.rodar(retomar=not a.recomecar)


if __name__ == "__main__":
    main()
