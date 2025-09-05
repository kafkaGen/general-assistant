from langchain_core.tools import StructuredTool


class ReasoningToolSet:
    def think(self, thought: str) -> str:
        """
        Pause to think, plan, and reflect on tasks or problems before taking action.

        This tool allows systematic reasoning, planning, and reflection without
        performing any external actions or modifying data. Use it to break down complex
        problems, analyze previous attempts, plan next steps, or reflect on results
        before proceeding.

        Args:
            thought (str): The reasoning, planning, or reflection content. Can include:
                - Problem analysis and breakdown
                - Step-by-step planning for complex tasks
                - Review of previous attempts and lessons learned
                - Reflection on tool results and next actions
                - Strategic thinking about approach or methodology
        """

        return thought

    def final_answer(self, answer: str) -> str:
        """
        Provide the final answer or conclusion to the user's question or request.

        This tool marks the completion of the task and delivers the final result to the
        user. Use this for both successful completions AND when all possible approaches
        have been exhausted without success. If unsuccessful - provide a clear
        explanation of what was attempted and why it failed.

        WHEN TO USE:
        - You have successfully completed all parts of the user's request
        - You have a complete, accurate answer ready to share
        - Multiple attempts have failed and no alternative solutions exist
        - You are confident no further progress is possible

        Args:
            answer (str): The complete, final answer to the user's question or request.
        """

        return answer

    def get_tools(self):
        return [
            StructuredTool.from_function(
                func=self.think,
                parse_docstring=True,
            ),
            StructuredTool.from_function(
                func=self.final_answer,
                parse_docstring=True,
            ),
        ]
