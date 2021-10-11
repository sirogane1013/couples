import git

from graph import Graph


def leave_one_out(commit: git.Commit, graph: Graph) -> tuple[str, float, float, float, list[dict[str, int]]]:
    """
    Parameters
    ----------
    commit: git.Commit
        Commit Object
    graph: Graph
        Coocc Graph

    Returns
    -------
    hexsha: str
        Commit Hash
    mrr: float
    recall: float
    feedback: float
    details: list[dict[str, int]]
        Detail of each trials
        format:
        {
            target: str -- target name of prediction
            rank: int   -- The rank target appeared
                           If prediction failed, it's value is -1.
        }

    Raises
    -------
    TooSmallCommitException
    """
    hexsha = commit.hexsha
    modified = get_modified(commit)
    if len(modified) <= 1:
        raise TooSmallCommitException("Commit size is too small to leave one out.")
    details = []
    f = 0
    for _ in range(len(modified)):
        modified.append(modified.pop(0))
        target = modified[0]
        query = modified[1:]
        answer = graph.guide(query)
        if len(answer) > 0:
            f += 1
        if target in answer:
            details.append({
                "target": target,
                "rank": answer.index(target) + 1
            })
        else:
            details.append({
                "target": target,
                "rank": -1
            })
    feedback = f / len(modified)
    mrr, recall = calc_metrics(details, feedback)
    return hexsha, mrr, recall, feedback, details


def calc_metrics(details: list[dict[str, int]], feedback: float) -> (float, float):
    m = 0
    r = 0
    for detail in details:
        rank = detail["rank"]
        if rank > 0:
            r += 1
            m += 1 / rank
    mrr = m / (len(details) * feedback)
    recall = r / len(details)
    return mrr, recall


def get_modified(commit: git.Commit) -> list[str]:
    diffs = commit.parents[0].diff(commit)
    return [d.a_path for d in diffs if d.change_type == 'M']


class TooSmallCommitException(Exception):
    pass
