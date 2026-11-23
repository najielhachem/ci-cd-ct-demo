from ci_cd_ct_demo import registry


def test_an_alias_points_to_a_registered_version():
    reg = {"versions": {}, "aliases": {}}
    version = registry.register(reg, 1.5, trained_on="train.csv")
    registry.set_alias(reg, "champion", version)
    assert registry.get_by_alias(reg, "champion") == (version, reg["versions"]["1"])


def test_a_missing_alias_returns_none():
    assert registry.get_by_alias({"versions": {}, "aliases": {}}, "champion") is None
