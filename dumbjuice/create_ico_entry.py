import argparse
from dumbjuice.utils import create_ico  # same helper function as before

def main():
    parser = argparse.ArgumentParser(description='Convert PNG to multi-size ICO file.')
    parser.add_argument('png_path', help='Path to input PNG')
    parser.add_argument('--output', '-o', help='Output .ico file (optional)')

    args = parser.parse_args()
    output = args.output or args.png_path.rsplit('.', 1)[0] + '.ico'
    create_ico(args.png_path, output)

if __name__ == '__main__':
    main() 