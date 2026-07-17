# experiments

Use this directory for micro-experiments: the smallest disposable program that
answers one technical uncertainty without copying the production project.

Every experiment records:

- question;
- decision the result will change;
- smallest revealing program or command;
- environment and relevant versions;
- observed output;
- interpretation and remaining uncertainty;
- production consequence;
- created and observed timestamps with time zones;
- disposition: delete or archive.

Optimize for fast learning and visible mechanism, not production architecture.
The experiment does not become a partial product, shadow implementation, or
source of copied production code.

Experimental code does not graduate. The finding graduates. Implement the
learned behavior deliberately in a production worktree with the real ownership,
style, tests, and review requirements.

When the question requires the real repository, build, integration boundary, or
performance profile, use a disposable integration-spike worktree under
`../worktrees/spikes/` instead.
