from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.metrics import f1_score, accuracy_score
from tmt import tmt_recorder, tmt_save

"""
This example uses scikit-learn, but tmt does not really care what you do in your function. If you want to save metrics, the only required thing is to return a dictionary.
"""


@tmt_recorder('logistic_example')
def run_experiments():
    x, y = make_classification()
    lr = LogisticRegression()
    lr.fit(x, y)
    preds = lr.predict(x)
    return {'f1': f1_score(y, preds), 'accuracy': accuracy_score(y, preds)}


@tmt_recorder('logistic_example_save_results')
def run_experiments_with_results():
    x, y = make_classification()
    lr = LogisticRegression()
    lr.fit(x, y)
    preds = lr.predict(x)
    tmt_save(preds, 'predictions')
    return {'f1': f1_score(y, preds), 'accuracy': accuracy_score(y, preds)}


# For this to work, our current working directory must be the "examples" directory
@tmt_recorder('with_custom_config', config_path='example_config.json')
def with_custom_config():
    x, y = make_classification()
    lr = LogisticRegression()
    lr.fit(x, y)
    preds = lr.predict(x)
    return {'f1': f1_score(y, preds), 'accuracy': accuracy_score(y, preds)}


if __name__ == '__main__':
    run_experiments()
    run_experiments_with_results()
    with_custom_config()