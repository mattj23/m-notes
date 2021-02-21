from mnotes.fix.common import CreationFixer
from tests.test_fixes import transact_fixture, local_tz


def test_simple_transaction_build(transact_fixture):
    provider, index_builder, master = transact_fixture
    fixer = CreationFixer(l)


def test_transaction_build_errors_on_conflict(transact_fixture):
    assert False


def test_hetrogenous_transaction(transact_fixture):
    assert False