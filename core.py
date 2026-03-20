from dataclasses import dataclass

@dataclass
class Bucket_Range:
    low: int
    high: int
    max_count: int

    def __str__(self):
        return f"{self.low}-{self.high}"

def get_bucket_from_diff(diff: int | None, bucket_ranges: list[Bucket_Range]) -> Bucket_Range | None:
    if diff is None: return None
    for b in bucket_ranges:
        if b.low <= diff and diff < b.high:
            return b
    return None
