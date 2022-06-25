from tmt.interface.tui.main import MainApp

def main():
    import argparse
    parser = argparse.ArgumentParser('That Metric Timeline (TMT) terminal user interface (TUI).\nThe goal of this TUI is to provide an easy way for the user to look for experiments and look at some of their details. Operations like looking at the code snapshot backup, loading results and so on are left to the user (the TmtManager helper class is available for some of these operations).')
    parser.add_argument('--config', '-c', help='configuration path. If not given, TUI will try to load from the default configuration path or a default configuration')

    args = parser.parse_args()
    MainApp(args.config).run()


if __name__ == '__main__':
    main()