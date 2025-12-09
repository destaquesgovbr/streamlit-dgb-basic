import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DGB Streamlit App",
    page_icon="📊",
    layout="wide",
)

def main():
    st.title("📊 Minha Aplicação DGB Streamlit")

    st.markdown("""
    Bem-vindo à Plataforma Streamlit DGB!

    Este é um app boilerplate. Substitua este conteúdo pela sua aplicação.
    """)

    # Exemplo: Dados em cache
    @st.cache_data
    def load_data():
        return pd.DataFrame({
            'coluna1': [1, 2, 3, 4, 5],
            'coluna2': [10, 20, 30, 40, 50]
        })

    df = load_data()

    st.subheader("Exemplo de DataFrame")
    st.dataframe(df, use_container_width=True)

    # Exemplo: Interação
    opcao = st.selectbox(
        'Selecione uma opção',
        ['Opção 1', 'Opção 2', 'Opção 3']
    )
    st.write(f'Você selecionou: {opcao}')

    # Exemplo: Gráfico
    st.subheader("Exemplo de Gráfico")
    st.line_chart(df.set_index('coluna1'))

if __name__ == "__main__":
    main()
