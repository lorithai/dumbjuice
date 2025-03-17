import sys
from .build import build

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        build()
    else:
        print("Usage: dumbjuice build")

if __name__ == "__main__":
    main()