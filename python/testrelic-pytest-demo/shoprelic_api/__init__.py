"""ShopRelic API — the FastAPI backend exercised by the testrelic-pytest demo.

This is the API-tier analog of the JS ShopRelic storefront demo. It is driven by
chaos flags (env vars) so the seed script can manufacture a realistic
regression -> recovery story across HTTP/GraphQL protocols.
"""

__all__ = ["__version__"]
__version__ = "1.0.0"
