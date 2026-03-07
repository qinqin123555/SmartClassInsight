import sys
import json
import os

# Usage:
#   python detect_stub.py --image "D:/path/to/image.jpg"
# Output:
#   A plain label string, or a JSON {"label":"xxx"}

def main():
    try:
        args = sys.argv
        if "--image" in args:
            img = args[args.index("--image")+1]
        elif "-i" in args:
            img = args[args.index("-i")+1]
        else:
            print("unknown")
            return 0
        labels = ["举手","阅读","使用手机","写作","走神"]
        idx = abs(hash(os.path.basename(img))) % len(labels)
        # print plain text label
        print(labels[idx])
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
