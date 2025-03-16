A key philosophy when applying these modifiers is to ensure they serve to expand the rating scale rather than artificially inflate or deflate it. Since the base scale only consists of three levels, these modifiers help differentiate values more precisely by extending or compressing the range for certain attributes.

For example, ADCs typically have the highest damage among all classes. However, a maximum score of 3 does not fully capture this distinction, which is why their Damage rating is multiplied by 1.3. Conversely, ADCs are usually very fragile, with a base Toughness of 1. In reality, their actual durability should be even lower, so applying a coefficient of less than 1 helps emphasize their squishiness—since this is a defining trait of their class.

However, not all ratings should be adjusted. Some attributes, even if not a key strength or weakness of a class, are already balanced within that class's rating system. For example, a Vanguard’s Utility is typically measured relative to the role’s overall function. If a champion like Taric has high Utility, this is already factored into his kit and does not need further modification just because high Utility is rare for his class.

Similarly, distinctions between subclasses should be preserved. For instance, Juggernauts and Divers both fall under the Fighter category, but their defining difference is Mobility. Therefore, we should avoid applying extreme modifiers to Mobility, as their base rating within the Fighter class already accounts for this difference. Another example is Artillery Mages—nearly all of them have a Toughness rating of 1, but adding a penalty further distinguishes the "different levels of 1" within their class compared to others.
Scale Conversion

The client rates champions on a 1-3 scale, where both "None" and "Low" in a particular attribute are treated equally. In contrast, the Wikia uses a 0-3 scale, which, based on visual inspection, appears to function as a 0-5 scale for Toughness, Control, Mobility, and Utility. This roughly translates as follows:
Client Scale

1 → Low
2 → Moderate
3 → High
Wiki Scale Approximation

-2 / -1 / 0 → Equivalent to 1 in the client scale (Low)
2 / 3 → Equivalent to 2 (Moderate)
4 / 5 → Equivalent to 3 (High)

For example, a champion listed on the Wikia as having a 0 or -1 in an attribute would be classified as a 1 in the client scale (and our dataset). However, we can refine this further by adjusting role-based weights. A champion with a -1 rating could receive a penalty modifier to reflect their position at the lower end of the 1 spectrum, while those rated 4-5 could receive a bonus modifier to emphasize their position at the top of the scale. The highest values (5) would be subject to the greatest modifier.