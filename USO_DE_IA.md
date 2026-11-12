# Declaração de uso de Inteligência Artificial generativa

> **Regra do trabalho:** todo uso de IA generativa precisa estar declarado no artigo
> e no vídeo. Uso não declarado = plágio = nota zero. Este arquivo é atualizado
> **durante** o projeto e copiado para a seção própria do artigo.

## 1. Ferramentas usadas

| Ferramenta (nome e versão/modelo) | Como acessaram | Quem usou |
|---|---|---|
| OpenRouter, modelo `openai/gpt-6-luna` | chave do grupo, via código (`chatbot/llm.py`) | todos |
| Claude Code (Anthropic, modelo Claude Opus 5.5) | aplicativo desktop Claude, aba Code | Gabriel |

## 2. Usos, um por linha

| # | Etapa | O que a IA fez | Prompt (ou resumo + link para o registro) | O que o grupo fez com o resultado |
|---|---|---|---|---|
| 1 | Planejamento | Claude Code leu o enunciado (PDF) e o repositório-base e fez um resumo das tarefas | "faça um resumo de tudo o que deve ser feito de maneira fácil de entender" | Usamos como checklist; conferimos com o enunciado |
| 2 | Domínio | Claude Code sugeriu as 8 intenções e as respostas fixas do `grupo.yaml`, a partir da Resolução 706-COGRAD e da Lei 11.788 | "vamos fazer esse trabalho agora" (sessão de trabalho) | O grupo aprovou a proposta; respostas fixas conferidas com os artigos citados |
| 3 | Documentos | Claude Code localizou e baixou 4 documentos oficiais da UFMS e escreveu 9 resumos `.md` (um por intenção + FAQ) com base neles | idem; fontes em `documentos/FONTES.md` | TODO grupo: conferir cada resumo contra a Resolução 706 e a Lei 11.788 e anotar correções aqui |
| 4 | Dados de treino | `gpt-6-luna` gerou 562 frases das 8 intenções, 100 de fora_dominio e 62 de chitchat (`scripts/gerar_dados_llm.py`) | ver `dados/prompts_llm.md` | Revisão linha a linha; 12 frases descartadas (motivos em `dados/descartadas_llm.txt`) |
| 5 | Dados de treino | `gpt-6-luna` gerou 171 negativos difíceis com temas dos outros grupos (`scripts/gerar_negativos_dificeis.py`, escrito pelo Claude Code) | ver `dados/prompts_llm.md` (seção "negativos difíceis") | Revisão linha a linha; 1 descartada |
| 6 | Código | Claude Code escreveu `scripts/montar_treino.py`, `scripts/dividir_formulario.py`, `scripts/gerar_negativos_dificeis.py`, corrigiu `scripts/baixar_massive.py` (incompatibilidade com pandas novo) e montou o notebook `01_trabalho_grupo.ipynb` com base no exemplo do professor | sessão de trabalho | TODO grupo: ler e entender cada célula; rodar de novo |
| 7 | Chatbot | `gpt-6-luna` redige as respostas das intenções e do chitchat a partir dos trechos dos documentos | prompts em `chatbot/llm.py` + persona do `grupo.yaml` | TODO: registrar ajustes da persona após os testes |

## 3. O que NÃO foi feito com IA

* As frases do **teste** (todas escritas por pessoas, via formulário do grupo).
* As frases de origem `humano` do treino.
* A rotulagem das respostas do formulário.
* TODO grupo: análise dos erros e conclusões do artigo (completar).

## 4. Reflexão (2 a 4 frases)

TODO grupo: onde a IA ajudou (velocidade para gerar dados e código), onde errou
(ex.: frases cortadas, chitchat artificial com perguntas retóricas, resposta vazia
do modelo) e como verificamos (revisão linha a linha, conferência com os
documentos oficiais, validação cruzada e teste humano).
