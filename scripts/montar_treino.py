#!/usr/bin/env python3
"""Monta dados/treino.csv (e dados/teste.csv) a partir das fontes do grupo.

Fontes do TREINO:
  1. dados/gerados_llm.csv      - frases do LLM, MENOS as de dados/descartadas_llm.txt
                                  (revisão manual linha a linha)
  2. dados/geral/massive_*.csv  - amostra da base MASSIVE (negativos fáceis)
  3. dados/humano_treino.csv    - frases escritas por pessoas (formulário / grupo),
                                  origem humano ou coletado
Fonte do TESTE:
  4. dados/humano_teste.csv     - frases escritas por pessoas, NUNCA usadas no treino

Se humano_treino.csv / humano_teste.csv não existirem, são ignorados. O script
remove do treino qualquer frase que esteja no teste (sem vazamento).

Uso:  python scripts/montar_treino.py [--chitchat-massive 120] [--fora-massive 250]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from chatbot.texto import normalizar  # noqa: E402

D = RAIZ / "dados"
COLS = ["texto", "intencao", "origem"]


def ler(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame(columns=COLS)
    df = pd.read_csv(caminho, dtype=str, keep_default_na=False)
    df["texto"] = df["texto"].str.strip()
    return df[df["texto"] != ""][COLS]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chitchat-massive", type=int, default=120)
    ap.add_argument("--fora-massive", type=int, default=250)
    ap.add_argument("--semente", type=int, default=42)
    args = ap.parse_args(argv)

    llm = ler(D / "gerados_llm.csv")
    descartar = {l.strip() for l in (D / "descartadas_llm.txt").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")}
    llm = llm[~llm["texto"].isin(descartar)]

    partes = [llm]
    for nome, n in (("massive_chitchat.csv", args.chitchat_massive),
                    ("massive_fora_dominio.csv", args.fora_massive)):
        m = ler(D / "geral" / nome)
        if len(m):
            partes.append(m.sample(n=min(n, len(m)), random_state=args.semente))
    partes.append(ler(D / "humano_treino.csv"))

    treino = pd.concat(partes, ignore_index=True)
    teste = ler(D / "humano_teste.csv")

    chave = treino["texto"].map(normalizar)
    treino = treino[~chave.duplicated()]
    if len(teste):
        teste = teste[~teste["texto"].map(normalizar).duplicated()]
        no_teste = set(teste["texto"].map(normalizar))
        antes = len(treino)
        treino = treino[~treino["texto"].map(normalizar).isin(no_teste)]
        print(f"removidas do treino por estarem no teste: {antes - len(treino)}")
        teste.to_csv(D / "teste.csv", index=False)
        print(f"teste.csv: {len(teste)} frases")

    treino = treino.sample(frac=1, random_state=args.semente).reset_index(drop=True)
    treino.to_csv(D / "treino.csv", index=False)
    print(f"treino.csv: {len(treino)} frases\n")
    print(pd.crosstab(treino["intencao"], treino["origem"], margins=True))
    humano = treino["origem"].isin(["humano", "coletado"]).mean()
    print(f"\nfração humano/coletado no treino: {humano:.1%} (mínimo exigido: 20%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
