"""M1 spike: a migration that always fails, to prove failed deploys roll back (docs/13 M1)."""


def execute():
	raise Exception("CentralBench M1 spike: forced migration failure")
