CASE1 = {"words": ["abcd", "bcda", "ada"]}
CASE1_ANSWER = [-1, 1, 0]

CASE2 = {"words": ["ABC"]}
CASE2_ANSWER = [0]

CASE3 = {"words": ["eaaaabaa", "eaaaacaa", "daaaaaaa", "eaaaadaa", "daaaafaa"]}
CASE3_ANSWER = [1, 1, 1, -1, 1]

CASE4 = {"words": ["aaa"] * 100000}
CASE4_ANSWER = [0] * 100000

alphabet = "abcdefghijklmnopqrstuvwxyz"


def int_to_word(i):
    x = []
    for _ in range(3):
        x.append(alphabet[i % len(alphabet)])
        i //= len(alphabet)
    return "".join(x)


num_strs = list(map(int_to_word, range(10000)))
CASE5 = {"words": [num_strs[i] + num_strs[i + 1] for i in range(len(num_strs) - 1)]}
CASE5_ANSWER = [(len(CASE5["words"]) - i) % 2 * 2 - 1 for i in range(len(CASE5["words"]))]
CASE_LIST = [
    [CASE1, CASE1_ANSWER],
    [CASE2, CASE2_ANSWER],
    [CASE3, CASE3_ANSWER],
    [CASE4, CASE4_ANSWER],
    [CASE5, CASE5_ANSWER],
]
