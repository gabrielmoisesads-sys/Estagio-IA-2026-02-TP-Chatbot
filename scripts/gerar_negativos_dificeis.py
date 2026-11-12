#!/usr/bin/env python3
"""Gera NEGATIVOS DIFÍCEIS (fora_dominio) para o bot de Estágio com o LLM.

A avaliação do professor usa frases dos temas dos OUTROS grupos como fora_dominio.
Este script pede ao LLM perguntas de cada um desses temas vizinhos, de preferência
usando palavras que também aparecem no tema Estágio (bolsa, termo, seguro, carga
horária, relatório, orientador, convênio, auxílio...).

Uso:  python scripts/gerar_negativos_dificeis.py --n 12

Saída: acrescenta em dados/gerados_llm.csv (origem=llm) e registra os prompts em
dados/prompts_llm.md. Revise as frases antes de usar no treino.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from chatbot.config import carregar_config  # noqa: E402
from chatbot.geracao import _limpar_linhas  # noqa: E402
from chatbot.llm import ClienteLLM, ErroLLM  # noqa: E402

TEMAS_VIZINHOS = {
    "Secretaria acadêmica": "matrícula, rematrícula, trancamento, histórico, declarações, aproveitamento de disciplinas, colação de grau",
    "Restaurante universitário": "cardápio, horários, valores e isenção, recarga de créditos, cadastro no RU",
    "Assistência estudantil": "auxílio permanência, auxílio alimentação, auxílio moradia, editais, documentação, pagamentos, recursos",
    "Trabalho de Conclusão de Curso": "escolha de orientador de TCC, prazos, formatação e normas, banca, depósito da versão final",
    "Iniciação científica e monitoria": "editais, bolsas e valores, inscrição, relatórios, certificados",
    "Atividades complementares e extensão": "cômputo de horas, validação, certificados, curricularização da extensão",
    "Mobilidade e intercâmbio": "editais, proficiência em idiomas, equivalência de disciplinas, documentação, auxílio financeiro",
    "TI do estudante": "e-mail institucional, Wi-Fi, senha do sistema acadêmico, AVA/Moodle, licenças de software",
    "Calendário e avaliações": "datas de provas, prova substitutiva, revisão de nota, frequência mínima, recessos",
    "Transporte e acesso ao campus": "linhas de ônibus, passe estudantil, estacionamento, bicicletário, acessibilidade",
    "Esporte e lazer no campus": "reserva de quadras, atléticas, academia universitária, eventos esportivos",
    "Biblioteca universitária": "empréstimo, renovação, multas, horários, salas de estudo, bases digitais",
}


def prompt(tema: str, assuntos: str, n: int) -> str:
    return (
        f"Gere {n} mensagens DIFERENTES que um estudante universitário brasileiro enviaria ao "
        f"chatbot do setor \"{tema}\" da universidade, sobre: {assuntos}.\n"
        "Pelo menos metade deve usar palavras que também aparecem em dúvidas sobre ESTÁGIO "
        "(bolsa, valor, termo, seguro, carga horária, horas, relatório, orientador, convênio, "
        "auxílio, prazo, documentos, assinatura), mas o assunto NÃO pode ser estágio.\n"
        "Misture estilos: perguntas completas, mensagens informais de WhatsApp sem acento, "
        "com erros de digitação e mensagens bem curtas.\n"
        "Não numere, não use aspas, não explique: uma mensagem por linha."
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="grupo.yaml")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--saida", default="dados/gerados_llm.csv")
    args = ap.parse_args(argv)

    config = carregar_config(args.config)
    cliente = ClienteLLM.da_config(config)
    linhas, log = [], []
    for tema, assuntos in TEMAS_VIZINHOS.items():
        p = prompt(tema, assuntos, args.n)
        resp = ""
        for _tentativa in range(3):          # o modelo às vezes devolve resposta vazia
            try:
                resp = cliente.conversar([{"role": "user", "content": p}], temperatura=0.9,
                                         max_tokens=60 * args.n)
                break
            except ErroLLM as e:
                print(f"  (tentando de novo: {e})")
        frases = _limpar_linhas(resp)
        linhas += [{"texto": f, "intencao": "fora_dominio", "origem": "llm"} for f in frases]
        log.append((tema, p, len(frases)))
        print(f"  {tema:40s} | {len(frases):3d} frases")

    novos = pd.DataFrame(linhas, columns=["texto", "intencao", "origem"])
    saida = config.pasta / args.saida
    if saida.exists():
        novos = pd.concat([pd.read_csv(saida, dtype=str, keep_default_na=False), novos], ignore_index=True)
    novos = novos[~novos["texto"].str.lower().duplicated()]
    novos.to_csv(saida, index=False)

    with open(config.pasta / "dados" / "prompts_llm.md", "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.now():%d/%m/%Y %H:%M} - modelo `{cliente.modelo}` - "
                "negativos difíceis (scripts/gerar_negativos_dificeis.py)\n")
        for tema, p, n in log:
            f.write(f"\n### `fora_dominio` ({tema}) - {n} frases\n\n```text\n{p}\n```\n")
    print(f"\n{len(novos)} frases em {saida} (uso: {cliente.uso})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
