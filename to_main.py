from main import main
import os

def to_main():
    input_file = "sanple.png"
    with open(input_file, mode="rb") as f:
        bin = f.read()
        
    main(bin)

if __name__ == "__main__":
    to_main()