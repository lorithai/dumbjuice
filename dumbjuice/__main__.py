import sys
from .build import build
import os

def main():

    target_folder = os.getcwd()

    if len(sys.argv) > 1: 
        if sys.argv[1] == "build":
            if len(sys.argv) > 2:
                target_folder = sys.argv[2]

        else:
            target_folder = sys.argv[1]
    
    build(target_folder)
if __name__ == "__main__":
    main()