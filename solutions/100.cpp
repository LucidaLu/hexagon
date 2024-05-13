#include <bits/stdc++.h>

long long Mul(long long a, long long b, const long long M) {
  long long r = 0;
  for (; b; b >>= 1, (a <<= 1) %= M)
    if (b & 1)
      (r += a) %= M;
  return r;
}

int main() {
  std::ios::sync_with_stdio(0);
  std::cin.tie(0);
  std::cout.tie(0);
  int T;
  std::cin >> T;
  while (T--) {
    long long A, B, C, M, X, p;
    std::cin >> A >> B >> C >> M;
    X = M / std::gcd((long long)((C - Mul(A, B, M) % M + M) % M), M);
    for (int i = 64; i >= 2; --i) {
      p = pow(X, 1.0 / i) + 0.5;
      if ((long long)(pow(p, i) + 0.5) == X)
        break;
      else
        p = -1;
    }
    if (p == -1)
      p = X;
    long long ans = 1;
    for (; M % p == 0; ans *= p, M /= p)
      ;
    std::cout << ans << '\n';
  }
  return 0;
}