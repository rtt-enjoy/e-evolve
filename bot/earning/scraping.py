"""Readable text from a web page -- the one place this project parses HTML.

A support module, not a product: it has no ``run`` and writes no status.

Why it exists: a feed gives the writer a title and, for most sources, almost
nothing else. A live pull found 29 of 40 candidates with under 300 characters of
summary (Hacker News 0, Lobsters 8), and the draft prompt then tells the model
to "rely on the title". A model asked to write an expert article from a headline
invents the detail, which is what the ``fabricated`` gate exists to catch. The
fix is to give it the source's own text, and that needs a real HTML parser.

The old extractor was three regexes. ``<article>...</article>`` matched lazily,
so a page with a nested or repeated ``<article>`` stopped at the first closing
tag; an unclosed ``<p>`` and a ``<style>`` body both leaked into the prose. This
parses the page with Scrapling (lxml underneath) and reads the paragraphs of the
densest content container, skipping anything inside navigation or page chrome.

Rules:

- **Never raises.** Every failure returns ``""``; the caller keeps the feed
  summary it already had. Reading a page is an enhancement to a draft.
- **Scrapling is imported lazily and is optional.** If the import or the parse
  fails, the regex extractor that was here before answers instead, so a missing
  wheel degrades quality and never the cycle.
- **Parser only.** The ``scrapling[fetchers]`` extra is deliberately not used:
  its browser engines need ``scrapling install`` on the runner, which means
  editing the heartbeat workflow. HTTP stays with ``requests``.
- **No LLM call.** Extraction is deterministic.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from ._shared import strip_html

log = logging.getLogger(__name__)

# Page chrome. A paragraph inside any of these is not the article.
_CHROME = ("nav", "header", "footer", "aside", "form", "noscript", "script", "style",
		   "svg", "iframe", "button", "select", "dialog", "template")

# Where an article body usually lives, most specific first. Several can match one
# page (a blog index is a stack of <article>), so the densest one wins.
_CONTAINERS = (
	"article, main, [role=main], .post-content, .entry-content, .article-body, "
	".post-body, .markdown-body, .prose, #content, #main"
)

# Blocks that carry prose. Containers that already hold their own text (a list
# item, a quote) are read whole, so the paragraph inside them is skipped rather
# than emitted twice.
_BLOCKS = (
	"p[not(ancestor::li or ancestor::blockquote)]",
	"h1", "h2", "h3", "h4", "h5", "h6",
	"li[not(.//li)]",
	"blockquote[not(.//blockquote)]",
	"pre",
)

# A list item or paragraph that is mostly link text is a menu or a "related
# posts" list, not prose.
_LINK_SHARE = 0.6
# Short list items are overwhelmingly navigation. Paragraphs are not filtered by
# length: "Note: this is breaking." is a real sentence.
_MIN_LIST_ITEM = 40
_MAX_CODE_BLOCK = 600
# Below this much prose a container is not an article, so look at the whole body.
_MIN_CONTAINER_CHARS = 200

# One XPath for every prose block that is not inside page chrome. A predicate
# cannot sit on a union, so each branch carries its own.
_NOT_CHROME = "[not(" + " or ".join(f"ancestor::{tag}" for tag in _CHROME) + ")]"
_BLOCK_XPATH = " | ".join(f".//{block}{_NOT_CHROME}" for block in _BLOCKS)


def extract_text(html: str, max_chars: int = 6000) -> str:
	"""Readable prose from ``html``, paragraphs separated by a blank line.

	Returns ``""`` when nothing readable is found. Falls back to a regex
	extractor when Scrapling is unavailable or fails.
	"""
	if not isinstance(html, str) or not html.strip():
		return ""
	try:
		text = _scrapling_extract(html)
	except Exception as exc:
		log.info("[scraping] scrapling extraction failed (%s); using regex fallback", exc)
		text = ""
	if not text:
		text = _regex_extract(html)
	return _clip(text, max_chars)


def _scrapling_extract(html: str) -> str:
	from scrapling.parser import Selector  # lazy: optional dependency

	page = Selector(html)
	container = _densest_container(page)
	blocks = _blocks(container if container is not None else page)
	seen: set[str] = set()
	out: list[str] = []
	for tag, text in blocks:
		if text in seen:
			continue
		seen.add(text)
		out.append(text)
	return "\n\n".join(out).strip()


def _prose_length(node: Any) -> int:
	return sum(len(text) for _, text in _blocks(node))


def _densest_container(page: Any) -> Any:
	best, best_len = None, 0
	for node in page.css(_CONTAINERS):
		length = _prose_length(node)
		if length > best_len:
			best, best_len = node, length
	if best is not None and best_len >= _MIN_CONTAINER_CHARS:
		return best
	return None


def _blocks(node: Any) -> list[tuple[str, str]]:
	"""(tag, text) for every prose block under ``node``, in document order."""
	out: list[tuple[str, str]] = []
	for el in node.xpath(_BLOCK_XPATH):
		tag = str(el.tag)
		if tag == "pre":
			text = str(el.get_all_text(separator="", strip=False)).strip("\n")
			text = text[:_MAX_CODE_BLOCK]
		else:
			text = re.sub(r"\s+", " ", str(el.get_all_text(separator=" ", strip=True))).strip()
		if not text:
			continue
		if tag in ("p", "li") and _mostly_links(el, text):
			continue
		if tag == "li" and len(text) < _MIN_LIST_ITEM:
			continue
		out.append((tag, text))
	return out


def _mostly_links(el: Any, text: str) -> bool:
	linked = sum(len(str(a.get_all_text(separator=" ", strip=True))) for a in el.css("a"))
	return bool(text) and linked / len(text) > _LINK_SHARE


def _regex_extract(html: str) -> str:
	"""The extractor used before Scrapling. Kept as the no-dependency fallback."""
	for tag in ("script", "style", "nav", "header", "footer", "aside", "noscript"):
		html = re.sub(rf"<{tag}\b.*?</{tag}>", " ", html, flags=re.DOTALL | re.IGNORECASE)
	body = re.search(r"<(?:article|main)\b.*?>(.*?)</(?:article|main)>",
					 html, flags=re.DOTALL | re.IGNORECASE)
	if body:
		html = body.group(1)
	# A sentinel survives strip_html's whitespace collapsing; a raw \n would not.
	html = re.sub(r"</(p|h[1-6]|li|pre|blockquote)>", " ¶ ", html, flags=re.IGNORECASE)
	text = strip_html(html)
	text = re.sub(r"(\s*¶\s*)+", "\n\n", text)
	return text.strip()


def _clip(text: str, max_chars: int) -> str:
	"""Cut at a paragraph boundary when one is close, so no sentence is chopped."""
	if max_chars <= 0 or len(text) <= max_chars:
		return text
	cut = text[:max_chars]
	boundary = cut.rfind("\n\n")
	if boundary >= max_chars * 0.6:
		cut = cut[:boundary]
	return cut.rstrip()
