import yaml
from typing import Any, Dict, Optional
from pathlib import Path

DEFAULT_CONFIG = {
    "default_channels": [],
    "summary_config": {"length": "medium"},
    "prompt_templates": {
        "default_summary": (
            "Summarize the following Telegram messages from the channel '{{channel_name}}' "
            "for the period '{{time_period}}'. Focus on key topics and highlights "
            "and provide the summary {{summary_length_guideline}}.\n\n"
            "Messages:\n{{messages}}"
        )
    },
    "checkpoints": {},
}


class ConfigManager:
    """Manages TeleShell configuration and state."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        if config_dir:
            self.base_dir = Path(config_dir)
        else:
            self.base_dir = Path.home() / ".teleshell"

        self.config_path = self.base_dir / "config.yaml"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from disk, creating default if missing."""
        if not self.config_path.exists():
            self._config = DEFAULT_CONFIG.copy()
            self.save()
        else:
            with open(self.config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
                self._config = self._merge_configs(DEFAULT_CONFIG, user_config)
        return self._config

    def save(self) -> None:
        """Save current configuration to disk."""
        with open(self.config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def _merge_configs(
        self, defaults: Dict[str, Any], user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursive merge of user config over defaults."""
        res = defaults.copy()
        for key, val in user.items():
            if key in res and isinstance(res[key], dict) and isinstance(val, dict):
                res[key] = self._merge_configs(res[key], val)
            else:
                res[key] = val
        return res

    def update_checkpoint(
        self, channel: str, last_message_id: int, last_message_date: str
    ) -> None:
        """Update a checkpoint for a given channel."""
        self.load()  # Ensure latest state
        if "checkpoints" not in self._config:
            self._config["checkpoints"] = {}

        self._config["checkpoints"][channel] = {
            "last_message_id": last_message_id,
            "last_message_date": last_message_date,
        }
        self.save()
