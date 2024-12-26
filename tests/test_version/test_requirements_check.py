import pytest

if __name__ == "__main__":
    pytest.main([__file__])


@pytest.mark.parametrize(
    "pkg_name,installed_ver,check_ver,result",
    [
        pytest.param("ruff", "0.8.8", "==0.8.0", False, id="ruff =="),
        pytest.param("requests", "1.1.3", "==1.1.3", True, id="requests =="),
        pytest.param("requests", "1.1.3", ">=1.1.3", True, id="requests >="),
        pytest.param("requests", "1.1.3", "<=1.1.3", True, id="requests <="),
        pytest.param("requests", "1.1.3", ">1.1.3", False, id="requests >"),
        pytest.param("requests", "1.1.3", "<1.1.3", False, id="requests <"),
        pytest.param("ruff", "0.8.8", "==*", True, id="ruff == *"),
        pytest.param("ruff", "0.8.8", "~=0.8.7", True, id="ruff ~= True"),
        pytest.param("ruff", "0.9.0", "~=1.0.0", False, id="ruff ~= False"),
        pytest.param("ruff", "1.0", "~=1.0", True, id="ruff 1.0 ~= 1.0"),
        pytest.param("ruff", "0.99", "~=1.0", False, id="ruff 0.99 ~= 1.0"),
        pytest.param("ruff", "0.99", "^1.0", False, id="ruff 0.99 ^ 1.0"),
        pytest.param("ruff", "1.98", "^1.99", False, id="ruff 1.98 ^ 1.99"),
        pytest.param("requests", "1.2.3", "^1.2.4", False, id="requests 1.2.3 ^1.2.4"),
        pytest.param("requests", "1.2.4", "^1.2.4", True, id="requests 1.2.4 ^1.2.4"),
        pytest.param("requests", "1.2.9", "^1.2.4", True, id="requests 1.2.9 ^1.2.4"),
        pytest.param("requests", "1.3.0", "^1.2.4", True, id="requests 1.3.0 ^1.2.4"),
    ],
)
def test_check_requirements(
    pkg_name: str, installed_ver: str, check_ver: str, result: bool, mocker
):
    # The packages being tested do not need to be installed for this test.
    def get_version(package_name):
        return installed_ver

    mock_config = mocker.patch("oxt.___lo_pip___.install.requirements_check.Config")
    mock_config.Config = mocker.Mock()
    # mock_config.Config.requirements = {"ruff": ">=0.8.1"}

    mock_logger = mocker.patch("oxt.___lo_pip___.install.requirements_check.OxtLogger")
    # mock_logger.OxtLogger = dummy_logger

    # mock the importlib.metadata.version function
    mock_version = mocker.patch("oxt.___lo_pip___.install.requirements_check.version")
    # assign the get_version function to the mock_version function
    mock_version.side_effect = get_version

    from oxt.___lo_pip___.install.requirements_check import RequirementsCheck

    rc = RequirementsCheck()
    rc._config.requirements = {pkg_name: check_ver}
    test_result = rc.check_requirements()
    assert test_result == result
