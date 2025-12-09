# Análise de Notícias GovBR

Dashboard interativo para análise temporal de notícias do portal gov.br por agência governamental.

**🚀 Criado a partir do** [streamlit-boilerplate](https://github.com/destaquesgovbr/streamlit-boilerplate)

---

## Sobre

Este aplicativo Streamlit permite explorar e analisar notícias publicadas em diferentes agências do governo brasileiro, extraídas do portal [gov.br](https://www.gov.br).

### Funcionalidades

- 📊 **Análise temporal**: Visualize notícias por ano, mês, semana ou dia
- 🏛️ **Filtro por agências**: Selecione agências governamentais específicas
- 📈 **Visualizações interativas**: Gráficos com Altair
- 📰 **Listagem detalhada**: Tabela com artigos filtrados
- 🔍 **Ranking de agências**: Veja as agências mais ativas

### Dados

Dataset hospedado no HuggingFace:
- **Dataset completo**: [`nitaibezerra/govbrnews`](https://huggingface.co/datasets/nitaibezerra/govbrnews)
- **Dataset reduzido**: [`nitaibezerra/govbrnews-reduced`](https://huggingface.co/datasets/nitaibezerra/govbrnews-reduced) (usado neste app)
- **Scraper**: https://github.com/nitaibezerra/govbrnews-scraper

---

## Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/destaquesgovbr/streamlit-dgb-basic.git
   cd streamlit-dgb-basic
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o app localmente:
   ```bash
   streamlit run app/main.py
   ```

4. Acesse `http://localhost:8501` no navegador

### Estrutura do Projeto

```
streamlit-dgb-basic/
├── app/
│   ├── main.py              # Aplicação principal com análise de notícias
│   ├── components/          # Componentes reutilizáveis
│   └── utils/               # Funções auxiliares
├── tests/
│   └── test_app.py          # Testes
├── .streamlit/
│   └── config.toml          # Configuração do Streamlit
├── .streamlit-app.yaml      # Metadados para catálogo
├── Dockerfile               # Container definition
└── requirements.txt         # Dependências Python
```

### Testes

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar testes
pytest

# Rodar com cobertura
pytest --cov=app tests/
```

---

## Deploy na Plataforma DGB

Este app está deployado na **Plataforma Streamlit DGB** via Cloud Run.

### Status do Deploy

- ✅ **Repositório**: https://github.com/destaquesgovbr/streamlit-dgb-basic
- 🔄 **Deploy**: Automático via GitHub Actions (push to main)
- ☁️ **Hospedagem**: Google Cloud Run
- 🔐 **Acesso**: Público via URL

### URL da Aplicação

🌐 **[Será preenchida após deploy]**

---

## Tecnologias

- **Streamlit 1.41.0**: Framework para dashboards interativos
- **HuggingFace Datasets 3.2.0**: Carregamento de dados
- **Altair 5.2.0**: Visualizações declarativas
- **Pandas 2.2.0**: Manipulação de dados

---

## Como Funciona

1. **Carregamento de Dados**: Dataset `nitaibezerra/govbrnews-reduced` é carregado do HuggingFace e cacheado por 6 horas
2. **Seleção de Agências**: Multiselect permite filtrar agências de interesse
3. **Granularidade Temporal**: Escolha entre ano, mês, semana ou dia
4. **Filtro de Período**: Slider para selecionar intervalo de datas
5. **Visualizações**:
   - Gráfico de linha com total de notícias ao longo do tempo
   - Gráfico comparativo por agência (top N agências)
   - Tabela com artigos ordenados por data

---

## Exemplo de Uso

```python
# O app usa cache do Streamlit para performance
@st.cache_data(ttl=3600 * 6)  # Cache por 6 horas
def load_data() -> pd.DataFrame:
    dataset = load_dataset("nitaibezerra/govbrnews-reduced", split="train")
    df = pd.DataFrame(dataset)
    # ... processamento temporal
    return df
```

---

## Contribuindo

Este app foi criado como validação da Plataforma Streamlit DGB (Fase 1 do plano de implementação).

Para contribuir:
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## Licença

MIT License - ver [LICENSE](LICENSE) para detalhes.

---

## Links Úteis

- **Plataforma Streamlit DGB**: [destaquesgovbr-infra](https://github.com/destaquesgovbr/destaquesgovbr-infra)
- **Template Boilerplate**: [streamlit-boilerplate](https://github.com/destaquesgovbr/streamlit-boilerplate)
- **Catálogo de Apps**: [streamlit-catalog](https://destaquesgovbr.github.io/streamlit-catalog/)
- **Documentação**: [docs/streamlit-platform.md](https://github.com/destaquesgovbr/destaquesgovbr-infra/blob/main/docs/streamlit-platform.md)

---

## Case Study

Este app faz parte da **Fase 1** do plano de implementação da Plataforma Streamlit DGB, servindo como validação end-to-end de todo o processo:

- ✅ Uso do template boilerplate
- ✅ Migração de app existente
- ✅ Registro via issue template
- ✅ PR automatizado
- ✅ Deploy no Cloud Run
- ✅ Integração com HuggingFace

Para mais detalhes, veja [STREAMLIT_PLATFORM_PLAN_2.md](https://github.com/destaquesgovbr/destaquesgovbr-infra/blob/main/STREAMLIT_PLATFORM_PLAN_2.md).
