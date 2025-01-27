"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

    def load(self, file_name):
        """Load a program into memory."""

        address = 0
        examples_dir = os.path.join(os.path.dirname(__file__), "examples/")
        file_path = os.path.join(examples_dir, file_name)

        program = list()
        try:
            with open(file_path) as f:
                for line in f:
                    comment_split = line.split("#")

                    num = comment_split[0].strip()

                    if len(num) == 0:
                        continue

                    value = int(num, 2)

                    program.append(value)

        except FileNotFoundError:
            print(f"{file_name} not found")
            sys.exit(2)
            
        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, mar):
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    def __verify_reg__(self, register):
        if (register >> 3 & 0b11111) != 0:
            return False
        return True

    def run(self):
        """Run the CPU."""
        LDI = 0b0010
        PRN = 0b0111
        HLT = 0b0001
        
        ALU_OPS = {
            0b0010: "MUL"
        }
        running = True

        while running:
            IR = self.ram_read(self.pc)
            OPERANDS = IR >> 6 & 0b11
            ALU = IR >> 5 & 1
            OPCODE = IR >> 0 & 0b1111
            
            if ALU == 1:
                register1 = self.ram_read(self.pc + 1)
                register2 = self.ram_read(self.pc + 2)
                if not (self.__verify_reg__(register1) and self.__verify_reg__(register2)):
                    print(f"Invalid registers")
                    running = False
                    break
                self.alu(ALU_OPS[OPCODE], register1, register2)
            elif OPCODE == LDI:
                register = self.ram_read(self.pc + 1)
                if not self.__verify_reg__(register):
                    print(f"Invalid register {register}")
                    running = False
                    break
                register = register >> 0 & 0b111
                self.reg[register] = self.ram_read(self.pc + 2)
            elif OPCODE == PRN:
                register = self.ram_read(self.pc + 1)
                if not self.__verify_reg__(register):
                    print(f"Invalid register {register}")
                    running = False
                    break
                register = register >> 0 & 0b111
                print(self.reg[register])
            elif OPCODE == HLT:
                running = False
                break
            else:
                print(f"Invalid instruction {OPCODE}")
                running = False
                break

            self.pc += 1 + OPERANDS