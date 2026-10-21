import time

from tripwire_pattern import Assessment, PendingActionManager, PolicyEngine, Tripwire


class Always:
    def assess(self, *a): return Assessment(0.97, 0.0, 1.0)


def test_policy_blocks_prod_mutation_for_operator_but_not_admin():
    e = PolicyEngine(caller_role="operator")
    assert not e.evaluate("stop_instance", {"instance_id": "web-prod-1"}, "Stop web-prod-1").passed
    assert PolicyEngine(caller_role="admin").evaluate("stop_instance", {"instance_id": "web-prod-1"}, "Stop web-prod-1").passed
    assert PolicyEngine(allow_prod_mutations=True).evaluate("stop_instance", {"instance_id": "web-prod-1"}, "x").passed


def test_policy_environment_confusion_and_viewer():
    r = PolicyEngine(allow_prod_mutations=True).evaluate("start_instance", {"instance_id": "web-prod-1"}, "Start the server in staging")
    assert not r.passed and "environment confusion" in r.violations[0]
    assert not PolicyEngine(caller_role="viewer").evaluate("start_instance", {"instance_id": "web-1"}, "Start web-1").passed
    assert PolicyEngine().evaluate("list_instances", {"env": "prod"}, "List prod").passed


def test_policy_only_tightens_a_decider_allow():
    tw = Tripwire(Always(), policy=PolicyEngine())
    v = tw.evaluate("Stop web-prod-1", "", "stop_instance", {"instance_id": "web-prod-1"})
    assert v.action == "block" and v.policy_violations
    assert Tripwire(Always(), policy=PolicyEngine()).evaluate(
        "Stop web-1", "", "stop_instance", {"instance_id": "web-1"}).action == "allow"


def test_pending_tokens_single_use_bound_and_expiring():
    m = PendingActionManager(ttl_seconds=0.05)
    p = m.create("stop_instance", {"instance_id": "web-1"}, "Which instance?")
    assert not m.verify_and_consume(p.token, "stop_instance", {"instance_id": "web-2"})   # bound to args
    assert m.verify_and_consume(p.token, "stop_instance", {"instance_id": "web-1"})
    assert not m.verify_and_consume(p.token, "stop_instance", {"instance_id": "web-1"})   # replay
    q = m.create("stop_instance", {"instance_id": "web-1"}, "?")
    time.sleep(0.08)
    assert not m.verify_and_consume(q.token, "stop_instance", {"instance_id": "web-1"})   # expired
