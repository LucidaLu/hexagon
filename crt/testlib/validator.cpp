#include <bits/stdc++.h>

#include "testlib.h"

using namespace std;

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    int T = inf.readInt(1, (long long)1e6);
    inf.readEoln();
    while (T--) {
        long long A = inf.readLong(0, (long long)1e18);
        inf.readSpace();
        long long B = inf.readLong(0, (long long)1e18);
        inf.readSpace();
        long long C = inf.readLong(0, (long long)1e18);
        inf.readSpace();
        long long M = inf.readLong(0, (long long)1e18);
        inf.readEoln();
        inf.ensure(A < M && B < M && C < M);
    }
    inf.readEof();
    return 0;
}