#include <cassert>
struct Wallet {
    int balance; int cap = 20;
    bool spend(int amount) {
        if (amount <= 0 || amount > balance) return false;
        balance -= amount; return true;
    }
    bool earn(int amount) {
        if (amount <= 0 || amount > cap - balance) return false;
        balance += amount; return true;
    }
};
int main() {
    Wallet w{10};
    assert(!w.spend(11) && w.balance==10);
    assert(w.spend(6) && w.balance==4);
    assert(!w.earn(19) && w.balance==4);
    assert(w.earn(3) && w.balance==7);
}
