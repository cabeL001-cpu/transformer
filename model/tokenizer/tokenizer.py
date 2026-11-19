import regex as re
from pathlib import Path

# pre-tokenizer pattern
PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""



class Mytokenizer():


    def __init__(self, dataset_path: Path, merge_rules: dict[int, bytes], max_vocab_size: int, special_tokens: list[str]) -> None:
        self.dataset_path = dataset_path
        self.merge_rules = merge_rules
        self.max_vovab_size = max_vocab_size
        self.spectial_tokens = spectial_tokens

    def __pretokenizer(self, PAT: str) -> list[str]:
        pass
    def train_tokenizer(self, save_path: Path) -> tuple[dict[int, bytes], list[tuple[bytes, bytes]]]:
        pass
    def encode(self, text: str) -> list[int]:
        pass
    def decode(self, list[int]) -> str:
        pass

















