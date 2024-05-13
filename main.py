from src.sheet import Sheet
from src.file import File
import os


def main():
    # print('Generating Images in "output"')
    # f = File()
    # f.init()
    # f.parser.extract_from_pptx()
    # f.parser.extract_from_pdf()
    # if len(os.listdir(f"{os.getcwd()}/input")) == 0:
    #     return
    # f.main()

    print("Uploading...")
    s = Sheet()
    s.main()


if __name__ == "__main__":
    main()
