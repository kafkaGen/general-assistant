import asyncio
import contextlib
import io
import math
import traceback

import numpy as np
import pandas as pd
from langchain.tools import Tool


class PythonExecutorTool:
    safe_globals = {
        "__builtins__": {
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "sorted": sorted,
            "map": map,
            "filter": filter,
            "any": any,
            "all": all,
            "print": print,
        },
        "math": math,
        "np": np,
        "numpy": np,
        "pd": pd,
        "pandas": pd,
    }

    async def run_python_code(self, code: str) -> dict:
        """
        Execute a Python code snippet and return the result.
        Use `print(...)` to return results to the assistant. Only printed output is
        captured and returned.

        Do NOT include `import` statements. All necessary libraries are preloaded.
        Tool exposes the following libraries:
        - `math`
        - `numpy` as `np`
        - `pandas` as `pd`

        Args:
            code (str): Python code using math, pandas, or numpy.
                        The code should print its result using the `print()` function.
                        Example:
                            "arr = np.array([1, 2, 3]); print(np.mean(arr))"

        Returns:
            dict:
                - success (bool): True if execution succeeded, False on error
                - output (str): Printed result (or error trace if failed)

        Notes:
            - `import` statements are NOT allowed.
            - Preloaded aliases:
                - math
                - numpy as np
                - pandas as pd
        """

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._execute_code_sync, code)
            return result
        except Exception:
            return {"success": False, "output": traceback.format_exc()}

    def _execute_code_sync(self, code: str) -> dict:
        """Synchronous code execution helper."""
        stdout_buffer = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(code, self.safe_globals)
            return {
                "success": True,
                "output": stdout_buffer.getvalue().strip()
                or "[Code executed with no output]",
            }
        except Exception:
            return {"success": False, "output": traceback.format_exc()}

    def get_tools(self):
        return [
            Tool.from_function(
                func=self.run_python_code,
                name=self.run_python_code.__name__,
                description=str(self.run_python_code.__doc__),
                coroutine=self.run_python_code,
            ),
        ]
