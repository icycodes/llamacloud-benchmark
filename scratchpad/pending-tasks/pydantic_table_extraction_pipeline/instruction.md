Financial documents often contain dense tables that are difficult to parse accurately. LlamaParse's high-fidelity extraction paired with structured LLM outputs ensures downstream applications receive reliable data.

You need to write a script `extract_table.py` that uses `LlamaParse` to read a local file `financial_report.pdf` into markdown format. Then, use LlamaIndex's structured output capabilities (e.g., `.as_structured_llm()` or program outputs) to prompt an LLM to extract the parsed markdown table into a predefined Pydantic model named `FinancialResults`. The model must contain `revenue`, `expenses`, and `net_income` (all as floats). Finally, print the JSON representation of the extracted Pydantic object.

**Constraints:**
- Must use `LlamaParse` as the document loader.
- Must define the `FinancialResults` Pydantic class exactly as specified.
- The final output printed to stdout MUST be the valid JSON string representation of the instantiated Pydantic object.