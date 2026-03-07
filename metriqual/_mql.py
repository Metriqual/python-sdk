"""Main MQL client — entry point for the Metriqual Python SDK."""

from __future__ import annotations

from typing import Optional

from ._client import HttpClient
from .analytics import AnalyticsAPI
from .audio import AudioAPI
from .chat import ChatAPI
from .embeddings import EmbeddingsAPI
from .experiments import ExperimentsAPI
from .feedback import FeedbackAPI
from .filters import FiltersAPI
from .images import ImagesAPI
from .models import ModelsAPI
from .music import MusicAPI
from .organizations import OrganizationsAPI
from .pricing import PricingAPI
from .prompt_hub import PromptHubAPI
from .proxy_keys import ProxyKeysAPI
from .subscription import SubscriptionAPI
from .video import VideoAPI
from .webhooks import WebhooksAPI


class MQL:
    """Metriqual SDK client.

    Usage::

        from metriqual import MQL

        client = MQL(api_key="mql_...")
        response = client.chat.create(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-4o",
        )
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = "https://api.metriqual.com",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._http = HttpClient(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
            max_retries=max_retries,
        )

        self.chat = ChatAPI(self._http)
        self.proxy_keys = ProxyKeysAPI(self._http)
        self.filters = FiltersAPI(self._http)
        self.organizations = OrganizationsAPI(self._http)
        self.analytics = AnalyticsAPI(self._http)
        self.models = ModelsAPI(self._http)
        self.webhooks = WebhooksAPI(self._http)
        self.pricing = PricingAPI(self._http)
        self.experiments = ExperimentsAPI(self._http)
        self.feedback = FeedbackAPI(self._http)
        self.prompt_hub = PromptHubAPI(self._http)
        self.subscription = SubscriptionAPI(self._http)
        self.audio = AudioAPI(self._http)
        self.images = ImagesAPI(self._http)
        self.video = VideoAPI(self._http)
        self.embeddings = EmbeddingsAPI(self._http)
        self.music = MusicAPI(self._http)

    def with_auth(
        self,
        *,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
    ) -> MQL:
        """Return a new client with different credentials."""
        new = MQL.__new__(MQL)
        new._http = self._http.clone(api_key=api_key, token=token)
        new.chat = ChatAPI(new._http)
        new.proxy_keys = ProxyKeysAPI(new._http)
        new.filters = FiltersAPI(new._http)
        new.organizations = OrganizationsAPI(new._http)
        new.analytics = AnalyticsAPI(new._http)
        new.models = ModelsAPI(new._http)
        new.webhooks = WebhooksAPI(new._http)
        new.pricing = PricingAPI(new._http)
        new.experiments = ExperimentsAPI(new._http)
        new.feedback = FeedbackAPI(new._http)
        new.prompt_hub = PromptHubAPI(new._http)
        new.subscription = SubscriptionAPI(new._http)
        new.audio = AudioAPI(new._http)
        new.images = ImagesAPI(new._http)
        new.video = VideoAPI(new._http)
        new.embeddings = EmbeddingsAPI(new._http)
        new.music = MusicAPI(new._http)
        return new

    def get_base_url(self) -> str:
        return self._http.base_url

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> MQL:
        return self

    def __exit__(self, *args) -> None:
        self.close()
