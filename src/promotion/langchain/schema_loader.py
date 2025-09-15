import glob
import json
from pathlib import Path

class SchemaLoader:
    """Loads and parses schema files from a directory."""

    def __init__(self, schema_dir: str):
        self.schema_dir = schema_dir

    def load(self) -> str:
        schema_files = glob.glob(str(Path(self.schema_dir) / "*.json"))
        descriptions = []
        for f in schema_files:
            try:
                with open(f, "r") as fp:
                    schema = json.load(fp)
                    table_name = schema.get("table_name")
                    table_desc = schema.get("table_description", "")
                    columns = schema.get("columns", [])
                    col_descs = []

                    for col in columns:
                        col_name = col.get("column_name")
                        col_type = col.get("metadata", {}).get("type", "")
                        col_description = col.get("description", "")
                        col_descs.append(f"- {col_name} ({col_type}): {col_description}")

                    table_schema = (
                        f"Table: {table_name}\n"
                        f"Description: {table_desc}\n"
                        f"Columns:\n{'\n'.join(col_descs)}"
                    )
                    descriptions.append(table_schema)
            except Exception as e:
                print(f"Error loading {f}: {e}")

        return "\n\n".join(descriptions)
