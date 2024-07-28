from typing import Optional
from uuid import UUID

from core.objects.cache import ObjectCache

from .models import SessionData


class SessionDataCache(ObjectCache[SessionData]):
    _model = SessionData
    _prefix = 'session_data'

    def _fetch_key(
            self,
            data: SessionData
    ) -> str:
        return str(data.session_uuid)

    async def get(self, session_uuid: UUID) -> Optional[SessionData]:
        return await self._get(str(session_uuid))
