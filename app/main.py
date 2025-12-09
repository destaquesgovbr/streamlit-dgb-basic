from datetime import datetime
from typing import Tuple

import altair as alt
import pandas as pd
import streamlit as st
from datasets import load_dataset

# Set the layout to wide
st.set_page_config(
    page_title="Análise de Notícias GovBR",
    page_icon="📰",
    layout="wide",
)


class GovBRNewsAnalysis:
    """Class to encapsulate the logic for analyzing GovBR News data."""

    df: pd.DataFrame

    def __init__(self):
        self.granularity_column = "year"

    @staticmethod
    @st.cache_data(ttl=3600 * 6)  # Cache the dataset for 6 hours
    def load_data() -> pd.DataFrame:
        """
        Load the dataset from Hugging Face and prepare necessary columns.

        Returns:
            pd.DataFrame: Preprocessed dataset with temporal columns.
        """
        dataset = load_dataset("nitaibezerra/govbrnews-reduced", split="train")
        df = pd.DataFrame(dataset)
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["year"] = df["published_at"].dt.year
        df["month"] = df["published_at"].dt.to_period("M").dt.to_timestamp()
        df["week"] = df["published_at"].dt.to_period("W").dt.to_timestamp()
        df["day"] = df["published_at"].dt.date
        return df

    def select_agencies(self) -> list:
        """
        Provide a UI to select the agencies to be considered,
        with a button to reset to the initial state, inside a collapsible expander.

        Returns:
            list: List of selected agencies.
        """
        agencies = sorted(self.df["agency"].unique().tolist())

        # Use Streamlit's session state to track the selected agencies
        if "selected_agencies" not in st.session_state:
            st.session_state.selected_agencies = agencies

        # Define a callback function to reset the selection
        def reset_selection():
            st.session_state.selected_agencies = agencies

        # Collapsible expander for the selector
        with st.expander("Selecionar Agências", expanded=False):
            st.button("Selecionar todas as agências", on_click=reset_selection)
            selected_agencies = st.multiselect(
                "Selecione as agências para considerar na análise",
                options=agencies,
                default=st.session_state.selected_agencies,
                help="Escolha as agências cujas notícias você deseja incluir na análise.",
                key="selected_agencies",
            )

        return selected_agencies

    def select_granularity(self) -> str:
        """
        Provide a UI to select the granularity for analysis.

        Returns:
            str: Selected granularity.
        """
        granularity = st.selectbox(
            "Selecione a granularidade temporal",
            options=["Year", "Month", "Week", "Day"],
            index=0,  # Default is "Year"
        )
        self.granularity_column = granularity.lower()
        return granularity

    def get_min_max_values(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """
        Retrieve the minimum and maximum values for the temporal range based on 'day'.

        Returns:
            Tuple[pd.Timestamp, pd.Timestamp]: Minimum and maximum values.
        """
        min_value = self.df["day"].min()
        max_value = self.df["day"].max()
        return min_value, max_value

    def filter_data(
        self, selected_range: Tuple[pd.Timestamp, pd.Timestamp]
    ) -> pd.DataFrame:
        """
        Filter the dataset based on the selected day range.

        Args:
            selected_range (Tuple[pd.Timestamp, pd.Timestamp]): Selected day range for filtering.

        Returns:
            pd.DataFrame: Filtered dataset.
        """
        return self.df[
            (self.df["day"] >= selected_range[0])
            & (self.df["day"] <= selected_range[1])
        ]

    def aggregate_data(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate the filtered dataset by the selected granularity.

        Args:
            filtered_df (pd.DataFrame): Filtered dataset.

        Returns:
            pd.DataFrame: Aggregated dataset with counts.
        """
        news_by_granularity = (
            filtered_df[self.granularity_column]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        news_by_granularity.columns = [self.granularity_column.capitalize(), "Count"]
        return news_by_granularity

    def aggregate_by_agency(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate the filtered dataset by agency and granularity.

        Args:
            filtered_df (pd.DataFrame): Filtered dataset.

        Returns:
            pd.DataFrame: Aggregated dataset with counts by agency.
        """
        grouped = (
            filtered_df.groupby([self.granularity_column, "agency"])
            .size()
            .reset_index(name="Count")
        )
        grouped.columns = [self.granularity_column.capitalize(), "Agency", "Count"]
        return grouped

    def plot_total(self, data: pd.DataFrame, granularity: str) -> None:
        """
        Plot the aggregated data as a line chart with formatted x-axis labels.

        Args:
            data (pd.DataFrame): Aggregated data to plot.
            granularity (str): Temporal granularity for the plot.
        """
        # Format x-axis labels based on granularity
        if granularity.lower() == "month":
            data[granularity] = data[granularity].dt.strftime("%Y-%m")
        elif granularity.lower() == "week":
            data[granularity] = data[granularity].dt.strftime("%G-W%V")
        elif granularity.lower() == "day":
            data[granularity] = pd.to_datetime(data[granularity]).dt.strftime(
                "%Y-%m-%d"
            )

        chart = (
            alt.Chart(data)
            .mark_line()
            .encode(
                x=alt.X(f"{granularity}:O", title=granularity),
                y=alt.Y("Count:Q", title="Número de Artigos"),
                tooltip=[granularity, "Count"],
            )
            .properties(
                title=f"Número de Artigos de Notícias por {granularity}",
                width=700,
                height=400,
            )
        )
        st.altair_chart(chart, use_container_width=True)

    def plot_by_agency(
        self, data: pd.DataFrame, granularity: str, rank_range: Tuple[int, int]
    ) -> None:
        """
        Plot the aggregated data as a line chart with one line per agency,
        showing agencies within the selected rank range.

        Args:
            data (pd.DataFrame): Aggregated data to plot.
            granularity (str): Temporal granularity for the plot.
            rank_range (Tuple[int, int]): The range of ranks to display (e.g., (1, 10)).
        """
        # Determine the agencies within the selected rank range
        top_agencies = (
            data.groupby("Agency")["Count"]
            .sum()
            .nlargest(rank_range[1])  # Get up to the highest rank
            .iloc[rank_range[0] - 1 : rank_range[1]]  # Select the specific range
            .index
        )
        data = data[data["Agency"].isin(top_agencies)]

        # Format x-axis labels based on granularity
        if granularity.lower() == "month":
            data[granularity] = data[granularity].dt.strftime("%Y-%m")
        elif granularity.lower() == "week":
            data[granularity] = data[granularity].dt.strftime("%G-W%V")
        elif granularity.lower() == "day":
            data[granularity] = pd.to_datetime(data[granularity]).dt.strftime(
                "%Y-%m-%d"
            )

        chart = (
            alt.Chart(data)
            .mark_line()
            .encode(
                x=alt.X(f"{granularity}:O", title=granularity),
                y=alt.Y("Count:Q", title="Número de Artigos"),
                color="Agency:N",
                tooltip=[granularity, "Agency", "Count"],
            )
            .properties(
                title=f"Número de Artigos por Agência (Classificação {rank_range[0]} a {rank_range[1]})",
                width=700,
                height=400,
            )
        )
        st.altair_chart(chart, use_container_width=True)

    def display_filtered_articles(
        self, filtered_df: pd.DataFrame, rank_range: Tuple[int, int]
    ) -> None:
        """
        Display a table of articles ordered by published_at (desc) and agency (asc),
        filtered by the rank range.

        Args:
            filtered_df (pd.DataFrame): Filtered dataset.
            rank_range (Tuple[int, int]): The range of ranks to display (e.g., (1, 10)).
        """
        # Determine the agencies within the selected rank range
        top_agencies = (
            filtered_df.groupby("agency")["title"]
            .count()
            .nlargest(rank_range[1])  # Get up to the highest rank
            .iloc[rank_range[0] - 1 : rank_range[1]]  # Select the specific range
            .index
        )

        # Filter the dataset for articles from the selected agencies
        filtered_articles = filtered_df[filtered_df["agency"].isin(top_agencies)]

        # Sort the filtered dataset
        sorted_articles = filtered_articles.sort_values(
            by=["published_at", "agency"], ascending=[False, True]
        )

        # Format `published_at` to display only DD/MM/YYYY
        sorted_articles["published_date"] = sorted_articles["published_at"].dt.strftime(
            "%d/%m/%Y"
        )

        # Select the desired columns
        displayed_columns = sorted_articles[
            ["published_date", "agency", "title", "url"]
        ]

        # Display the table
        st.write("### Artigos Filtrados")
        st.dataframe(displayed_columns, use_container_width=True)

    def run(self) -> None:
        """Run the Streamlit application."""
        st.title("Análise de Notícias GovBR")

        # ---------------------- INTRODUCTORY TEXT ----------------------
        st.markdown(
            """
            **Bem-vindo(a) à ferramenta de análise das notícias do GovBR!**
            Esta aplicação apresenta um panorama abrangente das notícias publicadas em
            diferentes agências do governo brasileiro, extraídas diretamente do portal
            [gov.br](https://www.gov.br) por meio de um scraper em Python, cujo código-fonte
            se encontra disponível em [**GitHub**](https://github.com/nitaibezerra/govbrnews-scraper).
            Além de conter títulos, datas de publicação e textos completos, a base de dados
            inclui informações sobre as agências responsáveis por cada notícia, facilitando
            análises comparativas e temporais.

            O objetivo deste dashboard é oferecer uma ferramenta interativa para filtrar,
            visualizar e explorar de forma dinâmica esses conteúdos. Você poderá selecionar
            períodos específicos e focar nas agências de seu interesse, gerando gráficos que
            ajudam a entender como a divulgação de informações governamentais evolui ao longo
            do tempo e como se distribui entre os diferentes órgãos. Dessa forma, pesquisadores,
            jornalistas ou qualquer pessoa interessada podem obter insights valiosos sobre a
            comunicação oficial no Brasil.

            Para ter acesso a todos os dados brutos e realizar análises próprias, visite a página
            do dataset no [**Hugging Face**](https://huggingface.co/datasets/nitaibezerra/govbrnews),
            onde você encontrará a coleção completa de artigos já pré-processados e prontos para uso
            em projetos de NLP, mineração de textos, análise de tendências ou qualquer outra aplicação
            que envolva conteúdo governamental. Esperamos que este aplicativo seja útil para suas
            pesquisas e lhe desejamos uma ótima exploração!
            """
        )
        # Load the dataset
        self.df = self.load_data()

        # Select agencies
        selected_agencies = self.select_agencies()

        # Filter the data by selected agencies
        self.df = self.df[self.df["agency"].isin(selected_agencies)]

        # Select granularity for aggregation
        granularity = self.select_granularity()

        # Get min and max values for the day range selector
        _, max_value = self.get_min_max_values()

        # Temporal range selector (always day-based)
        selected_range = st.slider(
            "Selecione o intervalo de dias",
            min_value=datetime(2000, 1, 1).date(),
            max_value=max_value,
            value=(
                datetime(2010, 1, 1).date(),
                max_value,
            ),  # Default start date
            format="YYYY-MM-DD",
        )

        # Filter and process data
        filtered_df = self.filter_data(selected_range)
        aggregated_data = self.aggregate_data(filtered_df)
        aggregated_by_agency = self.aggregate_by_agency(filtered_df)

        # Display total number of news articles
        total_articles = filtered_df.shape[0]
        st.metric(label="Total de Artigos de Notícias", value=total_articles)

        # Plot the data
        self.plot_total(aggregated_data, granularity)

        # Dynamically calculate max_value for the rank slider based on the number of agencies
        max_agencies = aggregated_by_agency["Agency"].nunique()

        # Add range slider for selecting the rank range
        rank_range = st.slider(
            "Selecione o intervalo de agências para exibir por classificação",
            min_value=1,
            max_value=max_agencies,
            value=(
                1,
                min(10, max_agencies),
            ),
            step=1,
            help="Ajuste para mostrar um intervalo específico de agências por classificação.",
        )

        # Plot the data by agency with rank range
        self.plot_by_agency(aggregated_by_agency, granularity, rank_range)

        # Display the filtered articles table
        self.display_filtered_articles(filtered_df, rank_range)


# Run the application
if __name__ == "__main__":
    app = GovBRNewsAnalysis()
    app.run()
