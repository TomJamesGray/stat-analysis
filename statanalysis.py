import argparse
import sys

if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Stat Analysis")
    # Allow any number of save files to be specified
    parser.add_argument("save_file", nargs="?", default=None, type=str)
    parser.add_argument("--devel", action="store_true")
    results = parser.parse_args()
    # Must parse the results before importing main because otherwise kivy tries to read sys.argv
    # and gets confused by it

    # Remove the options if they've been set from sys.argv to stop kivy reading them
    if results.save_file != None:
        sys.argv.remove(results.save_file)
    if results.devel:
        sys.argv.remove("--devel")

    from stat_analysis import main
    # Run the program
    main.main(results)