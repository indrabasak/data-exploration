import json
import re
from enum import Enum
from typing import Optional, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from sqlalchemy import text

from bedrock_llm_util import BedrockLlmUtil
from llm_util import LlmUtil
from prompt import SQL_GENERATION_PROMPT
from schema_loader import SchemaLoader
from snowflake_util import SnowflakeUtil

load_dotenv()


class GraphState(TypedDict):
    question: str
    sql_query: Optional[str]
    result_df: Optional[pd.DataFrame]
    summary_info: Optional[str]
    analysis: Optional[str]

class LlmProvider(Enum):
    APS_ANTHROPIC = 1
    AZURE_OPENAI = 2

class Analyzer:
    """Analyzes promotions using LLM and Snowflake."""

    def __init__(self, llm_provider: LlmProvider, schema_dir: str):
        self.llm_provider = llm_provider
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

    def get_llm(self):
        if self.llm_provider == LlmProvider.APS_ANTHROPIC:
            return BedrockLlmUtil.get_llm()
        elif self.llm_provider == LlmProvider.AZURE_OPENAI:
            return LlmUtil.get_llm()
        else:
            raise ValueError("Unsupported LLM provider")

    @staticmethod
    def clean_response(input) -> str:
        # Case 1: Direct JSON string
        if isinstance(input, str):
            output_str = re.sub(r"```json\s*", "", input)
            output_str = re.sub(r"```", "", output_str)
            return output_str.strip()

        # Case 2: List with 'text' containing Markdown JSON
        if isinstance(input, list) and input and 'text' in input[0]:
            text = input[0]['text']
            json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json_str

        raise ValueError("No valid JSON found in input.")

    def _generate_sql_node(self, state: GraphState) -> GraphState:
        question = state["question"]
        schema_context = self.schema
        llm = self.get_llm()
        system_prompt = SQL_GENERATION_PROMPT.format(schema_context=schema_context)
        print(system_prompt)
        response = llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
        )
        spec_str = response.content

        try:
            clean_str = Analyzer.clean_response(spec_str)
            spec_json = json.loads(clean_str)
            state["sql_query"] = spec_json.get("sql")
        except Exception as e:
            print(f"Could not parse JSON from LLM response: {e}")
            print(f"Raw LLM output: {spec_str}")
            state["sql_query"] = None

        return state

    @staticmethod
    def run_sql_node(state: GraphState) -> GraphState:
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

    @staticmethod
    def summarize_dataframe(df: pd.DataFrame) -> str:
        lines = []
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

    @staticmethod
    def summarize_node(state: GraphState) -> GraphState:
        df = state.get("result_df")
        if df is None or df.empty:
            state["summary_info"] = "No data returned for the given query."
        else:
            state["summary_info"] = Analyzer.summarize_dataframe(df)

        return state

    @staticmethod
    def analysis_node(state: GraphState) -> GraphState:
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
        workflow.add_node("run_sql", Analyzer.run_sql_node)
        workflow.add_node("summarize",  Analyzer.summarize_node)
        workflow.add_node("analyze", Analyzer.analysis_node)
        workflow.add_edge(START, "generate_sql")
        workflow.add_edge("generate_sql", "run_sql")
        workflow.add_edge("run_sql", "summarize")
        workflow.add_edge("summarize", "analyze")
        workflow.add_edge("analyze", END)

        return workflow.compile()


def main():
    analyzer = Analyzer(LlmProvider.APS_ANTHROPIC, "schema")
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
