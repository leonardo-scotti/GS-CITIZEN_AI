# Citizen Assist AI

Assistente de terminal que orienta **pessoas idosas** sobre **transporte público** (ônibus urbano, trens/metrô e ônibus rodoviário entre cidades e estados), usando apenas uma base de conhecimento verificada, sem coletar dados pessoais.

## Integrantes
| Nome | RM |
|------|----|
| Leonardo Scotti Tobias | 573305 |
| Henrique de Souza Aragão | 570529 |
| Natan Silva da Costa | 573100 |

## Público e problema
Idosos da Grande São Paulo têm dúvidas sobre gratuidade, Bilhete Único, documentos, passagens entre estados e onde reclamar. A informação está espalhada e há sites falsos. O assistente reúne respostas em linguagem simples, com fonte e data de verificação.

## ODS relacionados
ODS 3 (Saúde e Bem-Estar), ODS 10 (Redução das Desigualdades), ODS 11 (Cidades e Comunidades Sustentáveis).

## Como executar
```bash
python main.py
```
Requer Python 3.8+ e nenhuma biblioteca externa.

## Estrutura
```
main.py  orientacao.py  base_conhecimento.py  assistente.py
data/base_conhecimento.json  data/historico.json  data/atendimentos.csv (gerado)
```
Composição: `Assistente` → `BaseConhecimento` → lista de `Orientacao`.

## Regra de pontuação
- +3 por palavra-chave da orientação presente na pergunta
- +1 por palavra da pergunta (4+ letras) presente no título
- 6+ pontos: confiança ALTA; 3 a 5: MÉDIA; abaixo de 3: "não encontrei"
- Ajuste da equipe: palavras comuns (como, para, onde, qual...) não pontuam no título; alternativas só aparecem com 3+ pontos.

## Integrações com outras disciplinas
Nenhuma (preencher se houver).

## Fontes consultadas
Estatuto da Pessoa Idosa (Lei 10.741/2003), SPTrans, Metrô-SP, EMTU, ANTT, MDS. **Antes de entregar, abra cada link da base e reconfirme os dados, atualizando `verificado_em`.**

## Resultado do teste com usuários
(preencher: mínimo 3 pessoas, 10 atendimentos; indicadores, dúvidas sem solução e uma melhoria feita. Sem nomes.)

## Limitações
- Foco na Grande São Paulo; outras cidades têm regras próprias.
- Busca por palavras-chave: não entende sinônimos que não estejam no JSON.
- Regras de gratuidade mudam; a base precisa ser revisada periodicamente.
- Perguntas livres são salvas no histórico: o assistente bloqueia 8+ dígitos e "@", mas não detecta nomes.

## Vídeo técnico
(colar link do YouTube não listado)
