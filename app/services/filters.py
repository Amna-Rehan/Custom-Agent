from urllib.parse import urlparse

BAD_DOMAINS = [

    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",

    "wikipedia.org",

    "indeed.com",
    "glassdoor.com",

    "reddit.com",

    "amazon.com",

    "ebay.com",

    "linkedin.com",

    "medium.com",
    "quora.com",
    "pinterest.com",
    "crunchbase.com/hub",

    # News / media / listicles — not official organization websites
    "arynews.tv",
    "dawn.com",
    "tribune.com.pk",
    "geo.tv",
    "thenews.com.pk",
    "profit.pakistantoday.com.pk",
    "techcrunch.com",
    "forbes.com",
    "bloomberg.com",
    "reuters.com",
    "bbc.com",
    "cnn.com",
    "nytimes.com",
    "theguardian.com",
    "gadinsider.com",
    "reflectpakistan.com",
    "sramanamitra.com",
    "dailypakistan.com.pk",
    "startuppakistan.com.pk",
    "propakistani.pk",
    "pakwired.com",
    "techjuice.pk",
    "news.google.com",
    "yahoo.com",
    "msn.com",
    "businessinsider.com",
    "venturebeat.com",
    "wired.com",
    "substack.com",
]

# Path patterns that usually indicate articles / posts, not org home pages
BAD_PATH_FRAGMENTS = [
    "/posts/",
    "/activity-",
    "/blog/",
    "/news/",
    "/article/",
    "/articles/",
    "/press/",
    "/story/",
    "/stories/",
]

BLOCKED_TEXT_PATTERNS = [
    "checking your browser",
    "attention required",
    "just a moment",
    "cloudflare",
    "captcha",
    "cookie policy",
    "privacy policy",
    "terms of use",
    "404",
    "page not found",
    "403 forbidden",
    "error 403",
    "broker",
    "stock",
    "crypto",
    "forex",
    "posted on linkedin",
    "top 10",
    "top 20",
    "best startups",
    "list of startups",
    "startup directory",
    "complete list",
    "misunderstood",
    "news",
    "eyes",
    "posted",
    "rethinking",
    "directory",
    "unlock your",
    "success stories",
]


def is_blocked_domain(url_or_domain: str) -> bool:
    """Return True when the URL/domain matches a known low-quality or non-org domain."""
    if not url_or_domain:
        return False

    domain = url_or_domain.lower()
    if "://" in url_or_domain:
        domain = urlparse(url_or_domain).netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return any(bad in domain for bad in BAD_DOMAINS)


def is_blocked_path(url_or_path: str) -> bool:
    """Return True when a URL path looks like a blog/article/news page instead of an org site."""
    if not url_or_path:
        return False

    path = url_or_path.lower()
    if "://" in url_or_path:
        path = urlparse(url_or_path).path.lower()

    return any(fragment in path for fragment in BAD_PATH_FRAGMENTS)


def is_blocked_text(text: str, blocked_terms: list[str] | None = None) -> bool:
    """Return True when the text matches low-quality or non-organizational noise."""
    if not text:
        return False

    lowered = text.lower()
    terms = blocked_terms or BLOCKED_TEXT_PATTERNS
    return any(term in lowered for term in terms)


__all__ = [
    "BAD_DOMAINS",
    "BAD_PATH_FRAGMENTS",
    "BLOCKED_TEXT_PATTERNS",
    "is_blocked_domain",
    "is_blocked_path",
    "is_blocked_text",
]
