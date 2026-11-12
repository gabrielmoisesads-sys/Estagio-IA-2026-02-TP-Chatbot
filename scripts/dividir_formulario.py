#!/usr/bin/env python3
"""Divide as frases HUMANAS (formulário + integrantes) entre TESTE e TREINO.

Entrada: um CSV já ROTULADO pelo grupo (exportado da planilha do Google Forms),
com as colunas:

    texto,intencao[,autor]

* ``intencao``: uma das intenções do grupo.yaml, ``chitchat`` ou ``fora_dominio``
  (linhas com ``intencao`` vazia ou ``descartar`` são ignoradas);
* ``autor`` (opcional): ``grupo`` para frases escritas pelos integrantes; qualquer
  outro valor (ou vazio) = pessoa de fora do grupo.

Regras aplicadas:
1. frases de integrantes do grupo (autor=grupo) vão SEMPRE para o treino;
2. das frases de pessoas de fora, o teste recebe, por classe, a meta abaixo
   (mínimo do enunciado + margem); o que sobrar vai para o treino;
3. duplicatas (após normalização) são removidas; nada do teste fica no treino.

Metas do teste: --por-intencao 20, --chitchat 35, --fora 50  (mínimos: 15/30/40).

Saídas: dados/humano_teste.csv e dados/humano_treino.csv (origem=humano).
Depois rode:  python scripts/montar_treino.py

Uso:  python scripts/dividir_formulario.py dados/formulario_rotulado.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from chatbot.config import carregar_config  # noqa: E402
from chatbot.texto import normalizar  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--config", default="grupo.yaml")
    ap.add_argument("--por-intencao", type=int, default=20)
    ap.add_argument("--chitchat", type=int, default=35)
    ap.add_argument("--fora", type=int, default=50)
    ap.add_argument("--semente", type=int, default=42)
    args = ap.parse_args(argv)

    config = carregar_config(args.config)
    validos = set(config.nomes_intencoes) | {"chitchat", "fora_dominio"}

    df = pd.read_csv(args.entrada, dtype=str, keep_default_na=False)
    df.columns = [c.strip().lower() for c in df.columns]
    if "autor" not in df.columns:
        df["autor"] = ""
    df["texto"] = df["texto"].str.strip()
    df["intencao"] = df["intencao"].str.strip().str.lower()
    df = df[(df["texto"] != "") & (df["intencao"] != "") & (df["intencao"] != "descartar")]
    invalidos = sorted(set(df["intencao"]) - validos)
    if invalidos:
        print(f"[ERRO] rótulos inválidos: {invalidos}. Válidos: {sorted(validos)}")
        return 2
    df = df[~df["texto"].map(normalizar).duplicated()]
    df["origem"] = "humano"

    do_grupo = df[df["autor"].str.strip().str.lower() == "grupo"]
    de_fora = df.drop(do_grupo.index).sample(frac=1, random_state=args.semente)

    meta = {i: args.por_intencao for i in config.nomes_intencoes}
    meta.update({"chitchat": args.chitchat, "fora_dominio": args.fora})
    teste = de_fora.groupby("intencao", group_keys=False).apply(lambda g: g.head(meta[g.name]))
    treino = pd.concat([do_grupo, de_fora.drop(teste.index)])

    cols = ["texto", "intencao", "origem"]
    teste[cols].to_csv(RAIZ / "dados" / "humano_teste.csv", index=False)
    treino[cols].to_csv(RAIZ / "dados" / "humano_treino.csv", index=False)

    contagem = pd.DataFrame({"teste": teste["intencao"].value_counts(),
                             "treino": treino["intencao"].value_counts()}).fillna(0).astype(int)
    contagem["mínimo teste"] = [15 if i in config.nomes_intencoes else (30 if i == "chitchat" else 40)
                                for i in contagem.index]
    print(contagem)
    faltam = contagem[contagem["teste"] < contagem["mínimo teste"]]
    if len(faltam):
        print("\n[AVISO] classes abaixo do mínimo do teste - colete mais frases:")
        print((faltam["mínimo teste"] - faltam["teste"]).rename("faltam").to_string())
    print("\nPróximo passo: python scripts/montar_treino.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
