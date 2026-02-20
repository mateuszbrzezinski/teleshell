import yaml
from teleshell.config import ConfigManager


def test_load_default_config(tmp_path):
    """Test loading default configuration values when file is missing."""
    config_dir = tmp_path / ".teleshell"
    config_dir.mkdir()

    # We pass the temporary path to ConfigManager
    manager = ConfigManager(config_dir=str(config_dir))
    config = manager.load()

    assert config["summary_config"]["length"] == "medium"
    assert config["default_channels"] == []


def test_load_user_config(tmp_path):
    """Test loading configuration from an existing YAML file."""
    config_dir = tmp_path / ".teleshell"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"

    user_data = {
        "default_channels": ["@test_channel"],
        "summary_config": {"length": "short"},
    }

    with open(config_file, "w") as f:
        yaml.dump(user_data, f)

    manager = ConfigManager(config_dir=str(config_dir))
    config = manager.load()

    assert config["default_channels"] == ["@test_channel"]
    assert config["summary_config"]["length"] == "short"


def test_checkpoint_management(tmp_path):
    """Test saving and loading checkpoints."""
    config_dir = tmp_path / ".teleshell"
    config_dir.mkdir()

    manager = ConfigManager(config_dir=str(config_dir))
    manager.update_checkpoint("@test", 123, "2024-02-18T10:30:00Z")

    # Reload to verify persistence
    new_manager = ConfigManager(config_dir=str(config_dir))
    config = new_manager.load()

    assert config["checkpoints"]["@test"]["last_message_id"] == 123
    assert config["checkpoints"]["@test"]["last_message_date"] == "2024-02-18T10:30:00Z"


def test_save_with_argument(tmp_path):
    """Test saving configuration by passing a dictionary to save()."""
    config_dir = tmp_path / ".teleshell"
    config_dir.mkdir()
    manager = ConfigManager(config_dir=str(config_dir))
    
    new_data = {"default_channels": ["@passed_arg"]}
    manager.save(new_data)
    
    # Reload to verify
    loaded = manager.load()
    assert loaded["default_channels"] == ["@passed_arg"]
