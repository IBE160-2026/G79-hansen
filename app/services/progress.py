"""Fixed-action progress transport with bounded, validated public outcomes."""
from pydantic import ValidationError
from app.adapters.documents import DocumentFailure
from app.contracts.progress import ProgressResult


class Progress:
    def __init__(self, documents):
        self.documents = documents

    async def execute(self, identity, submitted, *, write, deadline):
        try:
            result = await self.documents.rpc(identity, 'progress_write' if write else 'progress_read',
                submitted.model_dump(mode='json', by_alias=True), deadline)
            response = ProgressResult.model_validate(result, by_alias=True, by_name=False)
            if response.document_id != submitted.document_id or response.generation_id != submitted.generation_id:
                raise DocumentFailure('progress_pending')
            return response.model_dump(mode='json', by_alias=True)
        except ValidationError:
            raise DocumentFailure('progress_pending') from None
        except DocumentFailure as failure:
            if failure.code not in {'progress_conflict', 'progress_mismatch', 'progress_generation', 'document_unknown'}:
                raise DocumentFailure('progress_pending') from None
            raise
