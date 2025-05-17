import pytest

from scrapy.http import Request, Response
from scrapy.pipelines.files import FileException, FilesPipeline
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler


class TestFilesPipeline201:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.spider = Spider("test_spider")
        self.crawler = get_crawler(Spider)
        self.pipeline = FilesPipeline.from_crawler(self.crawler)
        self.pipeline._download_request = (
            self.mock_download_request
        )  # Mock the _download_request method

    def mock_download_request(self, request, info, *, item=None):
        # Mock successful download
        return {
            "url": request.url,
            "path": "some/path",
            "checksum": "some_checksum",
            "status": "downloaded",
        }

    @pytest.mark.asyncio
    async def test_201_with_location(self):
        request = Request("http://example.com/file1")
        response = Response(
            "http://example.com/file1",
            status=201,
            headers={b"Location": b"http://example.com/file2"},
            request=request,
        )

        result = await self.pipeline.media_downloaded(
            response=response,
            request=request,
            info=self.pipeline.SpiderInfo(self.spider),
        )

        assert result is not None
        assert result["url"] == "http://example.com/file2"
        assert result["status"] == "downloaded"

    @pytest.mark.asyncio
    async def test_201_without_location(self):
        request = Request("http://example.com/file")
        response = Response(
            "http://example.com/file",
            status=201,
            request=request,
        )

        with pytest.raises(FileException, match="missing-location-header"):
            await self.pipeline.media_downloaded(
                response=response,
                request=request,
                info=self.pipeline.SpiderInfo(self.spider),
            )
