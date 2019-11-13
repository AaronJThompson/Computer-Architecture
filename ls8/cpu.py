"""CPU functionality."""

import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf3
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
        
        ALU_OPS = {
            0b0010: "MUL"
        }
        running = True

        def LDI(cpu):
            register = cpu.ram_read(cpu.pc + 1)
            if not cpu.__verify_reg__(register):
                print(f"Invalid register {register}")
                return False
            register = register >> 0 & 0b111
            cpu.reg[register] = cpu.ram_read(cpu.pc + 2)

        def PRN(cpu):
            register = cpu.ram_read(cpu.pc + 1)
            if not cpu.__verify_reg__(register):
                print(f"Invalid register {register}")
                return False
            register = register >> 0 & 0b111
            print(cpu.reg[register])

        def PUSH(cpu):
            register = cpu.ram_read(cpu.pc + 1)
            if not cpu.__verify_reg__(register):
                print(f"Invalid register {register}")
                return False
            register = register >> 0 & 0b111
            cpu.reg[7] -= 1
            MAR = cpu.reg[7]
            MDR = cpu.reg[register]
            cpu.ram_write(MAR, MDR)
        
        def POP(cpu):
            register = cpu.ram_read(cpu.pc + 1)
            if not cpu.__verify_reg__(register):
                print(f"Invalid register {register}")
                return False
            register = register >> 0 & 0b111
            MAR = cpu.reg[7]
            MDR = cpu.ram_read(MAR)
            cpu.reg[register] = MDR
            cpu.reg[7] += 1

        def HLT(cpu):
            return False

        def OPCODE_to_operation(opcode):
            nonlocal self
            operations = {
                0b0010: LDI,
                0b0111: PRN,
                0b0101: PUSH,
                0b0110: POP,
                0b0001: HLT
            }
            # Get the function from switcher dictionary
            if opcode not in operations:
                print(f"Invalid instruction {opcode}")
                return False
            func = operations[opcode]
            ret = func()
            if ret is None:
                return True
            else:
                return ret

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

            self.pc += 1 + OPERANDS