from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class MCPSettings(BaseSettings):
    transport: str = Field("HTTP", alias="MCP_TRANSPORT")
    weather_endpoint: Optional[str] = Field("http://localhost:8765", alias="MCP_WEATHER_ENDPOINT")

    # Defaults adaptados a Docker; en local puedes sobreescribir con .env
    destination_url: Optional[str] = Field("http://destinations:8773", alias="MCP_DESTINATION_URL")
    flight_url: Optional[str] = Field("http://flights:8771", alias="MCP_FLIGHT_URL")
    hotel_url: Optional[str] = Field("http://hotels:8772", alias="MCP_HOTEL_URL")

    timeout_seconds: int = Field(10, alias="MCP_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(extra="ignore")


class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    transcribe_local: Optional[bool] = Field(False, alias="TRANSCRIBE_LOCAL")
    use_openai_whisper: Optional[bool] = Field(True, alias="USE_OPENAI_WHISPER")
    mcp: MCPSettings = MCPSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Compatibilidad con código anterior
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self.openai_api_key


settings = Settings()
