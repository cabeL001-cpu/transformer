import regex as re
from functools import cmp_to_key


def split(data: str, special_tokens: list[str]) -> tuple[list[str], list[str]]:
    # 按特殊token把data切成片段, 返回数据块与数据中的特殊token表
    if not special_tokens:
        return ([data], [])

    tmp = [ re.escape(token) for token in special_tokens]
    reg = '|'.join(tmp)
    return (re.split(reg, data), re.findall(reg, data))

def pretokenizer(PAT: str, data: str, special_tokens: list[str]) -> list[list[str]]:
    # 先处理特殊token，再按PAT 预分词
    chunk_list, _ = split(data, special_tokens) 
    out = []
    for chunk in chunk_list:
        out.append(re.findall(PAT, chunk))

    return out


def tokenizer_train_step(pre_tokens: list[list[str]], vocab: dict[int, bytes], merges: list[tuple[bytes, bytes]]):
    # tokenizer 的一步训练，更新vocab与merges
    words_freq: dict[str, int] = {}
    merge_freq: dict[tuple[bytes, bytes], int] = {}
    for pre_token in pre_tokens:
        for word in pre_token:
            if(word in words_freq):
                words_freq[word] += 1
            else:
                words_freq[word] = 1


    for word, count in words_freq.items():
        tmp_freq = {}
        old = encode(word, vocab, merges)
        for i in range(len(old)-1):
            first = old[i]
            second = old[i+1]
            merge = (vocab[first], vocab[second])
            if(merge in tmp_freq):
                tmp_freq[merge] += 1
            else:
                tmp_freq[merge] = 1

        for merge, times in tmp_freq.items():
            if(merge in merge_freq):
                merge_freq[merge] += times * count
            else:
                merge_freq[merge] = times * count

    
    if not merge_freq:
        return

    max_freq = max(list(merge_freq.values()))
    max_key_lists = [key for key in merge_freq if merge_freq[key] == max_freq]
    max_key = max(max_key_lists)

    vocab[len(vocab)] = max_key[0] + max_key[1]
    merges.append(max_key)




def encode(data: str, vocab: dict[int,bytes], merges: list[tuple[bytes, bytes]]) -> list[int]:

    data_encoded:list[bytes] = [ bytes([i]) for i in list((data.encode("utf-8")))]
    for merge in merges:
        new_data: list[bytes] = []

        i = 0
        while i < len(data_encoded):
            if(i != len(data_encoded) - 1 and (data_encoded[i], data_encoded[i+1]) == merge):
                new_data.append(merge[0] + merge[1])
                i += 2
            else:
                new_data.append(data_encoded[i])
                i += 1
        data_encoded = new_data

    IDs = []
    for string in data_encoded:
        for key in vocab:
            if(vocab[key] == string):
                IDs.append(key)
                break
    return IDs



def tokenizer_encode(PAT: str, data: str, special_tokens: list[str], vocab: dict[int,bytes], merges: list[tuple[bytes, bytes]]) -> list[int]:
    chunks, special_token = split(data, special_tokens)
    special_token_ID = []

    for i in special_token:
        flag = 0
        for key in vocab:
            if(vocab[key] == i.encode('utf-8')):
                special_token_ID.append(key)
                flag = 1
                break
        if(flag != 1):
            print("unkowun token: " + i)
            raise RuntimeError
    IDs = []
    i = 0
    for chunk in chunks:
        for pile in re.findall(PAT, chunk):
            IDs += encode(pile, vocab, merges) 
        if(i < len(special_token)):
            IDs += [special_token_ID[i]]
            i += 1

    return IDs

def tokenizer_decode(IDs: list[int], vocab: dict[int, bytes]) -> str:
    bytes_str: bytes = bytes([])
    for ID in IDs:
        bytes_str += vocab[ID]

    return bytes_str.decode('utf-8')



def tokenizer_train(PAT: str, data: str, special_tokens: list[str], vocab: dict[int, bytes], merges: list[tuple[bytes, bytes]], train_steps: int):
    pre_tokens = pretokenizer(PAT, data, special_tokens)
    for i in range(train_steps):
        tokenizer_train_step(pre_tokens, vocab, merges)



def main():
    
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    data = "yes yes yes |fly fly fly fly fly| fly fly fly fly u i o op oi <eof> ioio <eof>"
    special_tokens = ['|', '<eof>']
    vocab = {i: bytes([i]) for i in range(256)}
    vocab[256] = '<eof>'.encode('utf=8')
    merges = []

    print(vocab)
    print(merges)
    encoded = tokenizer_encode(PAT, data, special_tokens, vocab, merges)
    decoded = tokenizer_decode(encoded, vocab)
    print(encoded)
    print(decoded)
    
    tokenizer_train(PAT, data, special_tokens, vocab, merges, train_steps = 6)

    print(vocab)
    print(merges)
    encoded = tokenizer_encode(PAT, data, special_tokens, vocab, merges)
    decoded = tokenizer_decode(encoded, vocab)
    print(encoded)
    print(decoded)




if __name__ == '__main__':
    main()
