[🇫🇷 Consulter la version française](./README-fr.md)

# MSM - Mini Stack Machine

A simulator for a minimal stack machine with a simple instruction set.

Takes as input a text file containing the assembly code to execute (or via standard input) and displays the result on the console.

## Attribution
This simulator was created by [Thomas LAVERGNE](https://perso.limsi.fr/lavergne/).

Original download link: [https://perso.limsi.fr/lavergne/app4-compil/msm.tgz](https://perso.limsi.fr/lavergne/app4-compil/msm.tgz)

## Compilation
To compile the MSM program, you can use either `make` or a C compiler like `gcc`.

**Using Make:** Run the following command in the terminal:
```bash
make msm
```

**Using GCC:** If `make` is not available, you can compile the program manually with:
```bash
gcc -o msm msm.c
```

## Execution

To execute the MSM program, you can use the following command in the terminal:
```bash
./msm <assembly_file_name>
```
or via standard input:
```bash
cat <assembly_file_name> | ./msm
```

**Note:** The program must include a `.start` label to indicate the entry point for execution.

### Debugging Mode
You can enable debugging mode using the `-d` flag. This will print detailed information about the program's execution, including the current instruction and stack state. Use `-d` multiple times for more verbosity.

Example:
```bash
./msm -d <assembly_file_name>
```

### Memory Size
The default memory size is 64 KB. You can increase it to 16 MB using the `-m` flag.

Example:
```bash
./msm -m <assembly_file_name>
```

### Error Handling
The MSM simulator provides detailed error messages for issues such as:
- Undefined labels.
- Invalid instructions.
- Incorrect argument counts.
- Memory allocation failures.

## Instruction Set

### Program Control

#### halt
Terminates the program execution.

### Stack Manipulation

#### drop [int]
Removes the top n elements from the stack.

#### dup
Pushes a copy of the top element of the stack.

#### swap
Swaps the two top elements of the stack.

#### push [int]
Pushes an integer constant onto the top of the stack.

#### get [int]
Pushes a copy of the N-th value from the base of the stack onto the top of the stack.

#### set [int]
Pops the top value from the stack and assigns it to the N-th value from the base of the stack.

### Memory Access

#### read
Pops a memory address, then pushes the content of the memory cell at that address onto the stack.

#### write
Pops a value and then an address. Assigns the value to the memory cell at the given address.

### Arithmetic and Logic

#### add / sub / mul / div / mod
Pops two values from the top of the stack, applies the corresponding operation, and pushes the result.  
Note: To perform the operation A-B, for example, the value A must be pushed first, followed by the value B.

#### not
Logical negation of the top of the stack. Pops a value, then pushes 0 if the value is non-zero and 1 otherwise.

#### and / or
Performs the logical operation between the two top values of the stack.

### Comparisons

#### cmpeq / cmpne / cmplt / cmle / cmpgt / cmpge
Pops two values from the top of the stack and pushes the result of their comparison:  
- `cmpeq` -> A == B  
- `cmpne` -> A != B  
- `cmplt` -> A < B  
- `cmple` -> A <= B  
- `cmpgt` -> A > B  
- `cmpge` -> A >= B  

### Branching

#### jump [label]
Unconditional jump to the specified address.

#### jumpt / jumpf [label]
Conditional jump. Pops an integer value from the top of the stack. If it is non-zero (resp. zero), jumps to the specified address; otherwise, continues execution at the next instruction.

### Function Calls

#### prep [label]
Prepares a call to the function [label]. Reserves two slots at the top of the stack.

#### call [int]
Performs the call to the function prepared by a `prep` instruction, with [int] arguments pushed onto the stack.

#### ret
Returns from a function, pushing the top value of the stack as the return value. Restores the stack to the state it was in at the corresponding `prep` instruction and pushes the result value.

#### resn [int]
Reserves [int] slots on the stack, typically for local variables.

### Communication

#### send
Pops the top value from the stack and sends it to the console as a byte interpreted as a character.

#### recv
Pushes an integer onto the stack corresponding to the next byte read from the console.

#### dbg
Pops the top value from the stack and prints it as an integer to the console.
