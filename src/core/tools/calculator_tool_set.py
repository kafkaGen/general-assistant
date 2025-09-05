from e2b_code_interpreter import Sandbox
from langchain_core.tools import StructuredTool


class CalculatorToolSet:
    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    def execute_code(self, python_code: str) -> str:
        """
        Calculator - deterministic Python execution for math and data operations.

        MANDATORY: Use this tool for ALL numeric calculations - never calculate
        manually.

        WHEN TO USE:
        - Any arithmetic or numeric reasoning (sum, diff, %, ratios, growth, ROI).
        - Statistics/aggregation (mean, median, std), vector/matrix math.
        - Data wrangling on small in-memory tables/arrays (NumPy, pandas).

        REQUIREMENTS:
        - Include ALL necessary import statements (numpy, pandas, math, etc.)
        - Use print() to output results you want to see
        - Code must be complete and executable

        Args:
            python_code (str): Complete Python code with imports and print statements.
        """

        sbx = Sandbox.create()
        run_result = sbx.run_code(python_code, timeout=self._timeout)

        execution_response = ""
        if run_result.results:
            execution_response += (
                "\n<code_return>\n" + "".join(run_result.results) + "\n</code_return>\n"
            )
        if run_result.logs.stdout:
            execution_response += (
                "\n<stdout>\n" + "".join(run_result.logs.stdout) + "\n</stdout>\n"
            )
        if run_result.logs.stderr:
            execution_response += (
                "\n<stderr>\n" + "".join(run_result.logs.stderr) + "\n</stderr>\n"
            )
        if run_result.error:
            execution_response += (
                "\n<error>\n" + run_result.error.traceback + "\n</error>\n"
            )

        return execution_response.strip()

    def get_tools(self):
        return [
            StructuredTool.from_function(
                name="calculator",
                func=self.execute_code,
                # coroutine=...,
                parse_docstring=True,
                # handle_tool_error=True,
            ),
        ]
