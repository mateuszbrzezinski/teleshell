import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from teleshell.summarizer import Summarizer


def test_prompt_construction():
    """Test if prompt is correctly constructed using templates and placeholders."""
    template = "Channel: {{channel_name}}, Period: {{time_period}}, Length: {{summary_length_guideline}}. Messages: {{messages}}"
    summarizer = Summarizer(api_key="test_key")

    prompt = summarizer.build_prompt(
        template=template,
        channel_name="@test",
        time_period="today",
        summary_length_guideline="short guideline",
        messages="Msg 1\nMsg 2",
    )

    assert "Channel: @test" in prompt
    assert "Period: today" in prompt
    assert "Length: short guideline" in prompt
    assert "Msg 1\nMsg 2" in prompt


def test_get_length_guideline():
    """Test translation of config length to text guideline."""
    summarizer = Summarizer(api_key="test_key")

    assert "1-3 concise sentences" in summarizer.get_length_guideline("short")
    assert "4-7 sentences" in summarizer.get_length_guideline("medium")
    assert "8-12 sentences" in summarizer.get_length_guideline("long")
    assert "up to 5 sentences" in summarizer.get_length_guideline(5)


@pytest.mark.asyncio
async def test_summarize_call():
    """Test the summarization call to LiteLLM."""
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a summary."
        mock_response.model = "gemini/gemini-flash-latest"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_acompletion.return_value = mock_response

        summarizer = Summarizer(api_key="test_key")
        result = await summarizer.summarize(
            messages=[{"text": "msg1"}],
            channel_name="@test",
            time_period="today",
            config={"length": "short"},
            template="Summarize {{messages}}",
        )

        assert isinstance(result, dict)
        assert result["content"] == "This is a summary."
        assert "metadata" in result
        assert result["metadata"]["input_tokens"] == 10
        mock_acompletion.assert_called_once()
