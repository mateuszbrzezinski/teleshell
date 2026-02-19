import os
import litellm
import time
from typing import List, Dict, Any, Union

class Summarizer:
    """Handles AI-powered summarization using LiteLLM."""

    def __init__(self, api_key: str, model: str = "gemini/gemini-flash-latest") -> None:
        self.api_key = api_key
        self.model = model
        # Configure LiteLLM
        os.environ["GEMINI_API_KEY"] = api_key

    def get_length_guideline(self, length: Union[str, int]) -> str:
        """Translate configuration length into a textual guideline for the LLM."""
        if length == "short":
            return "in 1-3 concise sentences"
        elif length == "medium":
            return "in 4-7 sentences"
        elif length == "long":
            return "in 8-12 sentences"
        elif isinstance(length, int) or (isinstance(length, str) and length.isdigit()):
            return f"in up to {length} sentences"
        return "in a concise manner"

    def build_prompt(
        self, 
        template: str, 
        channel_name: str, 
        time_period: str, 
        summary_length_guideline: str, 
        messages: str
    ) -> str:
        """Replace placeholders in the template with actual values."""
        prompt = template
        prompt = prompt.replace("{{channel_name}}", channel_name)
        prompt = prompt.replace("{{time_period}}", time_period)
        prompt = prompt.replace("{{summary_length_guideline}}", summary_length_guideline)
        prompt = prompt.replace("{{messages}}", messages)
        
        # Add internal formatting guidelines
        prompt += "\n\nFormat the output using Markdown. Use bold for key terms and bullet points for highlights where appropriate."
        return prompt

    async def summarize(
        self, 
        messages: List[Dict[str, Any]], 
        channel_name: str, 
        time_period: str, 
        config: Dict[str, Any],
        template: str
    ) -> Dict[str, Any]:
        """Generate a summary for the given messages and return with metadata."""
        if not messages:
            return {
                "content": "No messages to summarize for this period.",
                "metadata": {}
            }

        # Prepare messages text
        formatted_messages = "\n".join([
            f"- {msg.get('text', '')}" for msg in messages if msg.get('text')
        ])

        length_guideline = self.get_length_guideline(config.get("length", "medium"))
        
        prompt = self.build_prompt(
            template=template,
            channel_name=channel_name,
            time_period=time_period,
            summary_length_guideline=length_guideline,
            messages=formatted_messages
        )

        start_time = time.time()
        response = await litellm.acompletion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        end_time = time.time()

        content = response.choices[0].message.content
        usage = getattr(response, "usage", None)
        
        metadata = {
            "model": response.model,
            "latency": round(end_time - start_time, 2),
            "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        }

        return {
            "content": content,
            "metadata": metadata
        }
