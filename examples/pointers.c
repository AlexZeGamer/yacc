int increment(int *addr) {
    *addr = *addr + 1;
    return *addr;
}

int main() {
    int slot0;
    int slot1;
    int slot2;
    int *cursor;

    slot0 = 10;
    slot1 = 20;
    slot2 = 30;

    cursor = &slot0;
    debug(*cursor);
    increment(cursor);
    debug(*cursor);

    cursor = &slot2;
    cursor[0] = cursor[0] + 5;
    cursor[-1] = cursor[-1] + 2;

    debug(slot1);
    debug(slot2);

    return 0;
}
