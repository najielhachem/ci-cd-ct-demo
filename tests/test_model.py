from ci_cd_ct_demo import model


def test_predict_returns_a_label_on_each_side_of_the_threshold():
    assert model.predict(1.5, 0.0) == 0
    assert model.predict(1.5, 3.0) == 1


def test_fit_can_overfit_a_few_samples():
    rows = [(0.0, 0), (1.0, 0), (3.0, 1), (4.0, 1)]
    assert model.accuracy(model.fit(rows), rows) == 1.0
