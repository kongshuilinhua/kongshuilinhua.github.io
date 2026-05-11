from math import gcd
def solution(n: int, a: list) -> str:
    mi = float('inf')
    cnt = 0
    for i in range(n):
        if a[i] > mi:
            cnt += 1
        else:
            mi = a[i]
    g = gcd(cnt, n)
    return f'{cnt//g}/{n//g}'

if __name__ == '__main__':
    print(solution(5, [3, 1, 5, 4, 3]) == '3/5')
    print(solution(6, [6, 2, 9, 7, 4, 3]) == '2/3')
    print(solution(4, [8, 5, 6, 3]) == '1/4')