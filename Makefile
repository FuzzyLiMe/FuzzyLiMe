# Makefile for FuzzyLiMe
# Builds vulnerable/vuln (native) and Windows PE executables via mingw-w64

CC := gcc
CFLAGS := -Wall -Wextra -Wformat-security -O2
LDFLAGS :=

SRCDIR := vulnerable
BINDIR := vulnerable
TARGET := $(BINDIR)/vuln
SRC := $(SRCDIR)/vuln.c

# Cross-compilers for producing Windows PE executables from WSL or Linux
CROSS_64 := x86_64-w64-mingw32-gcc
CROSS_32 := i686-w64-mingw32-gcc
WINOUT := $(BINDIR)/vuln.exe

.PHONY: all clean run valgrind help win64 win32

all: $(TARGET)

$(TARGET): $(SRC)
	@echo "Compiling $< -> $@"
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

run: $(TARGET)
	@echo "Running $(TARGET) with example args..."
	@$(TARGET) aa "%c%c"

valgrind: CFLAGS += -g
valgrind: all
	@echo "Run under Valgrind: valgrind --leak-check=full $(TARGET) aa \"%c%c\""

# Build a 64-bit Windows executable using mingw-w64 cross-compiler
win64: $(WINOUT)

$(WINOUT): $(SRC)
	@echo "Compiling (win64) $< -> $@"
	$(CROSS_64) $(CFLAGS) $(LDFLAGS) -o $@ $<

# Build a 32-bit Windows executable using mingw-w64 cross-compiler
win32: $(BINDIR)/vuln32.exe

$(BINDIR)/vuln32.exe: $(SRC)
	@echo "Compiling (win32) $< -> $@"
	$(CROSS_32) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	@echo "Cleaning binaries"
	@-rm -f $(TARGET) $(WINOUT) $(BINDIR)/vuln32.exe

help:
	@echo "Makefile targets:"
	@echo "  make        build native $(TARGET) (default)"
	@echo "  make run    build and run with example args" 
	@echo "  make win64  build a Windows x86_64 PE executable (vuln.exe) using x86_64-w64-mingw32-gcc" 
	@echo "  make win32  build a Windows i686 PE executable (vuln32.exe) using i686-w64-mingw32-gcc" 
	@echo "  make clean  remove built binaries"
