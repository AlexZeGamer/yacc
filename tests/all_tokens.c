// Test source exercising all tokens from src/yacc/token.py
// Includes: constants, identifiers, arithmetic, logical, comparisons,
// parentheses, brackets, braces, assignment, separators, address-of,
// dereference, and all listed keywords (including debug/send/recv).

int arr[3] = {1, 2, 3};
int *ptr = &arr[0];

int add(int a, int b) { return a + b; }

void debug_send_recv_example() {
    int x = 10, y = 20, z = 0; // TOK_INT, TOK_CONST, TOK_COMMA, TOK_AFFECT, TOK_SEMICOLON

    // Arithmetic + assignment + parentheses
    z = x + y - (x * y) / (x % y); // + - * / % ( )

    // Comparisons and logical operators
    if ((x < y) && (y > 0) || !(z == 0)) { // < > && || ! ==
        debug(x); // TOK_DEBUG keyword
        send(x, y); // TOK_SEND keyword and comma
    } else { // TOK_ELSE
        recv(z); // TOK_RECV keyword
    }

    // do-while with continue/break and <= >=
    int i = 0;
    do {
        i = i + 1;
        if (i == 2) { continue; }
        if (i >= 3) { break; }
    } while (i <= 3);

    // for-loop with brackets and braces
    for (int j = 0; j < 3; j = j + 1) {
        z = z + arr[j];
    }

    // Pointer dereference vs multiplication
    *ptr = *ptr + 1; // unary * (deref) and binary * (mul appears above)
}

int main(void) {
    int a = 1, b = 2;
    int c = add(a, b);

    if (a != b) { // !=
        c = c;
    }

    return 0; // TOK_RETURN, TOK_CONST, TOK_SEMICOLON
}
