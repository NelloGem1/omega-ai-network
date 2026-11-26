"""Negotiation intelligence — Phase 1 stub.
Real negotiation barely exists in retail; covers bundle detection
and API-vendor discount requests."""

def find_bundles(offers):
    """Detect vendor bundle deals: same vendor, complementary items."""
    by_vendor = {}
    for o in offers:
        by_vendor.setdefault(o['vendor'], []).append(o)
    bundles = []
    for v, items in by_vendor.items():
        if len(items) > 1:
            total = sum(i['price'] for i in items)
            bundles.append({'vendor': v, 'items': items,
                            'total': total,
                            'note': 'multi-item vendor — check bundle pricing'})
    return bundles

def negotiate(offer):
    """Phase 1: no-op. Phase 3: AP2/ACP protocol calls."""
    return {'offer_id': offer['offer_id'],
            'negotiated_price': offer['price'],
            'method': 'none',
            'note': 'take-it-or-leave-it (Phase 1)'}
