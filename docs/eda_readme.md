# 📊 Documentação EDA - Camada Silver (CGMacros)

## 📋 Visão Geral
Esta camada contém os dados de sensores de glicose e biométricos dos pacientes, convertidos de CSV para **Parquet**. Os dados foram tipados, limpos e padronizados para garantir a integridade das séries temporais.

**Granularidade:** 1 minuto (amostragem por linha).  
**Formato:** Parquet (Snappy compression).  
**Bucket Minio:** `cgmacros/silver/CGMacros/`

---

## 🏗 Dicionário de Dados (Schema)

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `Timestamp` | `datetime64[ns]` | Carimbo de tempo da leitura (Fuso local). |
| `Libre GL` | `float64` | Glicemia medida pelo sensor Abbott Libre (mg/dL). |
| `Dexcom GL` | `float64` | Glicemia medida pelo sensor Dexcom (mg/dL). |
| `HR` | `float64` | Frequência Cardíaca (Batimentos por minuto). |
| `Calories (Activity)` | `float64` | Gasto calórico estimado por atividade. |
| `Meal Type` | `string` | Tipo da refeição (Café, Almoço, Jantar, Snack). |
| `Carbs` / `Protein` / `Fat` | `float64` | Macronutrientes da refeição (se houver). |
| `Image path` | `string` | Caminho para a foto da refeição no Minio. |

---

## 🔍 Principais Insights da Análise (EDA)

### 1. Integridade dos Sensores
* **Libre vs Dexcom:** Foi observada uma discrepância média de **~25 mg/dL**, com o sensor Libre apresentando valores sistematicamente mais altos e picos mais acentuados (Máx: 342 mg/dL) em relação ao Dexcom (Máx: 300 mg/dL).
* **Dados Faltantes (Gaps):** * O **Dexcom** apresentou falhas de sinal em ~2.6% dos registros.
    * O **HR (Batimentos)** apresentou a maior taxa de nulos (~8.5%), sugerindo desconexão do dispositivo vestível em períodos de repouso ou carregamento.

### 2. Comportamento Glicêmico
* **Perfil do Paciente:** Alta variabilidade glicêmica. Médias em torno de **164 mg/dL**, com episódios frequentes de hiperglicemia (> 200 mg/dL).
* **Eventos de Refeição:** Os dados de alimentação são esparsos (apenas ~33 registros em 14.600 linhas). Isso exige a criação de janelas sintéticas (ex: 120 min) para análise de impacto pós-prandial.

---

## 🛠 Processamento Realizado (Silver Pipeline)

1.  **Conversão de Formato:** Transição de CSV para Parquet para otimização de armazenamento e velocidade de leitura.
2.  **Tipagem Estrita:** Conversão manual de strings para floats e objetos datetime.
3.  **Tratamento de Nulos:** * Sensores de Glicose: Interpolação linear para gaps de até 15 minutos.
    * Batimentos Cardíacos: Interpolação linear para gaps de até 5 minutos.
4.  **Sincronização:** Ordenação rigorosa por `Timestamp` para garantir que os métodos de *shift* e *rolling* funcionem corretamente na camada Gold.

---

## 📈 Visualizações de Referência
Os relatórios visuais de cada paciente, incluindo histogramas de distribuição e matrizes de correlação, encontram-se no Minio em:
`cgmacros/eda_reports/{PATIENT_ID}/`

---

## 🚀 Próximos Passos (Camada Gold)
* Criação de janelas de 120 minutos para impacto de refeições (`In_Meal_Window`).
* Geração de **Lags** (5, 15, 30, 60 min) para modelos de previsão.
* Engenharia de **Target** com horizonte de 30 minutos para Forecasting.

---

### Como você pode usar este arquivo:
1.  Crie um arquivo chamado `README.md` localmente.
2.  Cole o conteúdo acima.
3.  Você pode fazer o upload dele para o próprio Minio na raiz da pasta `silver` para que o projeto fique documentado "dentro do dado".

```python
# Exemplo rápido para subir o README pro Minio
with open("README.md", "rb") as f:
    client.put_object(
        "cgmacros", "silver/CGMacros/README.md", 
        data=f, 
        length=os.path.getsize("README.md"), 
        content_type="text/markdown"
    )
```