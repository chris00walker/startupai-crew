# Ad Platform Specifications Library

> **Purpose**: Canonical reference for ad creative specifications across platforms.
> **Usage**: Agents MUST consult this library when generating ad creatives.
> **Last Verified**: 2026-01-10

---

## Overview

This library contains authoritative specifications for ad creatives across major advertising platforms. Agents use this as a constraint system to ensure all generated ads are compliant before submission.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AD CREATIVE GENERATION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│  1. P1 receives platform target (e.g., "meta")                      │
│  2. P1 loads specs from this library                                │
│  3. P1 generates copy within character limits                       │
│  4. P1 specifies image requirements per spec                        │
│  5. AssetResolver fetches images matching dimensions                │
│  6. Validator checks all constraints before output                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Supported Platforms:**
- [Meta (Facebook + Instagram)](#meta-facebook--instagram)
- [Google Ads](#google-ads)
- [LinkedIn](#linkedin)
- [TikTok](#tiktok)

---

## Meta (Facebook + Instagram)

### Ad Formats

| Format | Placement | Best For |
|--------|-----------|----------|
| **Single Image** | Feed, Stories, Reels | Simple messaging, product showcase |
| **Carousel** | Feed, Stories | Multiple products, storytelling |
| **Video** | Feed, Stories, Reels | Engagement, demonstrations |
| **Collection** | Feed | E-commerce, catalog browsing |

### Text Specifications

#### Single Image / Video Ads

| Field | Character Limit | Recommendation | Notes |
|-------|----------------|----------------|-------|
| **Primary Text** | 125 chars | 80-100 chars | Truncates after 125 on mobile |
| **Headline** | 40 chars | 25-30 chars | Below image, bold |
| **Description** | 30 chars | 20-25 chars | Below headline, secondary |
| **Link Description** | 30 chars | — | Optional, rarely shown |

#### Carousel Ads

| Field | Character Limit | Notes |
|-------|----------------|-------|
| **Primary Text** | 125 chars | Shared across all cards |
| **Card Headline** | 40 chars | Per card |
| **Card Description** | 20 chars | Per card |
| **Cards** | 2-10 | Minimum 2, maximum 10 |

### Image Specifications

#### Feed Placements

| Aspect Ratio | Dimensions | Use Case |
|--------------|------------|----------|
| **1:1** (Square) | 1080 × 1080 px | Recommended default |
| **4:5** (Portrait) | 1080 × 1350 px | More screen real estate |
| **1.91:1** (Landscape) | 1200 × 628 px | Link ads |

#### Stories / Reels Placements

| Aspect Ratio | Dimensions | Use Case |
|--------------|------------|----------|
| **9:16** (Full Screen) | 1080 × 1920 px | Stories, Reels |

#### Technical Requirements

| Requirement | Specification |
|-------------|---------------|
| **File Types** | JPG, PNG |
| **Max File Size** | 30 MB |
| **Min Resolution** | 600 × 600 px |
| **Text on Image** | < 20% recommended (no longer enforced but affects delivery) |

### Video Specifications

| Requirement | Feed | Stories/Reels |
|-------------|------|---------------|
| **Aspect Ratio** | 1:1, 4:5, 16:9 | 9:16 |
| **Resolution** | 1080 × 1080 min | 1080 × 1920 |
| **Duration** | 1 sec - 241 min | 1-120 sec |
| **File Size** | 4 GB max | 4 GB max |
| **Format** | MP4, MOV | MP4, MOV |
| **Captions** | Recommended | Required (sound-off viewing) |

### Call-to-Action Options

```python
META_CTA_OPTIONS = [
    "Learn More",
    "Shop Now",
    "Sign Up",
    "Subscribe",
    "Get Offer",
    "Get Quote",
    "Contact Us",
    "Download",
    "Apply Now",
    "Book Now",
    "Get Directions",
    "Watch More",
    "Send Message",
    "Request Time",
    "See Menu",
    "Listen Now",
]
```

### Policy Highlights

**Common Rejection Reasons:**
- Before/after images (weight loss, cosmetic)
- Excessive text on images (>20% coverage)
- Misleading claims or clickbait
- Personal attributes ("Are you overweight?")
- Prohibited content (weapons, drugs, adult)
- Non-functional landing page
- Price/availability mismatches

**Safe Zones for Stories/Reels:**
```
┌─────────────────────────────────┐
│  ← 250px safe zone (top)        │
│                                 │
│     SAFE CONTENT AREA           │
│                                 │
│  ← 340px safe zone (bottom)     │
│  [CTA Button / Profile]         │
└─────────────────────────────────┘
```

---

## Google Ads

### Ad Formats

| Format | Network | Best For |
|--------|---------|----------|
| **Responsive Search** | Search | Intent-based queries |
| **Responsive Display** | Display | Awareness, retargeting |
| **Performance Max** | All | Automated optimization |
| **Video (YouTube)** | YouTube | Brand awareness |

### Text Specifications

#### Responsive Search Ads

| Field | Character Limit | Quantity | Notes |
|-------|----------------|----------|-------|
| **Headlines** | 30 chars each | 3-15 | At least 3 required |
| **Descriptions** | 90 chars each | 2-4 | At least 2 required |
| **Display Path** | 15 chars each | 2 | URL path segments |
| **Final URL** | 2048 chars | 1 | Landing page |

**Headline Requirements:**
- First 3 headlines can appear together
- Avoid repetition across headlines
- Include keyword in at least 2 headlines
- Pin important headlines to positions 1-2

#### Responsive Display Ads

| Field | Character Limit | Notes |
|-------|----------------|-------|
| **Short Headline** | 30 chars | Required |
| **Long Headline** | 90 chars | Required |
| **Description** | 90 chars | Required |
| **Business Name** | 25 chars | Required |

### Image Specifications

#### Display Network

| Asset Type | Aspect Ratio | Dimensions | Required |
|------------|--------------|------------|----------|
| **Landscape** | 1.91:1 | 1200 × 628 px | Yes |
| **Square** | 1:1 | 1200 × 1200 px | Yes |
| **Logo (Landscape)** | 4:1 | 512 × 128 px | Recommended |
| **Logo (Square)** | 1:1 | 128 × 128 px | Recommended |

#### Technical Requirements

| Requirement | Specification |
|-------------|---------------|
| **File Types** | JPG, PNG, GIF (static) |
| **Max File Size** | 5.12 MB |
| **Min Resolution** | 600 × 314 px (1.91:1), 300 × 300 px (1:1) |
| **Animation** | Not supported for display images |

### Video Specifications (YouTube)

| Ad Type | Duration | Skippable | Aspect Ratio |
|---------|----------|-----------|--------------|
| **Skippable In-Stream** | 12 sec - 3 min | After 5 sec | 16:9 or 1:1 |
| **Non-Skippable** | 15-20 sec | No | 16:9 |
| **Bumper** | 6 sec max | No | 16:9 |
| **In-Feed** | Any | N/A | 16:9 or 1:1 |

| Requirement | Specification |
|-------------|---------------|
| **Resolution** | 1920 × 1080 (recommended) |
| **File Types** | MP4, AVI, MOV, MPEG |
| **Max File Size** | 256 GB |

### Call-to-Action Options

```python
GOOGLE_CTA_OPTIONS = [
    # Standard
    "Learn more",
    "Get quote",
    "Apply now",
    "Sign up",
    "Contact us",
    "Subscribe",
    "Download",
    "Book now",
    "Shop now",
    # E-commerce
    "Buy now",
    "Add to cart",
    "See offer",
    "View deals",
    # Local
    "Get directions",
    "Call now",
    "Visit site",
]
```

### Policy Highlights

**Common Rejection Reasons:**
- Trademark violations in ad text
- Destination mismatch (ad doesn't match landing page)
- Superlatives without third-party verification ("Best", "#1")
- Misleading content or exaggerated claims
- Capitalization abuse (ALL CAPS)
- Punctuation/symbol abuse (!!!, $$$)
- Unavailable products/services

**Editorial Requirements:**
- Correct grammar and spelling
- No gimmicky capitalization
- Standard punctuation only
- No phone numbers in headlines (use call extensions)

---

## LinkedIn

### Ad Formats

| Format | Best For |
|--------|----------|
| **Single Image** | Brand awareness, lead gen |
| **Carousel** | Multiple offerings, storytelling |
| **Video** | Thought leadership, product demos |
| **Message Ads** | Direct outreach (InMail) |
| **Text Ads** | Simple awareness, low budget |
| **Document Ads** | Thought leadership, whitepapers |

### Text Specifications

#### Sponsored Content (Single Image)

| Field | Character Limit | Recommendation |
|-------|----------------|----------------|
| **Intro Text** | 600 chars | 150 chars (before "see more") |
| **Headline** | 200 chars | 70 chars |
| **Description** | 300 chars | Rarely shown |

#### Sponsored Content (Carousel)

| Field | Character Limit | Notes |
|-------|----------------|-------|
| **Intro Text** | 255 chars | Shared across cards |
| **Card Headline** | 45 chars | Per card |
| **Cards** | 2-10 | Each with own image + headline |

#### Message Ads (InMail)

| Field | Character Limit |
|-------|----------------|
| **Subject Line** | 60 chars |
| **Message Body** | 1,500 chars |
| **CTA Button** | 20 chars |
| **Custom Footer** | 2,500 chars |

#### Text Ads

| Field | Character Limit |
|-------|----------------|
| **Headline** | 25 chars |
| **Description** | 75 chars |

### Image Specifications

#### Sponsored Content

| Asset Type | Aspect Ratio | Dimensions |
|------------|--------------|------------|
| **Single Image** | 1.91:1 | 1200 × 627 px |
| **Square Option** | 1:1 | 1200 × 1200 px |
| **Carousel Card** | 1:1 | 1080 × 1080 px |

#### Technical Requirements

| Requirement | Specification |
|-------------|---------------|
| **File Types** | JPG, PNG, GIF (static) |
| **Max File Size** | 5 MB |
| **Min Resolution** | 400 px wide |

### Video Specifications

| Requirement | Specification |
|-------------|---------------|
| **Aspect Ratio** | 16:9, 1:1, 9:16 |
| **Resolution** | 360p - 1080p |
| **Duration** | 3 sec - 30 min (15-30 sec recommended) |
| **File Size** | 75 KB - 200 MB |
| **Format** | MP4 |
| **Captions** | SRT file supported |

### Call-to-Action Options

```python
LINKEDIN_CTA_OPTIONS = [
    "Apply",
    "Download",
    "Get Quote",
    "Learn More",
    "Sign Up",
    "Subscribe",
    "Register",
    "Join",
    "Attend",
    "Request Demo",
]
```

### Policy Highlights

**Common Rejection Reasons:**
- Unprofessional language or imagery
- Misleading job postings
- Third-party data usage claims
- Personal data collection without consent
- Competitor disparagement
- Unverified credentials or certifications

**Best Practices:**
- Professional tone (B2B audience)
- Industry-specific language acceptable
- Thought leadership positioning
- Clear value proposition for professionals

---

## TikTok

### Ad Formats

| Format | Placement | Best For |
|--------|-----------|----------|
| **In-Feed Ads** | For You feed | Awareness, engagement |
| **TopView** | First ad on open | Maximum reach |
| **Branded Hashtag** | Discover page | UGC campaigns |
| **Branded Effects** | Creation tools | Interactive engagement |
| **Spark Ads** | Boosted organic | Authentic content |

### Text Specifications

#### In-Feed Ads

| Field | Character Limit | Notes |
|-------|----------------|-------|
| **Ad Text** | 100 chars | First 2 lines visible without tap |
| **CTA Text** | 16 chars | Button text |
| **Display Name** | 40 chars | Brand/app name |

#### TopView Ads

| Field | Character Limit |
|-------|----------------|
| **Ad Text** | 100 chars |
| **CTA Text** | 16 chars |

### Image Specifications

TikTok is **video-first**, but static images are supported for some placements:

| Asset Type | Aspect Ratio | Dimensions |
|------------|--------------|------------|
| **Profile Image** | 1:1 | 200 × 200 px |
| **Static Image (limited)** | 9:16 | 720 × 1280 px |

### Video Specifications (Primary Format)

| Requirement | Specification |
|-------------|---------------|
| **Aspect Ratio** | 9:16 (vertical), 1:1, 16:9 |
| **Resolution** | 720 × 1280 px minimum (1080 × 1920 recommended) |
| **Duration** | 5-60 sec (9-15 sec recommended) |
| **File Size** | 500 MB max |
| **Format** | MP4, MOV, MPEG, AVI |
| **Bitrate** | 516 kbps+ |

**Safe Zones:**
```
┌─────────────────────────────────┐
│  ← 44px safe zone (top)         │
│                                 │
│     SAFE CONTENT AREA           │
│     (main message here)         │
│                                 │
│  ← 140px safe zone (bottom)     │
│  [Username / CTA / Sound]       │
│  ← 64px safe zone (right)       │
└─────────────────────────────────┘
```

### Call-to-Action Options

```python
TIKTOK_CTA_OPTIONS = [
    "Shop Now",
    "Learn More",
    "Sign Up",
    "Download",
    "Contact Us",
    "Apply Now",
    "Book Now",
    "Subscribe",
    "Get Quote",
    "Order Now",
    "Play Game",
    "Install Now",
    "Watch Now",
    "Listen Now",
]
```

### Policy Highlights

**Common Rejection Reasons:**
- Static or low-quality video
- Overly polished/corporate content (doesn't fit platform)
- Misleading claims or fake urgency
- Prohibited products (weapons, tobacco, adult content)
- Copyright music without license
- Before/after transformations

**Platform-Specific Best Practices:**
- Native, authentic content (not TV-style ads)
- Sound-on design (music, voiceover)
- Hook in first 3 seconds
- Trending sounds/formats when appropriate
- UGC-style often outperforms polished content

---

## Cross-Platform Comparison

### Text Limits Quick Reference

| Platform | Headline | Primary Text | Description | CTA |
|----------|----------|--------------|-------------|-----|
| **Meta** | 40 | 125 | 30 | 20 |
| **Google Search** | 30 × 3-15 | — | 90 × 2-4 | — |
| **Google Display** | 30 + 90 | — | 90 | — |
| **LinkedIn** | 200 | 600 | 300 | 20 |
| **TikTok** | — | 100 | — | 16 |

### Image Dimensions Quick Reference

| Platform | Feed | Stories/Vertical | Square |
|----------|------|------------------|--------|
| **Meta** | 1200 × 628 | 1080 × 1920 | 1080 × 1080 |
| **Google** | 1200 × 628 | — | 1200 × 1200 |
| **LinkedIn** | 1200 × 627 | — | 1200 × 1200 |
| **TikTok** | — | 1080 × 1920 | 1080 × 1080 |

### Platform Selection Guide

| Goal | Recommended Platform | Why |
|------|---------------------|-----|
| **B2B Lead Gen** | LinkedIn | Professional targeting |
| **E-commerce** | Meta, Google Shopping | Purchase intent |
| **App Install** | TikTok, Meta | Engagement, younger demo |
| **Brand Awareness** | Meta, TikTok | Reach, engagement |
| **Search Intent** | Google Search | High intent queries |
| **Retargeting** | Google Display, Meta | Pixel-based audiences |

---

## Programmatic Access

### Python Constants

```python
"""
Ad Platform Specifications Library
Load these constants in AdCreativeGeneratorTool
"""

# Character limits by platform and field
CHAR_LIMITS = {
    "meta": {
        "headline": 40,
        "primary_text": 125,
        "description": 30,
        "cta": 20,
    },
    "google_search": {
        "headline": 30,
        "headline_count": (3, 15),
        "description": 90,
        "description_count": (2, 4),
        "display_path": 15,
    },
    "google_display": {
        "short_headline": 30,
        "long_headline": 90,
        "description": 90,
        "business_name": 25,
    },
    "linkedin": {
        "headline": 200,
        "headline_recommended": 70,
        "intro_text": 600,
        "intro_recommended": 150,
        "description": 300,
        "cta": 20,
    },
    "tiktok": {
        "ad_text": 100,
        "cta": 16,
        "display_name": 40,
    },
}

# Image specifications by platform
IMAGE_SPECS = {
    "meta": {
        "feed": {"ratio": "1.91:1", "size": (1200, 628), "formats": ["jpg", "png"]},
        "square": {"ratio": "1:1", "size": (1080, 1080), "formats": ["jpg", "png"]},
        "stories": {"ratio": "9:16", "size": (1080, 1920), "formats": ["jpg", "png"]},
        "max_file_size_mb": 30,
    },
    "google": {
        "landscape": {"ratio": "1.91:1", "size": (1200, 628), "formats": ["jpg", "png"]},
        "square": {"ratio": "1:1", "size": (1200, 1200), "formats": ["jpg", "png"]},
        "max_file_size_mb": 5.12,
    },
    "linkedin": {
        "landscape": {"ratio": "1.91:1", "size": (1200, 627), "formats": ["jpg", "png"]},
        "square": {"ratio": "1:1", "size": (1200, 1200), "formats": ["jpg", "png"]},
        "max_file_size_mb": 5,
    },
    "tiktok": {
        "vertical": {"ratio": "9:16", "size": (1080, 1920), "formats": ["jpg", "png"]},
        "square": {"ratio": "1:1", "size": (1080, 1080), "formats": ["jpg", "png"]},
        "max_file_size_mb": 500,  # For video
    },
}

# CTA options by platform
CTA_OPTIONS = {
    "meta": [
        "Learn More", "Shop Now", "Sign Up", "Subscribe", "Get Offer",
        "Get Quote", "Contact Us", "Download", "Apply Now", "Book Now",
    ],
    "google": [
        "Learn more", "Get quote", "Apply now", "Sign up", "Contact us",
        "Subscribe", "Download", "Book now", "Shop now", "Buy now",
    ],
    "linkedin": [
        "Apply", "Download", "Get Quote", "Learn More", "Sign Up",
        "Subscribe", "Register", "Join", "Request Demo",
    ],
    "tiktok": [
        "Shop Now", "Learn More", "Sign Up", "Download", "Contact Us",
        "Apply Now", "Book Now", "Subscribe", "Order Now",
    ],
}
```

### Validation Function

```python
def validate_ad_creative(
    platform: str,
    headline: str,
    primary_text: str,
    description: str = None,
    cta: str = None,
) -> dict:
    """
    Validate ad creative against platform specifications.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "char_counts": dict
        }
    """
    limits = CHAR_LIMITS.get(platform)
    if not limits:
        return {"valid": False, "errors": [f"Unknown platform: {platform}"]}

    errors = []
    warnings = []
    counts = {}

    # Check headline
    if "headline" in limits:
        counts["headline"] = len(headline)
        if len(headline) > limits["headline"]:
            errors.append(
                f"Headline exceeds {limits['headline']} chars "
                f"({len(headline)} chars)"
            )

    # Check primary text
    if "primary_text" in limits:
        counts["primary_text"] = len(primary_text)
        if len(primary_text) > limits["primary_text"]:
            errors.append(
                f"Primary text exceeds {limits['primary_text']} chars "
                f"({len(primary_text)} chars)"
            )

    # Check CTA
    if cta and "cta" in limits:
        counts["cta"] = len(cta)
        if len(cta) > limits["cta"]:
            errors.append(f"CTA exceeds {limits['cta']} chars ({len(cta)} chars)")

        # Check if CTA is in allowed list
        platform_ctas = CTA_OPTIONS.get(platform, [])
        if cta not in platform_ctas:
            warnings.append(
                f"CTA '{cta}' not in standard options. "
                f"Allowed: {', '.join(platform_ctas[:5])}..."
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "char_counts": counts,
    }
```

---

## Change Log

| Date | Change | Source |
|------|--------|--------|
| 2026-01-10 | Initial creation with Meta, Google, LinkedIn, TikTok specs | Platform documentation |

---

## References

- [Meta Ads Guide](https://www.facebook.com/business/ads-guide)
- [Google Ads Specifications](https://support.google.com/google-ads/answer/1722124)
- [LinkedIn Ad Specifications](https://www.linkedin.com/help/lms/answer/a425102)
- [TikTok Ad Specifications](https://ads.tiktok.com/help/article/ad-specifications)
