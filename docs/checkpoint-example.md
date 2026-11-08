# A checkpoint before and after continuation

This fictional example shows what survives the switch. It is not a benchmark or evidence that a vendor model ran these exact steps.

## Before: save partial work

The outgoing agent has saved:

```python
def greet(name):
    return "Hello " + name
```

The user wants a blank name to become "world". The [before checkpoint](examples/before.md) records the current implementation, that missing behavior, the agreed trimming decision, the scope, and the next action. It does not label unfinished checks as passed.

## Resume: inspect before implementing

The successor reads the checkpoint and actual source. If they agree, it continues with the missing fallback. If the source already has the fallback, it validates the existing work and corrects the checkpoint instead of implementing it again. Either way, the files must be inspected; the checkpoint is a route to evidence.

## After: leave evidence and a clear stopping point

The resulting function in this example is:

```python
def greet(name):
    return "Hello " + (name.strip() or "world")
```

The [after checkpoint](examples/after.md) records completion of the named task, the illustrative checks, remaining coverage limits, and no active writer. It retains the decision and does not invent the next task.

| Information | Before | After |
| --- | --- | --- |
| Task identity and scope | GREET-1; greeting.py | Same task and scope |
| Reusable work | Named greeting | Preserved |
| Missing behavior | Blank fallback | Implemented |
| Checks | Named case only; blank not run | Agreed string cases checked in the scenario |
| Handoff | Partial task, ready | Completed task, ready |
| Next action | Add missing fallback | Await next goal |

These documents use the same default format as the real template. The after checkpoint shows the optional `updated_at` line; the before checkpoint omits it, as v0.1.x checkpoints do. Both are valid. They are outside the installed skill so normal resume does not load demonstration material.
