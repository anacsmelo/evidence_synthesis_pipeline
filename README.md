# Avaliação da Qualidade Metodológica de Sínteses de Evidência Geradas por LLMs
Este repositório contém o código, os scripts auxiliares e os dados derivados utilizados no Trabalho de Conclusão de Curso (TCC) 
em Engenharia Biomédica, cujo objetivo é avaliar a qualidade metodológica de sínteses de evidência geradas por 
Modelos de Linguagem de Grande Escala (Large Language Models – LLMs), utilizando o framework PICOS 
(Population, Intervention, Comparator, Outcomes, Study design).

O estudo investiga em que medida LLMs conseguem reconstruir, de forma metodologicamente adequada, uma síntese de evidência 
previamente consolidada a partir da literatura científica, mantendo controle rigoroso sobre dados de entrada, 
parâmetros de geração, prompts e critérios de avaliação.

---
## Pergunta de Pesquisa
Qual é a qualidade metodológica das sínteses de evidência geradas por LLMs quando avaliadas segundo o framework PICOS, 
em comparação com uma síntese de evidência consolidada baseada na literatura científica?

---
## Modelos Avaliados

As APIs de LLMs são acessadas via OpenRouter, permitindo uso padronizado
dos seguintes modelos:

- Qwen / Qwen3-4B (modelo compacto)
- DeepSeek / R1-0528 (modelo com ênfase em raciocínio)
- OpenAI / gpt-oss-120B (modelo de larga escala)

Esses modelos representam diferentes classes arquiteturais e escalas,
possibilitando a análise do impacto dessas características na qualidade
metodológica das sínteses geradas.

---
## Pipeline Metodológico

1. **Seleção da literatura**
   - Artigos científicos armazenados em formato PDF (`data/sources/articles_pdf`)

2. **Extração padronizada de texto**
   - Conversão de PDFs para texto utilizando um único script (`extract_pdfs_to_text.py`)
   - Preservação do conteúdo textual sem interpretação semântica

3. **Construção do corpus**
   - Textos extraídos compilados em um corpus único (`corpus_compiled.md`)
   - Corpus fixo utilizado como entrada para todas as LLMs

4. **Geração das sínteses**
   - Execução controlada via `run_generation.py`
   - Prompts estruturados segundo PICOS
   - Parâmetros de geração explicitamente documentados

5.	**Avaliação automática**
   - Extração e pontuação automática dos componentes PICOS por meio de parser dedicado
   - Geração de tabelas intermediárias (`picos_scores.csv`)

6.	**Avaliação humana**
	•	Avaliação manual de clareza e fidelidade metodológica
	•	Registro estruturado em scoring_sheet.csv
7.	**Integração e métricas**
   - Integração entre avaliação automática e humana (`picos_combined.csv`)
   - Cálculo de métricas agregadas por modelo e prompt (`metrics_by_model_prompt.csv`)

8.	**Visualização dos resultados**
   - Geração automática de gráficos por meio do script `results/generate_plots.py`
   - Figuras exportadas em alta resolução para uso em relatório e monografia

---
## Reprodutibilidade

- Todos os prompts são versionados
- Todos os parâmetros de geração são documentados em `configs.yaml`
- Cada saída é registrada em `metadata_log.json`
- O uso de uma única API (OpenRouter) garante uniformidade de acesso aos modelos
- Scripts são determinísticos sempre que possível

---
## Configuração do Ambiente

1. Criar ambiente virtual:
   python3 -m venv venv
   source venv/bin/activate

2. Instalar dependências:
   pip install -r requirements.txt

3. Definir variável de ambiente no arquivo `.env`:
   export OPENROUTER_API_KEY="sua_chave_aqui"

---
## Reprodução do Experimento

1. **Extração dos textos**
   python3 scripts/extract_pdfs_to_text.py

2. **Construção do corpus**
   python3 scripts/build_corpus.py

3. **Geração das sínteses**
   python3 experiments/run_generation.py

4. **Avaliação automática e integração**
   python3 evaluation/picos_parser.py
   python3 evaluation/picos_aggregator.py
   python3 evaluation/metrics.py

5. **Geração de gráficos**
   python3 results/generate_plots.py

---

## Observações Metodológicas Importantes
- PDFs não são fornecidos diretamente às LLMs
- Não há fine-tuning ou otimização de prompts por modelo
- Não são utilizadas ferramentas externas de recuperação (RAG)
- Diferenças observadas entre sínteses são atribuídas exclusivamente às características dos modelos avaliados
- Métricas operacionais (ex.: taxa de geração válida) são utilizadas apenas como controle do pipeline, não como critério de qualidade metodológica


---

## Licença
Este projeto é distribuído sob a licença GNU General Public License v3.0 (GPL-3.0).

Você é livre para:
	•	usar
	•	estudar
	•	modificar
	•	redistribuir

desde que qualquer trabalho derivado mantenha a mesma licença.

O texto completo da licença pode ser encontrado em:
https://www.gnu.org/licenses/gpl-3.0.html

---
## Direitos Autorais e Uso Acadêmico

Este repositório é destinado exclusivamente a fins acadêmicos.
Os artigos científicos utilizados permanecem sob seus respectivos direitos autorais.
