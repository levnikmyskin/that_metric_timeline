from tmt import TmtManager
import pickle


if __name__ == '__main__':
    # The recommended way to look and search for experiments is 
    # to use the binary tool provided with the library `tmt_tui`.
    # Let's say we know there is an experiment with id "example"


    # If you don't have a custom configuration file, then use
    manager = TmtManager()

    # otherwise, use 
    manager = TmtManager(config='example_config.json')

    # An Entry is a row in the database, i.e. an experiment that was tracked.
    manager.set_entry_by_id('example')  # This will fail in this case since there is no such entry in the database
    
    # load the results and unpickle them
    for name, path in manager.results_paths():
        with open(path, 'rb') as f:
            # do stuff with your results. If it's a pickle it's more convenient to use the code block below this one
            res = pickle.load(f)
    
    # load the unpickled results
    for name, res in manager.load_results():
        # do something with your results.
        # if res is a numpy array...
        print(res.mean())
    
    for name, val in manager.get_metrics():
        print(f"{name}: {val}")

    # If you need to do other stuff, like searching for 
    # experiments between two datetimes and so on
    # you can access the `db` member like
    manager.db.get_entries_greater_than_date(date_or_timestamp)
