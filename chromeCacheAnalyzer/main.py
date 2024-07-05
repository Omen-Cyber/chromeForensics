import utils chromeCacheExtractor

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(f"USAGE: {pathlib.Path(sys.argv[0]).name} <cache input dir> <out dir>")
        exit(1)
    main(sys.argv[1:])