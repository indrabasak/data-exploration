import json
import re
from typing import Optional, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from sqlalchemy import text

from llm_util import LlmUtil
from schema_loader import SchemaLoader
from snowflake_util import SnowflakeUtil
from prompt import SQL_GENERATION_PROMPT

load_dotenv()


class GraphState(TypedDict):
    question: str
    sql_query: Optional[str]
    result_df: Optional[pd.DataFrame]
    summary_info: Optional[str]
    analysis: Optional[str]


class Analyzer:
    """Analyzes promotions using LLM and Snowflake."""

    def __init__(self, schema_dir: str):
        self.schema = SchemaLoader(schema_dir).load()
        self.analysis_graph = self._create_analysis_graph()

    def answer_question(self, question: str) -> dict[str, object]:
        """Answers a user question by running the analysis graph."""
        initial_state: GraphState = {
            "question": question,
            "sql_query": None,
            "result_df": None,
            "summary_info": None,
            "analysis": None,
        }
        final_state = self.analysis_graph.invoke(initial_state)

        return final_state

    def _clean_json_response(self, input_str: str) -> str:
        output_str = re.sub(r"```json\s*", "", input_str)
        output_str = re.sub(r"```", "", output_str)

        return output_str.strip()

    def _generate_sql_node(self, state: GraphState) -> GraphState:
        question = state["question"]
        schema_context = self.schema
        llm = LlmUtil.get_llm()
        system_prompt = SQL_GENERATION_PROMPT.format(schema_context=schema_context)
        response = llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
        )
        spec_str = response.content

        try:
            clean_str = self._clean_json_response(spec_str)
            spec_json = json.loads(clean_str)
            state["sql_query"] = spec_json.get("sql")
        except Exception as e:
            print(f"Could not parse JSON from LLM response: {e}")
            print(f"Raw LLM output: {spec_str}")
            state["sql_query"] = None

        return state

    def _run_sql_node(self, state: GraphState) -> GraphState:
        sql = state.get("sql_query")
        if not sql:
            return state
        engine = SnowflakeUtil.get_snowflake_engine()
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)
            state["result_df"] = df
        except Exception as e:
            print(f"Error executing SQL: {e}")
            state["result_df"] = None

        return state

    def summarise_dataframe(self, df: pd.DataFrame) -> str:
        lines = []
        n_rows, n_cols = df.shape
        date_cols = [c for c in df.columns if "date" in c.lower()]
        if date_cols:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            if "CURRENCY_CODE" in df.columns:
                grouped = df.groupby([df[date_col].dt.to_period("Q"), "CURRENCY_CODE"]).size()
                trend = {str(period): grouped.loc[period].to_dict()
                         for period in grouped.index.levels[0]}
                lines.append(f"Records per quarter by currency_code: {trend}")
            else:
                monthly_counts = df.groupby(df[date_col].dt.to_period("M")).size()
                lines.append(f"Records per month: {monthly_counts.to_dict()}")

            if "PROMOTION_DISCOUNT_AMOUNT" in df.columns:
                avg = df.groupby(df[date_col].dt.to_period("Q"))["PROMOTION_DISCOUNT_AMOUNT"].mean()
                lines.append(f"Average promotion_discount_amount per quarter: "
                             f"{ {str(p): round(v, 2) for p, v in avg.items()} }")
        else:
            lines.append("No date column found, so no time trends were computed.")

        return "\\n".join(lines)

    def _summarize_node(self, state: GraphState) -> GraphState:
        df = state.get("result_df")
        if df is None or df.empty:
            state["summary_info"] = "No data returned for the given query."
        else:
            state["summary_info"] = self.summarise_dataframe(df)

        return state

    def _analysis_node(self, state: GraphState) -> GraphState:
        df = state.get("result_df")
        question = state.get("question")
        summary_info = state.get("summary_info") or ""
        if df is None or df.empty:
            state["analysis"] = "No data was returned for the given query."
            return state
        llm = LlmUtil.get_llm()
        analysis_prompt = (
            f"The user asked: \"{question}\"\n\n"
            f"Here is a summary of the data:\n{summary_info}\n\n"
            f"Here are the first 10 rows of the data:\n{df.head(10).to_markdown()}\n\n"
            f"Provide a detailed analysis highlighting key patterns, trends, "
            f"and any notable outliers. Explain what these insights mean in simple business language."
        )
        response = llm.invoke(
            [
                {"role": "system", "content": "You are a data analyst who explains insights clearly and thoroughly."},
                {"role": "user", "content": analysis_prompt},
            ]
        )
        state["analysis"] = response.content

        return state

    def _create_analysis_graph(self) -> StateGraph:
        workflow: StateGraph = StateGraph(GraphState)
        workflow.add_node("generate_sql", self._generate_sql_node)
        workflow.add_node("run_sql", self._run_sql_node)
        workflow.add_node("summarize", self._summarize_node)
        workflow.add_node("analyze", self._analysis_node)
        workflow.add_edge(START, "generate_sql")
        workflow.add_edge("generate_sql", "run_sql")
        workflow.add_edge("run_sql", "summarize")
        workflow.add_edge("summarize", "analyze")
        workflow.add_edge("analyze", END)

        return workflow.compile()


def main():
    analyzer = Analyzer("schema")
    user_question = "How many promotions resulted in sales?"
    result = analyzer.answer_question(user_question)
    print("\nGenerated SQL:\n", result.get("sql_query"))
    print("\nSummary:\n", result.get("summary_info"))
    print("\nAnalysis:\n", result.get("analysis"))
    # print("===================================================")
    # user_question = "Which are the top five promotions?"
    # result = analyzer.answer_question(user_question)
    # print("\nGenerated SQL:\n", result.get("sql_query"))
    # print("\nSummary:\n", result.get("summary_info"))
    # print("\nAnalysis:\n", result.get("analysis"))
    # print("===================================================")
    # user_question = "Based on the past history, suggest a promotion that would result in increased sales next month? Explain why you think so."
    # result = analyzer.answer_question(user_question)
    # print("\nGenerated SQL:\n", result.get("sql_query"))
    # print("\nSummary:\n", result.get("summary_info"))
    # print("\nAnalysis:\n", result.get("analysis"))

if __name__ == "__main__":
    main()
